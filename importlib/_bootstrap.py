"""Core implementation of import.

This module is NOT meant to be directly imported! It has been designed such
that it can be bootstrapped into Python as the implementation of import. As
such it requires the injection of specific modules and attributes in order to
work. One should use importlib as the public-facing version of this module.

"""

# See importlib._setup() for what is injected into the global namespace.

# When editing this code be aware that code executed at import time CANNOT
# reference any injected objects! This includes not only global code but also
# anything specified at the class level.


# Bootstrap-related code ######################################################

CASE_INSENSITIVE_PLATFORMS = 'win', 'cygwin', 'darwin'


def _make_relax_case():
    if sys.platform.startswith(CASE_INSENSITIVE_PLATFORMS):
        def _relax_case():
            """True if filenames must be checked case-insensitively."""
            return b'PYTHONCASEOK' in _os.environ
    else:
        def _relax_case():
            """True if filenames must be checked case-insensitively."""
            return False
    return _relax_case


# TODO: Expose from marshal
def _w_long(x):
    """Convert a 32-bit integer to little-endian.

    XXX Temporary until marshal's long functions are exposed.

    """
    x = int(x)
    int_bytes = []
    int_bytes.append(x & 0xFF)
    int_bytes.append((x >> 8) & 0xFF)
    int_bytes.append((x >> 16) & 0xFF)
    int_bytes.append((x >> 24) & 0xFF)
    return bytearray(int_bytes)


# TODO: Expose from marshal
def _r_long(int_bytes):
    """Convert 4 bytes in little-endian to an integer.

    XXX Temporary until marshal's long function are exposed.

    """
    x = int_bytes[0]
    x |= int_bytes[1] << 8
    x |= int_bytes[2] << 16
    x |= int_bytes[3] << 24
    return x


def _path_join(*args):
    """Replacement for os.path.join()."""
    sep = path_sep if args[0][-1:] not in path_separators else args[0][-1]
    return sep.join(x[:-len(path_sep)] if x.endswith(path_sep) else x
                    for x in args if x)


def _path_split(path):
    """Replacement for os.path.split()."""
    for x in reversed(path):
        if x in path_separators:
            sep = x
            break
    else:
        sep = path_sep
    front, _, tail = path.rpartition(sep)
    return front, tail


def _path_exists(path):
    """Replacement for os.path.exists."""
    try:
        _os.stat(path)
    except OSError:
        return False
    else:
        return True


def _path_is_mode_type(path, mode):
    """Test whether the path is the specified mode type."""
    try:
        stat_info = _os.stat(path)
    except OSError:
        return False
    return (stat_info.st_mode & 0o170000) == mode


# XXX Could also expose Modules/getpath.c:isfile()
def _path_isfile(path):
    """Replacement for os.path.isfile."""
    return _path_is_mode_type(path, 0o100000)


# XXX Could also expose Modules/getpath.c:isdir()
def _path_isdir(path):
    """Replacement for os.path.isdir."""
    if not path:
        path = _os.getcwd()
    return _path_is_mode_type(path, 0o040000)


def _path_without_ext(path, ext_type):
    """Replacement for os.path.splitext()[0]."""
    for suffix in _suffix_list(ext_type):
        if path.endswith(suffix):
            return path[:-len(suffix)]
    else:
        raise ValueError("path is not of the specified type")


def _path_absolute(path):
    """Replacement for os.path.abspath."""
    if not path:
        path = _os.getcwd()
    try:
        return _os._getfullpathname(path)
    except AttributeError:
        if path.startswith('/'):
            return path
        else:
            return _path_join(_os.getcwd(), path)


def _write_atomic(path, data):
    """Best-effort function to write data to a path atomically.
    Be prepared to handle a FileExistsError if concurrent writing of the
    temporary file is attempted."""
    # id() is used to generate a pseudo-random filename.
    path_tmp = '{}.{}'.format(path, id(path))
    fd = _os.open(path_tmp, _os.O_EXCL | _os.O_CREAT | _os.O_WRONLY, 0o666)
    try:
        # We first write data to a temporary file, and then use os.replace() to
        # perform an atomic rename.
        with _io.FileIO(fd, 'wb') as file:
            file.write(data)
        _os.replace(path_tmp, path)
    except OSError:
        try:
            _os.unlink(path_tmp)
        except OSError:
            pass
        raise


