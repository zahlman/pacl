"""Selector eventloop for Unix with signal handling."""

import errno
import fcntl
import os
import signal
import socket
import stat
import subprocess
import sys
import threading


from . import base_subprocess
from . import constants
from . import events
from . import protocols
from . import selector_events
from . import tasks
from . import transports
from .log import logger


__all__ = ['SelectorEventLoop', 'STDIN', 'STDOUT', 'STDERR',
           'AbstractChildWatcher', 'SafeChildWatcher',
           'FastChildWatcher', 'DefaultEventLoopPolicy',
           ]

STDIN = 0
STDOUT = 1
STDERR = 2


if sys.platform == 'win32':  # pragma: no cover
    raise ImportError('Signals are not really supported on Windows')


class _UnixSelectorEventLoop(selector_events.BaseSelectorEventLoop):
    """Unix event loop

    Adds signal handling to SelectorEventLoop
    """

    def __init__(self, selector=None):
        super().__init__(selector)
        self._signal_handlers = {}

    def _socketpair(self):
        return socket.socketpair()

    def close(self):
        for sig in list(self._signal_handlers):
            self.remove_signal_handler(sig)
        super().close()

    def add_signal_handler(self, sig, callback, *args):
        """Add a handler for a signal.  UNIX only.

        Raise ValueError if the signal number is invalid or uncatchable.
        Raise RuntimeError if there is a problem setting up the handler.
        """
        self._check_signal(sig)
        try:
            # set_wakeup_fd() raises ValueError if this is not the
            # main thread.  By calling it early we ensure that an
            # event loop running in another thread cannot add a signal
            # handler.
            signal.set_wakeup_fd(self._csock.fileno())
        except ValueError as exc:
            raise RuntimeError(str(exc))

        handle = events.make_handle(callback, args)
        self._signal_handlers[sig] = handle

        try:
            signal.signal(sig, self._handle_signal)
        except OSError as exc:
            del self._signal_handlers[sig]
            if not self._signal_handlers:
                try:
                    signal.set_wakeup_fd(-1)
                except ValueError as nexc:
                    logger.info('set_wakeup_fd(-1) failed: %s', nexc)

            if exc.errno == errno.EINVAL:
                raise RuntimeError('sig {} cannot be caught'.format(sig))
            else:
                raise

    def _handle_signal(self, sig, arg):
        """Internal helper that is the actual signal handler."""
        handle = self._signal_handlers.get(sig)
        if handle is None:
            return  # Assume it's some race condition.
        if handle._cancelled:
            self.remove_signal_handler(sig)  # Remove it properly.
        else:
            self._add_callback_signalsafe(handle)

    def remove_signal_handler(self, sig):
        """Remove a handler for a signal.  UNIX only.

        Return True if a signal handler was removed, False if not.
        """
        self._check_signal(sig)
        try:
            del self._signal_handlers[sig]
        except KeyError:
            return False

        if sig == signal.SIGINT:
            handler = signal.default_int_handler
        else:
            handler = signal.SIG_DFL

        try:
            signal.signal(sig, handler)
        except OSError as exc:
            if exc.errno == errno.EINVAL:
                raise RuntimeError('sig {} cannot be caught'.format(sig))
            else:
                raise

        if not self._signal_handlers:
            try:
                signal.set_wakeup_fd(-1)
            except ValueError as exc:
                logger.info('set_wakeup_fd(-1) failed: %s', exc)

        return True

    def _check_signal(self, sig):
        """Internal helper to validate a signal.

        Raise ValueError if the signal number is invalid or uncatchable.
        Raise RuntimeError if there is a problem setting up the handler.
        """
        if not isinstance(sig, int):
            raise TypeError('sig must be an int, not {!r}'.format(sig))

        if not (1 <= sig < signal.NSIG):
            raise ValueError(
                'sig {} out of range(1, {})'.format(sig, signal.NSIG))

    def _make_read_pipe_transport(self, pipe, protocol, waiter=None,
                                  extra=None):
        return _UnixReadPipeTransport(self, pipe, protocol, waiter, extra)

    def _make_write_pipe_transport(self, pipe, protocol, waiter=None,
                                   extra=None):
        return _UnixWritePipeTransport(self, pipe, protocol, waiter, extra)

    @tasks.coroutine
    def _make_subprocess_transport(self, protocol, args, shell,
                                   stdin, stdout, stderr, bufsize,
                                   extra=None, **kwargs):
        with events.get_child_watcher() as watcher:
            transp = _UnixSubprocessTransport(self, protocol, args, shell,
                                              stdin, stdout, stderr, bufsize,
                                              extra=None, **kwargs)
            watcher.add_child_handler(transp.get_pid(),
                                      self._child_watcher_callback, transp)
        yield from transp._post_init()
        return transp

    def _child_watcher_callback(self, pid, returncode, transp):
        self.call_soon_threadsafe(transp._process_exited, returncode)

    def _subprocess_closed(self, transp):
        pass