def _wrap(new, old):
    """Simple substitute for functools.wraps."""
    for replace in ['__module__', '__name__', '__qualname__', '__doc__']:
        if hasattr(old, replace):
            setattr(new, replace, getattr(old, replace))
    new.__dict__.update(old.__dict__)


code_type = type(_wrap.__code__)


def _new_module(name):
    """Create a new module.

    The module is not entered into sys.modules.

    """
    return type(sys)(name)


# Finder/loader utility code ##################################################

PYCACHE = '__pycache__'

DEBUG_BYTECODE_SUFFIX = '.pyc'
OPT_BYTECODE_SUFFIX = '.pyo'
BYTECODE_SUFFIX = DEBUG_BYTECODE_SUFFIX if __debug__ else OPT_BYTECODE_SUFFIX

def _cache_from_source(path, debug_override=None):
    """Given the path to a .py file, return the path to its .pyc/.pyo file.

    The .py file does not need to exist; this simply returns the path to the
    .pyc/.pyo file calculated as if the .py file were imported.  The extension
    will be .pyc unless __debug__ is not defined, then it will be .pyo.

    If debug_override is not None, then it must be a boolean and is taken as
    the value of __debug__ instead.

    """
    debug = __debug__ if debug_override is None else debug_override
    suffix = DEBUG_BYTECODE_SUFFIX if debug else OPT_BYTECODE_SUFFIX
    head, tail = _path_split(path)
    base_filename, sep, _ = tail.partition('.')
    filename = '{}{}{}{}'.format(base_filename, sep, _imp.get_tag(), suffix)
    return _path_join(head, PYCACHE, filename)


def verbose_message(message, *args):
    """Print the message to stderr if -v/PYTHONVERBOSE is turned on."""
    if sys.flags.verbose:
        if not message.startswith(('#', 'import ')):
            message = '# ' + message
        print(message.format(*args), file=sys.stderr)


def set_package(fxn):
    """Set __package__ on the returned module."""
    def set_package_wrapper(*args, **kwargs):
        module = fxn(*args, **kwargs)
        if not hasattr(module, '__package__') or module.__package__ is None:
            module.__package__ = module.__name__
            if not hasattr(module, '__path__'):
                module.__package__ = module.__package__.rpartition('.')[0]
        return module
    _wrap(set_package_wrapper, fxn)
    return set_package_wrapper


def set_loader(fxn):
    """Set __loader__ on the returned module."""
    def set_loader_wrapper(self, *args, **kwargs):
        module = fxn(self, *args, **kwargs)
        if not hasattr(module, '__loader__'):
            module.__loader__ = self
        return module
    _wrap(set_loader_wrapper, fxn)
    return set_loader_wrapper


def module_for_loader(fxn):
    """Decorator to handle selecting the proper module for loaders.

    The decorated function is passed the module to use instead of the module
    name. The module passed in to the function is either from sys.modules if
    it already exists or is a new module which has __name__ set and is inserted
    into sys.modules. If an exception is raised and the decorator created the
    module it is subsequently removed from sys.modules.

    The decorator assumes that the decorated function takes the module name as
    the second argument.

    """
    def module_for_loader_wrapper(self, fullname, *args, **kwargs):
        module = sys.modules.get(fullname)
        is_reload = module is not None
        if not is_reload:
            # This must be done before open() is called as the 'io' module
            # implicitly imports 'locale' and would otherwise trigger an
            # infinite loop.
            module = _new_module(fullname)
            sys.modules[fullname] = module
        try:
            return fxn(self, module, *args, **kwargs)
        except:
            if not is_reload:
                del sys.modules[fullname]
            raise
    _wrap(module_for_loader_wrapper, fxn)
    return module_for_loader_wrapper


def _check_name(method):
    """Decorator to verify that the module being requested matches the one the
    loader can handle.

    The first argument (self) must define _name which the second argument is
    compared against. If the comparison fails then ImportError is raised.

    """
    def _check_name_wrapper(self, name, *args, **kwargs):
        if self._name != name:
            raise ImportError("loader cannot handle %s" % name, name=name)
        return method(self, name, *args, **kwargs)
    _wrap(_check_name_wrapper, method)
    return _check_name_wrapper


def _requires_builtin(fxn):
    """Decorator to verify the named module is built-in."""
    def _requires_builtin_wrapper(self, fullname):
        if fullname not in sys.builtin_module_names:
            raise ImportError("{0} is not a built-in module".format(fullname),
                              name=fullname)
        return fxn(self, fullname)
    _wrap(_requires_builtin_wrapper, fxn)
    return _requires_builtin_wrapper


def _requires_frozen(fxn):
    """Decorator to verify the named module is frozen."""
    def _requires_frozen_wrapper(self, fullname):
        if not _imp.is_frozen(fullname):
            raise ImportError("{0} is not a frozen module".format(fullname),
                              name=fullname)
        return fxn(self, fullname)
    _wrap(_requires_frozen_wrapper, fxn)
    return _requires_frozen_wrapper


def _suffix_list(suffix_type):
    """Return a list of file suffixes based on the imp file type."""
    return [suffix[0] for suffix in _imp.get_suffixes()
            if suffix[2] == suffix_type]


# Loaders #####################################################################

class BuiltinImporter:

    """Meta path import for built-in modules.

    All methods are either class or static methods to avoid the need to
    instantiate the class.

    """

    @classmethod
    def find_module(cls, fullname, path=None):
        """Find the built-in module.

        If 'path' is ever specified then the search is considered a failure.

        """
        if path is not None:
            return None
        return cls if _imp.is_builtin(fullname) else None

    @classmethod
    @set_package
    @set_loader
    @_requires_builtin
    def load_module(cls, fullname):
        """Load a built-in module."""
        is_reload = fullname in sys.modules
        try:
            return _imp.init_builtin(fullname)
        except:
            if not is_reload and fullname in sys.modules:
                del sys.modules[fullname]
            raise

    @classmethod
    @_requires_builtin
    def get_code(cls, fullname):
        """Return None as built-in modules do not have code objects."""
        return None

    @classmethod
    @_requires_builtin
    def get_source(cls, fullname):
        """Return None as built-in modules do not have source code."""
        return None

    @classmethod
    @_requires_builtin
    def is_package(cls, fullname):
        """Return None as built-in modules are never packages."""
        return False


class FrozenImporter:

    """Meta path import for frozen modules.

    All methods are either class or static methods to avoid the need to
    instantiate the class.

    """

    @classmethod
    def find_module(cls, fullname, path=None):
        """Find a frozen module."""
        return cls if _imp.is_frozen(fullname) else None

    @classmethod
    @set_package
    @set_loader
    @_requires_frozen
    def load_module(cls, fullname):
        """Load a frozen module."""
        is_reload = fullname in sys.modules
        try:
            return _imp.init_frozen(fullname)
        except:
            if not is_reload and fullname in sys.modules:
                del sys.modules[fullname]
            raise

    @classmethod
    @_requires_frozen
    def get_code(cls, fullname):
        """Return the code object for the frozen module."""
        return _imp.get_frozen_object(fullname)

    @classmethod
    @_requires_frozen
    def get_source(cls, fullname):
        """Return None as frozen modules do not have source code."""
        return None

    @classmethod
    @_requires_frozen
    def is_package(cls, fullname):
        """Return if the frozen module is a package."""
        return _imp.is_frozen_package(fullname)


class _LoaderBasics:

    """Base class of common code needed by both SourceLoader and
    _SourcelessFileLoader."""

    def is_package(self, fullname):
        """Concrete implementation of InspectLoader.is_package by checking if
        the path returned by get_filename has a filename of '__init__.py'."""
        filename = _path_split(self.get_filename(fullname))[1]
        return filename.rsplit('.', 1)[0] == '__init__'

    def _bytes_from_bytecode(self, fullname, data, bytecode_path, source_stats):
        """Return the marshalled bytes from bytecode, verifying the magic
        number, timestamp and source size along the way.

        If source_stats is None then skip the timestamp check.

        """
        magic = data[:4]
        raw_timestamp = data[4:8]
        raw_size = data[8:12]
        if magic != _MAGIC_NUMBER:
            msg = 'bad magic number in {!r}: {!r}'.format(fullname, magic)
            raise ImportError(msg, name=fullname, path=bytecode_path)
        elif len(raw_timestamp) != 4:
            message = 'bad timestamp in {}'.format(fullname)
            verbose_message(message)
            raise EOFError(message)
        elif len(raw_size) != 4:
            message = 'bad size in {}'.format(fullname)
            verbose_message(message)
            raise EOFError(message)
        if source_stats is not None:
            try:
                source_mtime = int(source_stats['mtime'])
            except KeyError:
                pass
            else:
                if _r_long(raw_timestamp) != source_mtime:
                    message = 'bytecode is stale for {}'.format(fullname)
                    verbose_message(message)
                    raise ImportError(message, name=fullname,
                                      path=bytecode_path)
            try:
                source_size = source_stats['size'] & 0xFFFFFFFF
            except KeyError:
                pass
            else:
                if _r_long(raw_size) != source_size:
                    raise ImportError(
                        "bytecode is stale for {}".format(fullname),
                        name=fullname, path=bytecode_path)
        # Can't return the code object as errors from marshal loading need to
        # propagate even when source is available.
        return data[12:]

    @module_for_loader
    def _load_module(self, module, *, sourceless=False):
        """Helper for load_module able to handle either source or sourceless
        loading."""
        name = module.__name__
        code_object = self.get_code(name)
        module.__file__ = self.get_filename(name)
        if not sourceless:
            module.__cached__ = _cache_from_source(module.__file__)
        else:
            module.__cached__ = module.__file__
        module.__package__ = name
        if self.is_package(name):
            module.__path__ = [_path_split(module.__file__)[0]]
        else:
            module.__package__ = module.__package__.rpartition('.')[0]
        module.__loader__ = self
        exec(code_object, module.__dict__)
        return module