def _set_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)


class _UnixReadPipeTransport(transports.ReadTransport):

    max_size = 256 * 1024  # max bytes we read in one eventloop iteration

    def __init__(self, loop, pipe, protocol, waiter=None, extra=None):
        super().__init__(extra)
        self._extra['pipe'] = pipe
        self._loop = loop
        self._pipe = pipe
        self._fileno = pipe.fileno()
        mode = os.fstat(self._fileno).st_mode
        if not (stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode)):
            raise ValueError("Pipe transport is for pipes/sockets only.")
        _set_nonblocking(self._fileno)
        self._protocol = protocol
        self._closing = False
        self._loop.add_reader(self._fileno, self._read_ready)
        self._loop.call_soon(self._protocol.connection_made, self)
        if waiter is not None:
            self._loop.call_soon(waiter.set_result, None)

    def _read_ready(self):
        try:
            data = os.read(self._fileno, self.max_size)
        except (BlockingIOError, InterruptedError):
            pass
        except OSError as exc:
            self._fatal_error(exc)
        else:
            if data:
                self._protocol.data_received(data)
            else:
                self._closing = True
                self._loop.remove_reader(self._fileno)
                self._loop.call_soon(self._protocol.eof_received)
                self._loop.call_soon(self._call_connection_lost, None)

    def pause_reading(self):
        self._loop.remove_reader(self._fileno)

    def resume_reading(self):
        self._loop.add_reader(self._fileno, self._read_ready)

    def close(self):
        if not self._closing:
            self._close(None)

    def _fatal_error(self, exc):
        # should be called by exception handler only
        logger.exception('Fatal error for %s', self)
        self._close(exc)

    def _close(self, exc):
        self._closing = True
        self._loop.remove_reader(self._fileno)
        self._loop.call_soon(self._call_connection_lost, exc)

    def _call_connection_lost(self, exc):
        try:
            self._protocol.connection_lost(exc)
        finally:
            self._pipe.close()
            self._pipe = None
            self._protocol = None
            self._loop = None