class SourceLoader(_LoaderBasics):

    def path_mtime(self, path):
        """Optional method that returns the modification time (an int) for the
        specified path, where path is a str.
        """
        raise NotImplementedError

    def path_stats(self, path):
        """Optional method returning a metadata dict for the specified path
        to by the path (str).
        Possible keys:
        - 'mtime' (mandatory) is the numeric timestamp of last source
          code modification;
        - 'size' (optional) is the size in bytes of the source code.

        Implementing this method allows the loader to read bytecode files.
        """
        return {'mtime': self.path_mtime(path)}

    def set_data(self, path, data):
        """Optional method which writes data (bytes) to a file path (a str).

        Implementing this method allows for the writing of bytecode files.

        """
        raise NotImplementedError


    def get_source(self, fullname):
        """Concrete implementation of InspectLoader.get_source."""
        import tokenize
        path = self.get_filename(fullname)
        try:
            source_bytes = self.get_data(path)
        except IOError:
            raise ImportError("source not available through get_data()",
                              name=fullname)
        encoding = tokenize.detect_encoding(_io.BytesIO(source_bytes).readline)
        newline_decoder = _io.IncrementalNewlineDecoder(None, True)
        return newline_decoder.decode(source_bytes.decode(encoding[0]))

    def get_code(self, fullname):
        """Concrete implementation of InspectLoader.get_code.

        Reading of bytecode requires path_stats to be implemented. To write
        bytecode, set_data must also be implemented.

        """
        source_path = self.get_filename(fullname)
        bytecode_path = _cache_from_source(source_path)
        source_mtime = None
        if bytecode_path is not None:
            try:
                st = self.path_stats(source_path)
            except NotImplementedError:
                pass
            else:
                source_mtime = int(st['mtime'])
                try:
                    data = self.get_data(bytecode_path)
                except IOError:
                    pass
                else:
                    try:
                        bytes_data = self._bytes_from_bytecode(fullname, data,
                                                               bytecode_path,
                                                               st)
                    except (ImportError, EOFError):
                        pass
                    else:
                        verbose_message('{} matches {}', bytecode_path,
                                        source_path)
                        found = marshal.loads(bytes_data)
                        if isinstance(found, code_type):
                            _imp._fix_co_filename(found, source_path)
                            verbose_message('code object from {}',
                                            bytecode_path)
                            return found
                        else:
                            msg = "Non-code object in {}"
                            raise ImportError(msg.format(bytecode_path),
                                              name=fullname, path=bytecode_path)
        source_bytes = self.get_data(source_path)
        code_object = compile(source_bytes, source_path, 'exec',
                                dont_inherit=True)
        verbose_message('code object from {}', source_path)
        if (not sys.dont_write_bytecode and bytecode_path is not None and
            source_mtime is not None):
            data = bytearray(_MAGIC_NUMBER)
            data.extend(_w_long(source_mtime))
            data.extend(_w_long(len(source_bytes)))
            data.extend(marshal.dumps(code_object))
            try:
                self.set_data(bytecode_path, data)
                verbose_message('wrote {!r}', bytecode_path)
            except NotImplementedError:
                pass
        return code_object

    def load_module(self, fullname):
        """Concrete implementation of Loader.load_module.

        Requires ExecutionLoader.get_filename and ResourceLoader.get_data to be
        implemented to load source code. Use of bytecode is dictated by whether
        get_code uses/writes bytecode.

        """
        return self._load_module(fullname)