class _UnixWritePipeTransport(transports.WriteTransport):

    def __init__(self, loop, pipe, protocol, waiter=None, extra=None):
        super().__init__(extra)
        self._extra['pipe'] = pipe
        self._loop = loop
        self._pipe = pipe
        self._fileno = pipe.fileno()
        mode = os.fstat(self._fileno).st_mode
        is_socket = stat.S_ISSOCK(mode)
        is_pipe = stat.S_ISFIFO(mode)
        if not (is_socket or is_pipe):
            raise ValueError("Pipe transport is for pipes/sockets only.")
        _set_nonblocking(self._fileno)
        self._protocol = protocol
        self._buffer = []
        self._conn_lost = 0
        self._closing = False  # Set when close() or write_eof() called.

        # On AIX, the reader trick only works for sockets.
        # On other platforms it works for pipes and sockets.
        # (Exception: OS X 10.4?  Issue #19294.)
        if is_socket or not sys.platform.startswith("aix"):
            self._loop.add_reader(self._fileno, self._read_ready)

        self._loop.call_soon(self._protocol.connection_made, self)
        if waiter is not None:
            self._loop.call_soon(waiter.set_result, None)

    def _read_ready(self):
        # Pipe was closed by peer.
        self._close()

    def write(self, data):
        assert isinstance(data, bytes), repr(data)
        if not data:
            return

        if self._conn_lost or self._closing:
            if self._conn_lost >= constants.LOG_THRESHOLD_FOR_CONNLOST_WRITES:
                logger.warning('pipe closed by peer or '
                               'os.write(pipe, data) raised exception.')
            self._conn_lost += 1
            return

        if not self._buffer:
            # Attempt to send it right away first.
            try:
                n = os.write(self._fileno, data)
            except (BlockingIOError, InterruptedError):
                n = 0
            except Exception as exc:
                self._conn_lost += 1
                self._fatal_error(exc)
                return
            if n == len(data):
                return
            elif n > 0:
                data = data[n:]
            self._loop.add_writer(self._fileno, self._write_ready)

        self._buffer.append(data)

    def _write_ready(self):
        data = b''.join(self._buffer)
        assert data, 'Data should not be empty'

        self._buffer.clear()
        try:
            n = os.write(self._fileno, data)
        except (BlockingIOError, InterruptedError):
            self._buffer.append(data)
        except Exception as exc:
            self._conn_lost += 1
            # Remove writer here, _fatal_error() doesn't it
            # because _buffer is empty.
            self._loop.remove_writer(self._fileno)
            self._fatal_error(exc)
        else:
            if n == len(data):
                self._loop.remove_writer(self._fileno)
                if self._closing:
                    self._loop.remove_reader(self._fileno)
                    self._call_connection_lost(None)
                return
            elif n > 0:
                data = data[n:]

            self._buffer.append(data)  # Try again later.

    def can_write_eof(self):
        return True

    # TODO: Make the relationships between write_eof(), close(),
    # abort(), _fatal_error() and _close() more straightforward.

    def write_eof(self):
        if self._closing:
            return
        assert self._pipe
        self._closing = True
        if not self._buffer:
            self._loop.remove_reader(self._fileno)
            self._loop.call_soon(self._call_connection_lost, None)

    def close(self):
        if not self._closing:
            # write_eof is all what we needed to close the write pipe
            self.write_eof()

    def abort(self):
        self._close(None)

    def _fatal_error(self, exc):
        # should be called by exception handler only
        logger.exception('Fatal error for %s', self)
        self._close(exc)

    def _close(self, exc=None):
        self._closing = True
        if self._buffer:
            self._loop.remove_writer(self._fileno)
        self._buffer.clear()
        self._loop.remove_reader(self._fileno)
        self._loop.call_soon(self._call_connection_lost, exc)

    def _call_connection_lost(self, exc):
        try:
            self._protocol.connection_lost(exc)
        finally:
            self._pipe.close()
            self._pipe = None
            self._protocol = None
            self._loop = None


class _UnixSubprocessTransport(base_subprocess.BaseSubprocessTransport):

    def _start(self, args, shell, stdin, stdout, stderr, bufsize, **kwargs):
        stdin_w = None
        if stdin == subprocess.PIPE:
            # Use a socket pair for stdin, since not all platforms
            # support selecting read events on the write end of a
            # socket (which we use in order to detect closing of the
            # other end).  Notably this is needed on AIX, and works
            # just fine on other platforms.
            stdin, stdin_w = self._loop._socketpair()
        self._proc = subprocess.Popen(
            args, shell=shell, stdin=stdin, stdout=stdout, stderr=stderr,
            universal_newlines=False, bufsize=bufsize, **kwargs)
        if stdin_w is not None:
            stdin.close()
            self._proc.stdin = open(stdin_w.detach(), 'rb', buffering=bufsize)