class _FileLoader:

    """Base file loader class which implements the loader protocol methods that
    require file system usage."""

    def __init__(self, fullname, path):
        """Cache the module name and the path to the file found by the
        finder."""
        self._name = fullname
        self._path = path

    @_check_name
    def get_filename(self, fullname):
        """Return the path to the source file as found by the finder."""
        return self._path

    def get_data(self, path):
        """Return the data from path as raw bytes."""
        with _io.FileIO(path, 'r') as file:
            return file.read()


class _SourceFileLoader(_FileLoader, SourceLoader):

    """Concrete implementation of SourceLoader using the file system."""

    def path_stats(self, path):
        """Return the metadat for the path."""
        st = _os.stat(path)
        return {'mtime': st.st_mtime, 'size': st.st_size}

    def set_data(self, path, data):
        """Write bytes data to a file."""
        parent, filename = _path_split(path)
        path_parts = []
        # Figure out what directories are missing.
        while parent and not _path_isdir(parent):
            parent, part = _path_split(parent)
            path_parts.append(part)
        # Create needed directories.
        for part in reversed(path_parts):
            parent = _path_join(parent, part)
            try:
                _os.mkdir(parent)
            except FileExistsError:
                # Probably another Python process already created the dir.
                continue
            except PermissionError:
                # If can't get proper access, then just forget about writing
                # the data.
                return
        try:
            _write_atomic(path, data)
            verbose_message('created {!r}', path)
        except (PermissionError, FileExistsError):
            # Don't worry if you can't write bytecode or someone is writing
            # it at the same time.
            pass


class _SourcelessFileLoader(_FileLoader, _LoaderBasics):

    """Loader which handles sourceless file imports."""

    def load_module(self, fullname):
        return self._load_module(fullname, sourceless=True)

    def get_code(self, fullname):
        path = self.get_filename(fullname)
        data = self.get_data(path)
        bytes_data = self._bytes_from_bytecode(fullname, data, path, None)
        found = marshal.loads(bytes_data)
        if isinstance(found, code_type):
            verbose_message('code object from {!r}', path)
            return found
        else:
            raise ImportError("Non-code object in {}".format(path),
                              name=fullname, path=path)

    def get_source(self, fullname):
        """Return None as there is no source code."""
        return None


class _ExtensionFileLoader:

    """Loader for extension modules.

    The constructor is designed to work with FileFinder.

    """

    def __init__(self, name, path):
        self._name = name
        self._path = path

    @_check_name
    @set_package
    @set_loader
    def load_module(self, fullname):
        """Load an extension module."""
        is_reload = fullname in sys.modules
        try:
            module = _imp.load_dynamic(fullname, self._path)
            verbose_message('extension module loaded from {!r}', self._path)
            return module
        except:
            if not is_reload and fullname in sys.modules:
                del sys.modules[fullname]
            raise

    @_check_name
    def is_package(self, fullname):
        """Return False as an extension module can never be a package."""
        return False

    @_check_name
    def get_code(self, fullname):
        """Return None as an extension module cannot create a code object."""
        return None

    @_check_name
    def get_source(self, fullname):
        """Return None as extension modules have no source code."""
        return None


# Finders #####################################################################

class PathFinder:

    """Meta path finder for sys.(path|path_hooks|path_importer_cache)."""

    @classmethod
    def _path_hooks(cls, path, hooks=None):
        """Search sequence of hooks for a finder for 'path'.

        If 'hooks' is false then use sys.path_hooks.

        """
        if hooks is None:
            hooks = sys.path_hooks
        for hook in hooks:
            try:
                return hook(path)
            except ImportError:
                continue
        else:
            raise ImportError("no path hook found for {0}".format(path),
                              path=path)

    @classmethod
    def _path_importer_cache(cls, path, default=None):
        """Get the finder for the path from sys.path_importer_cache.

        If the path is not in the cache, find the appropriate finder and cache
        it. If None is cached, get the default finder and cache that
        (if applicable).

        Because of NullImporter, some finder should be returned. The only
        explicit fail case is if None is cached but the path cannot be used for
        the default hook, for which ImportError is raised.

        """
        if path == '':
            path = '.'
        try:
            finder = sys.path_importer_cache[path]
        except KeyError:
            finder = cls._path_hooks(path)
            sys.path_importer_cache[path] = finder
        else:
            if finder is None and default:
                # Raises ImportError on failure.
                finder = default(path)
                sys.path_importer_cache[path] = finder
        return finder

    @classmethod
    def find_module(cls, fullname, path=None):
        """Find the module on sys.path or 'path' based on sys.path_hooks and
        sys.path_importer_cache."""
        if path is None:
            path = sys.path
        for entry in path:
            try:
                finder = cls._path_importer_cache(entry)
            except ImportError:
                continue
            if finder:
                loader = finder.find_module(fullname)
                if loader:
                    return loader
        else:
            return None


class _FileFinder:

    """File-based finder.

    Constructor takes a list of objects detailing what file extensions their
    loader supports along with whether it can be used for a package.

    """

    def __init__(self, path, *details):
        """Initialize with finder details."""
        packages = []
        modules = []
        for detail in details:
            modules.extend((suffix, detail.loader) for suffix in detail.suffixes)
            if detail.supports_packages:
                packages.extend((suffix, detail.loader)
                                for suffix in detail.suffixes)
        self.packages = packages
        self.modules = modules
        # Base (directory) path
        self.path = path or '.'
        self._path_mtime = -1
        self._path_cache = set()
        self._relaxed_path_cache = set()

    def invalidate_caches(self):
        """Invalidate the directory mtime."""
        self._path_mtime = -1

    def find_module(self, fullname):
        """Try to find a loader for the specified module."""
        tail_module = fullname.rpartition('.')[2]
        try:
            mtime = _os.stat(self.path).st_mtime
        except OSError:
            mtime = -1
        if mtime != self._path_mtime:
            self._fill_cache()
            self._path_mtime = mtime
        # tail_module keeps the original casing, for __file__ and friends
        if _relax_case():
            cache = self._relaxed_path_cache
            cache_module = tail_module.lower()
        else:
            cache = self._path_cache
            cache_module = tail_module
        # Check if the module is the name of a directory (and thus a package).
        if cache_module in cache:
            base_path = _path_join(self.path, tail_module)
            if _path_isdir(base_path):
                for suffix, loader in self.packages:
                    init_filename = '__init__' + suffix
                    full_path = _path_join(base_path, init_filename)
                    if _path_isfile(full_path):
                        return loader(fullname, full_path)
                else:
                    msg = "Not importing directory {}: missing __init__"
                    _warnings.warn(msg.format(base_path), ImportWarning)
        # Check for a file w/ a proper suffix exists.
        for suffix, loader in self.modules:
            if cache_module + suffix in cache:
                full_path = _path_join(self.path, tail_module + suffix)
                if _path_isfile(full_path):
                    return loader(fullname, full_path)
        return None

    def _fill_cache(self):
        """Fill the cache of potential modules and packages for this directory."""
        path = self.path
        contents = _os.listdir(path)
        # We store two cached versions, to handle runtime changes of the
        # PYTHONCASEOK environment variable.
        if not sys.platform.startswith('win'):
            self._path_cache = set(contents)
        else:
            # Windows users can import modules with case-insensitive file
            # suffixes (for legacy reasons). Make the suffix lowercase here
            # so it's done once instead of for every import. This is safe as
            # the specified suffixes to check against are always specified in a
            # case-sensitive manner.
            lower_suffix_contents = set()
            for item in contents:
                name, dot, suffix = item.partition('.')
                if dot:
                    new_name = '{}.{}'.format(name, suffix.lower())
                else:
                    new_name = name
                lower_suffix_contents.add(new_name)
            self._path_cache = lower_suffix_contents
        if sys.platform.startswith(CASE_INSENSITIVE_PLATFORMS):
            self._relaxed_path_cache = set(fn.lower() for fn in contents)


class _SourceFinderDetails:

    loader = _SourceFileLoader
    supports_packages = True

    def __init__(self):
        self.suffixes = _suffix_list(_imp.PY_SOURCE)

class _SourcelessFinderDetails:

    loader = _SourcelessFileLoader
    supports_packages = True

    def __init__(self):
        self.suffixes = _suffix_list(_imp.PY_COMPILED)


class _ExtensionFinderDetails:

    loader = _ExtensionFileLoader
    supports_packages = False

    def __init__(self):
        self.suffixes = _suffix_list(_imp.C_EXTENSION)


# Import itself ###############################################################