class AbstractChildWatcher:
    """Abstract base class for monitoring child processes.

    Objects derived from this class monitor a collection of subprocesses and
    report their termination or interruption by a signal.

    New callbacks are registered with .add_child_handler(). Starting a new
    process must be done within a 'with' block to allow the watcher to suspend
    its activity until the new process if fully registered (this is needed to
    prevent a race condition in some implementations).

    Example:
        with watcher:
            proc = subprocess.Popen("sleep 1")
            watcher.add_child_handler(proc.pid, callback)

    Notes:
        Implementations of this class must be thread-safe.

        Since child watcher objects may catch the SIGCHLD signal and call
        waitpid(-1), there should be only one active object per process.
    """

    def add_child_handler(self, pid, callback, *args):
        """Register a new child handler.

        Arrange for callback(pid, returncode, *args) to be called when
        process 'pid' terminates. Specifying another callback for the same
        process replaces the previous handler.

        Note: callback() must be thread-safe
        """
        raise NotImplementedError()

    def remove_child_handler(self, pid):
        """Removes the handler for process 'pid'.

        The function returns True if the handler was successfully removed,
        False if there was nothing to remove."""

        raise NotImplementedError()

    def set_loop(self, loop):
        """Reattach the watcher to another event loop.

        Note: loop may be None
        """
        raise NotImplementedError()

    def close(self):
        """Close the watcher.

        This must be called to make sure that any underlying resource is freed.
        """
        raise NotImplementedError()

    def __enter__(self):
        """Enter the watcher's context and allow starting new processes

        This function must return self"""
        raise NotImplementedError()

    def __exit__(self, a, b, c):
        """Exit the watcher's context"""
        raise NotImplementedError()


class BaseChildWatcher(AbstractChildWatcher):

    def __init__(self, loop):
        self._loop = None
        self._callbacks = {}

        self.set_loop(loop)

    def close(self):
        self.set_loop(None)
        self._callbacks.clear()

    def _do_waitpid(self, expected_pid):
        raise NotImplementedError()

    def _do_waitpid_all(self):
        raise NotImplementedError()

    def set_loop(self, loop):
        assert loop is None or isinstance(loop, events.AbstractEventLoop)

        if self._loop is not None:
            self._loop.remove_signal_handler(signal.SIGCHLD)

        self._loop = loop
        if loop is not None:
            loop.add_signal_handler(signal.SIGCHLD, self._sig_chld)

            # Prevent a race condition in case a child terminated
            # during the switch.
            self._do_waitpid_all()

    def remove_child_handler(self, pid):
        try:
            del self._callbacks[pid]
            return True
        except KeyError:
            return False

    def _sig_chld(self):
        try:
            self._do_waitpid_all()
        except Exception:
            logger.exception('Unknown exception in SIGCHLD handler')

    def _compute_returncode(self, status):
        if os.WIFSIGNALED(status):
            # The child process died because of a signal.
            return -os.WTERMSIG(status)
        elif os.WIFEXITED(status):
            # The child process exited (e.g sys.exit()).
            return os.WEXITSTATUS(status)
        else:
            # The child exited, but we don't understand its status.
            # This shouldn't happen, but if it does, let's just
            # return that status; perhaps that helps debug it.
            return status


class SafeChildWatcher(BaseChildWatcher):
    """'Safe' child watcher implementation.

    This implementation avoids disrupting other code spawning processes by
    polling explicitly each process in the SIGCHLD handler instead of calling
    os.waitpid(-1).

    This is a safe solution but it has a significant overhead when handling a
    big number of children (O(n) each time SIGCHLD is raised)
    """

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        pass

    def add_child_handler(self, pid, callback, *args):
        self._callbacks[pid] = callback, args

        # Prevent a race condition in case the child is already terminated.
        self._do_waitpid(pid)

    def _do_waitpid_all(self):

        for pid in list(self._callbacks):
            self._do_waitpid(pid)

    def _do_waitpid(self, expected_pid):
        assert expected_pid > 0

        try:
            pid, status = os.waitpid(expected_pid, os.WNOHANG)
        except ChildProcessError:
            # The child process is already reaped
            # (may happen if waitpid() is called elsewhere).
            pid = expected_pid
            returncode = 255
            logger.warning(
                "Unknown child process pid %d, will report returncode 255",
                pid)
        else:
            if pid == 0:
                # The child process is still alive.
                return

            returncode = self._compute_returncode(status)

        try:
            callback, args = self._callbacks.pop(pid)
        except KeyError:  # pragma: no cover
            # May happen if .remove_child_handler() is called
            # after os.waitpid() returns.
            pass
        else:
            callback(pid, returncode, *args)