def _file_path_hook(path):
    """If the path is a directory, return a file-based finder."""
    if _path_isdir(path):
        return _FileFinder(path, _ExtensionFinderDetails(),
                           _SourceFinderDetails(),
                           _SourcelessFinderDetails())
    else:
        raise ImportError("only directories are supported", path=path)


_DEFAULT_PATH_HOOK = _file_path_hook

class _DefaultPathFinder(PathFinder):

    """Subclass of PathFinder that implements implicit semantics for
    __import__."""

    @classmethod
    def _path_hooks(cls, path):
        """Search sys.path_hooks as well as implicit path hooks."""
        try:
            return super()._path_hooks(path)
        except ImportError:
            implicit_hooks = [_DEFAULT_PATH_HOOK, _imp.NullImporter]
            return super()._path_hooks(path, implicit_hooks)

    @classmethod
    def _path_importer_cache(cls, path):
        """Use the default path hook when None is stored in
        sys.path_importer_cache."""
        return super()._path_importer_cache(path, _DEFAULT_PATH_HOOK)


class _ImportLockContext:

    """Context manager for the import lock."""

    def __enter__(self):
        """Acquire the import lock."""
        _imp.acquire_lock()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Release the import lock regardless of any raised exceptions."""
        _imp.release_lock()


def _resolve_name(name, package, level):
    """Resolve a relative module name to an absolute one."""
    bits = package.rsplit('.', level - 1)
    if len(bits) < level:
        raise ValueError('attempted relative import beyond top-level package')
    base = bits[0]
    return '{0}.{1}'.format(base, name) if name else base


def _find_module(name, path):
    """Find a module's loader."""
    meta_path = sys.meta_path + _IMPLICIT_META_PATH
    for finder in meta_path:
        loader = finder.find_module(name, path)
        if loader is not None:
            # The parent import may have already imported this module.
            if name not in sys.modules:
                return loader
            else:
                return sys.modules[name].__loader__
    else:
        return None


def _sanity_check(name, package, level):
    """Verify arguments are "sane"."""
    if not isinstance(name, str):
        raise TypeError("module name must be str, not {}".format(type(name)))
    if level < 0:
        raise ValueError('level must be >= 0')
    if package:
        if not isinstance(package, str):
            raise TypeError("__package__ not set to a string")
        elif package not in sys.modules:
            msg = ("Parent module {0!r} not loaded, cannot perform relative "
                   "import")
            raise SystemError(msg.format(package))
    if not name and level == 0:
        raise ValueError("Empty module name")


_IMPLICIT_META_PATH = [BuiltinImporter, FrozenImporter, _DefaultPathFinder]

_ERR_MSG = 'No module named {!r}'

def _find_and_load(name, import_):
    """Find and load the module."""
    path = None
    parent = name.rpartition('.')[0]
    if parent:
        if parent not in sys.modules:
            import_(parent)
        # Crazy side-effects!
        if name in sys.modules:
            return sys.modules[name]
        # Backwards-compatibility; be nicer to skip the dict lookup.
        parent_module = sys.modules[parent]
        try:
            path = parent_module.__path__
        except AttributeError:
            msg = (_ERR_MSG + '; {} is not a package').format(name, parent)
            raise ImportError(msg, name=name)
    loader = _find_module(name, path)
    if loader is None:
        raise ImportError(_ERR_MSG.format(name), name=name)
    elif name not in sys.modules:
        # The parent import may have already imported this module.
        loader.load_module(name)
        verbose_message('import {!r} # {!r}', name, loader)
    # Backwards-compatibility; be nicer to skip the dict lookup.
    module = sys.modules[name]
    if parent:
        # Set the module as an attribute on its parent.
        parent_module = sys.modules[parent]
        setattr(parent_module, name.rpartition('.')[2], module)
    # Set __package__ if the loader did not.
    if not hasattr(module, '__package__') or module.__package__ is None:
        try:
            module.__package__ = module.__name__
            if not hasattr(module, '__path__'):
                module.__package__ = module.__package__.rpartition('.')[0]
        except AttributeError:
            pass
    return module


def _gcd_import(name, package=None, level=0):
    """Import and return the module based on its name, the package the call is
    being made from, and the level adjustment.

    This function represents the greatest common denominator of functionality
    between import_module and __import__. This includes setting __package__ if
    the loader did not.

    """
    _sanity_check(name, package, level)
    if level > 0:
        name = _resolve_name(name, package, level)
    with _ImportLockContext():
        try:
            module = sys.modules[name]
            if module is None:
                message = ("import of {} halted; "
                            "None in sys.modules".format(name))
                raise ImportError(message, name=name)
            return module
        except KeyError:
            pass  # Don't want to chain the exception
        return _find_and_load(name, _gcd_import)