class FastChildWatcher(BaseChildWatcher):
    """'Fast' child watcher implementation.

    This implementation reaps every terminated processes by calling
    os.waitpid(-1) directly, possibly breaking other code spawning processes
    and waiting for their termination.

    There is no noticeable overhead when handling a big number of children
    (O(1) each time a child terminates).
    """
    def __init__(self, loop):
        super().__init__(loop)

        self._lock = threading.Lock()
        self._zombies = {}
        self._forks = 0

    def close(self):
        super().close()
        self._zombies.clear()

    def __enter__(self):
        with self._lock:
            self._forks += 1

            return self

    def __exit__(self, a, b, c):
        with self._lock:
            self._forks -= 1

            if self._forks or not self._zombies:
                return

            collateral_victims = str(self._zombies)
            self._zombies.clear()

        logger.warning(
            "Caught subprocesses termination from unknown pids: %s",
            collateral_victims)

    def add_child_handler(self, pid, callback, *args):
        assert self._forks, "Must use the context manager"

        self._callbacks[pid] = callback, args

        try:
            # Ensure that the child is not already terminated.
            # (raise KeyError if still alive)
            returncode = self._zombies.pop(pid)

            # Child is dead, therefore we can fire the callback immediately.
            # First we remove it from the dict.
            # (raise KeyError if .remove_child_handler() was called in-between)
            del self._callbacks[pid]
        except KeyError:
            pass
        else:
            callback(pid, returncode, *args)

    def _do_waitpid_all(self):
        # Because of signal coalescing, we must keep calling waitpid() as
        # long as we're able to reap a child.
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                # No more child processes exist.
                return
            else:
                if pid == 0:
                    # A child process is still alive.
                    return

                returncode = self._compute_returncode(status)

            try:
                callback, args = self._callbacks.pop(pid)
            except KeyError:
                # unknown child
                with self._lock:
                    if self._forks:
                        # It may not be registered yet.
                        self._zombies[pid] = returncode
                        continue

                logger.warning(
                    "Caught subprocess termination from unknown pid: "
                    "%d -> %d", pid, returncode)
            else:
                callback(pid, returncode, *args)


class _UnixDefaultEventLoopPolicy(events.BaseDefaultEventLoopPolicy):
    """XXX"""
    _loop_factory = _UnixSelectorEventLoop

    def __init__(self):
        super().__init__()
        self._watcher = None

    def _init_watcher(self):
        with events._lock:
            if self._watcher is None:  # pragma: no branch
                if isinstance(threading.current_thread(),
                              threading._MainThread):
                    self._watcher = SafeChildWatcher(self._local._loop)
                else:
                    self._watcher = SafeChildWatcher(None)

    def set_event_loop(self, loop):
        """Set the event loop.

        As a side effect, if a child watcher was set before, then calling
        .set_event_loop() from the main thread will call .set_loop(loop) on the
        child watcher.
        """

        super().set_event_loop(loop)

        if self._watcher is not None and \
            isinstance(threading.current_thread(), threading._MainThread):
            self._watcher.set_loop(loop)

    def get_child_watcher(self):
        """Get the child watcher

        If not yet set, a SafeChildWatcher object is automatically created.
        """
        if self._watcher is None:
            self._init_watcher()

        return self._watcher

    def set_child_watcher(self, watcher):
        """Set the child watcher"""

        assert watcher is None or isinstance(watcher, AbstractChildWatcher)

        if self._watcher is not None:
            self._watcher.close()

        self._watcher = watcher

SelectorEventLoop = _UnixSelectorEventLoop
DefaultEventLoopPolicy = _UnixDefaultEventLoopPolicy