def _handle_fromlist(module, fromlist, import_):
    """Figure out what __import__ should return.

    The import_ parameter is a callable which takes the name of module to
    import. It is required to decouple the function from assuming importlib's
    import implementation is desired.

    """
    # The hell that is fromlist ...
    # If a package was imported, try to import stuff from fromlist.
    if hasattr(module, '__path__'):
        if '*' in fromlist and hasattr(module, '__all__'):
            fromlist = list(fromlist)
            fromlist.remove('*')
            fromlist.extend(module.__all__)
        for x in (y for y in fromlist if not hasattr(module, y)):
            try:
                import_('{0}.{1}'.format(module.__name__, x))
            except ImportError:
                pass
    return module


def _calc___package__(globals):
    """Calculate what __package__ should be.

    __package__ is not guaranteed to be defined or could be set to None
    to represent that its proper value is unknown.

    """
    package = globals.get('__package__')
    if package is None:
        package = globals['__name__']
        if '__path__' not in globals:
            package = package.rpartition('.')[0]
    return package


def __import__(name, globals={}, locals={}, fromlist=[], level=0):
    """Import a module.

    The 'globals' argument is used to infer where the import is occuring from
    to handle relative imports. The 'locals' argument is ignored. The
    'fromlist' argument specifies what should exist as attributes on the module
    being imported (e.g. ``from module import <fromlist>``).  The 'level'
    argument represents the package location to import from in a relative
    import (e.g. ``from ..pkg import mod`` would have a 'level' of 2).

    """
    if level == 0:
        module = _gcd_import(name)
    else:
        package = _calc___package__(globals)
        module = _gcd_import(name, package, level)
    if not fromlist:
        # Return up to the first dot in 'name'. This is complicated by the fact
        # that 'name' may be relative.
        if level == 0:
            return sys.modules[name.partition('.')[0]]
        elif not name:
            return module
        else:
            cut_off = len(name) - len(name.partition('.')[0])
            return sys.modules[module.__name__[:len(module.__name__)-cut_off]]
    else:
        return _handle_fromlist(module, fromlist, _gcd_import)


_MAGIC_NUMBER = None  # Set in _setup()


def _setup(sys_module, _imp_module):
    """Setup importlib by importing needed built-in modules and injecting them
    into the global namespace.

    As sys is needed for sys.modules access and _imp is needed to load built-in
    modules, those two modules must be explicitly passed in.

    """
    global _imp, sys
    _imp = _imp_module
    sys = sys_module

    for module in (_imp, sys):
        if not hasattr(module, '__loader__'):
            module.__loader__ = BuiltinImporter

    self_module = sys.modules[__name__]
    for builtin_name in ('_io', '_warnings', 'builtins', 'marshal'):
        if builtin_name not in sys.modules:
            builtin_module = BuiltinImporter.load_module(builtin_name)
        else:
            builtin_module = sys.modules[builtin_name]
        setattr(self_module, builtin_name, builtin_module)

    os_details = ('posix', ['/']), ('nt', ['\\', '/']), ('os2', ['\\', '/'])
    for builtin_os, path_separators in os_details:
        path_sep = path_separators[0]
        if builtin_os in sys.modules:
            os_module = sys.modules[builtin_os]
            break
        else:
            try:
                os_module = BuiltinImporter.load_module(builtin_os)
                # TODO: rip out os2 code after 3.3 is released as per PEP 11
                if builtin_os == 'os2' and 'EMX GCC' in sys.version:
                    path_sep = path_separators[1]
                break
            except ImportError:
                continue
    else:
        raise ImportError('importlib requires posix or nt')
    setattr(self_module, '_os', os_module)
    setattr(self_module, 'path_sep', path_sep)
    setattr(self_module, 'path_separators', set(path_separators))
    # Constants
    setattr(self_module, '_relax_case', _make_relax_case())
    setattr(self_module, '_MAGIC_NUMBER', _imp_module.get_magic())


def _install(sys_module, _imp_module):
    """Install importlib as the implementation of import.

    It is assumed that _imp and sys have been imported and injected into the
    global namespace for the module prior to calling this function.

    """
    _setup(sys_module, _imp_module)
    orig_import = builtins.__import__
    builtins.__import__ = __import__
    builtins.__original_import__ = orig_import
