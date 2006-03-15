""" Python Character Mapping Codec mac_greek generated from 'MAPPINGS/VENDORS/APPLE/GREEK.TXT' with gencodec.py.

"""#"

import codecs

### Codec APIs

class Codec(codecs.Codec):

    def encode(self,input,errors='strict'):
        return codecs.charmap_encode(input,errors,encoding_map)

    def decode(self,input,errors='strict'):
        return codecs.charmap_decode(input,errors,decoding_table)

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return codecs.charmap_encode(input,self.errors,encoding_map)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return codecs.charmap_decode(input,self.errors,decoding_table)[0]

class StreamWriter(Codec,codecs.StreamWriter):
    pass

class StreamReader(Codec,codecs.StreamReader):
    pass

### encodings module API

def getregentry():
    return codecs.CodecInfo(
        name='mac-greek',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )


### Decoding Table

decoding_table = (
    u'\x00'     #  0x00 -> CONTROL CHARACTER
    u'\x01'     #  0x01 -> CONTROL CHARACTER
    u'\x02'     #  0x02 -> CONTROL CHARACTER
    u'\x03'     #  0x03 -> CONTROL CHARACTER
    u'\x04'     #  0x04 -> CONTROL CHARACTER
    u'\x05'     #  0x05 -> CONTROL CHARACTER
    u'\x06'     #  0x06 -> CONTROL CHARACTER
    u'\x07'     #  0x07 -> CONTROL CHARACTER
    u'\x08'     #  0x08 -> CONTROL CHARACTER
    u'\t'       #  0x09 -> CONTROL CHARACTER
    u'\n'       #  0x0A -> CONTROL CHARACTER
    u'\x0b'     #  0x0B -> CONTROL CHARACTER
    u'\x0c'     #  0x0C -> CONTROL CHARACTER
    u'\r'       #  0x0D -> CONTROL CHARACTER
    u'\x0e'     #  0x0E -> CONTROL CHARACTER
    u'\x0f'     #  0x0F -> CONTROL CHARACTER
    u'\x10'     #  0x10 -> CONTROL CHARACTER
    u'\x11'     #  0x11 -> CONTROL CHARACTER
    u'\x12'     #  0x12 -> CONTROL CHARACTER
    u'\x13'     #  0x13 -> CONTROL CHARACTER
    u'\x14'     #  0x14 -> CONTROL CHARACTER
    u'\x15'     #  0x15 -> CONTROL CHARACTER
    u'\x16'     #  0x16 -> CONTROL CHARACTER
    u'\x17'     #  0x17 -> CONTROL CHARACTER
    u'\x18'     #  0x18 -> CONTROL CHARACTER
    u'\x19'     #  0x19 -> CONTROL CHARACTER
    u'\x1a'     #  0x1A -> CONTROL CHARACTER
    u'\x1b'     #  0x1B -> CONTROL CHARACTER
    u'\x1c'     #  0x1C -> CONTROL CHARACTER
    u'\x1d'     #  0x1D -> CONTROL CHARACTER
    u'\x1e'     #  0x1E -> CONTROL CHARACTER
    u'\x1f'     #  0x1F -> CONTROL CHARACTER
    u' '        #  0x20 -> SPACE
    u'!'        #  0x21 -> EXCLAMATION MARK
    u'"'        #  0x22 -> QUOTATION MARK
    u'#'        #  0x23 -> NUMBER SIGN
    u'$'        #  0x24 -> DOLLAR SIGN
    u'%'        #  0x25 -> PERCENT SIGN
    u'&'        #  0x26 -> AMPERSAND
    u"'"        #  0x27 -> APOSTROPHE
    u'('        #  0x28 -> LEFT PARENTHESIS
    u')'        #  0x29 -> RIGHT PARENTHESIS
    u'*'        #  0x2A -> ASTERISK
    u'+'        #  0x2B -> PLUS SIGN
    u','        #  0x2C -> COMMA
    u'-'        #  0x2D -> HYPHEN-MINUS
    u'.'        #  0x2E -> FULL STOP
    u'/'        #  0x2F -> SOLIDUS
    u'0'        #  0x30 -> DIGIT ZERO
    u'1'        #  0x31 -> DIGIT ONE
    u'2'        #  0x32 -> DIGIT TWO
    u'3'        #  0x33 -> DIGIT THREE
    u'4'        #  0x34 -> DIGIT FOUR
    u'5'        #  0x35 -> DIGIT FIVE
    u'6'        #  0x36 -> DIGIT SIX
    u'7'        #  0x37 -> DIGIT SEVEN
    u'8'        #  0x38 -> DIGIT EIGHT
    u'9'        #  0x39 -> DIGIT NINE
    u':'        #  0x3A -> COLON
    u';'        #  0x3B -> SEMICOLON
    u'<'        #  0x3C -> LESS-THAN SIGN
    u'='        #  0x3D -> EQUALS SIGN
    u'>'        #  0x3E -> GREATER-THAN SIGN
    u'?'        #  0x3F -> QUESTION MARK
    u'@'        #  0x40 -> COMMERCIAL AT
    u'A'        #  0x41 -> LATIN CAPITAL LETTER A
    u'B'        #  0x42 -> LATIN CAPITAL LETTER B
    u'C'        #  0x43 -> LATIN CAPITAL LETTER C
    u'D'        #  0x44 -> LATIN CAPITAL LETTER D
    u'E'        #  0x45 -> LATIN CAPITAL LETTER E
    u'F'        #  0x46 -> LATIN CAPITAL LETTER F
    u'G'        #  0x47 -> LATIN CAPITAL LETTER G
    u'H'        #  0x48 -> LATIN CAPITAL LETTER H
    u'I'        #  0x49 -> LATIN CAPITAL LETTER I
    u'J'        #  0x4A -> LATIN CAPITAL LETTER J
    u'K'        #  0x4B -> LATIN CAPITAL LETTER K
    u'L'        #  0x4C -> LATIN CAPITAL LETTER L
    u'M'        #  0x4D -> LATIN CAPITAL LETTER M
    u'N'        #  0x4E -> LATIN CAPITAL LETTER N
    u'O'        #  0x4F -> LATIN CAPITAL LETTER O
    u'P'        #  0x50 -> LATIN CAPITAL LETTER P
    u'Q'        #  0x51 -> LATIN CAPITAL LETTER Q
    u'R'        #  0x52 -> LATIN CAPITAL LETTER R
    u'S'        #  0x53 -> LATIN CAPITAL LETTER S
    u'T'        #  0x54 -> LATIN CAPITAL LETTER T
    u'U'        #  0x55 -> LATIN CAPITAL LETTER U
    u'V'        #  0x56 -> LATIN CAPITAL LETTER V
    u'W'        #  0x57 -> LATIN CAPITAL LETTER W
    u'X'        #  0x58 -> LATIN CAPITAL LETTER X
    u'Y'        #  0x59 -> LATIN CAPITAL LETTER Y
    u'Z'        #  0x5A -> LATIN CAPITAL LETTER Z
    u'['        #  0x5B -> LEFT SQUARE BRACKET
    u'\\'       #  0x5C -> REVERSE SOLIDUS
    u']'        #  0x5D -> RIGHT SQUARE BRACKET
    u'^'        #  0x5E -> CIRCUMFLEX ACCENT
    u'_'        #  0x5F -> LOW LINE
    u'`'        #  0x60 -> GRAVE ACCENT
    u'a'        #  0x61 -> LATIN SMALL LETTER A
    u'b'        #  0x62 -> LATIN SMALL LETTER B
    u'c'        #  0x63 -> LATIN SMALL LETTER C
    u'd'        #  0x64 -> LATIN SMALL LETTER D
    u'e'        #  0x65 -> LATIN SMALL LETTER E
    u'f'        #  0x66 -> LATIN SMALL LETTER F
    u'g'        #  0x67 -> LATIN SMALL LETTER G
    u'h'        #  0x68 -> LATIN SMALL LETTER H
    u'i'        #  0x69 -> LATIN SMALL LETTER I
    u'j'        #  0x6A -> LATIN SMALL LETTER J
    u'k'        #  0x6B -> LATIN SMALL LETTER K
    u'l'        #  0x6C -> LATIN SMALL LETTER L
    u'm'        #  0x6D -> LATIN SMALL LETTER M
    u'n'        #  0x6E -> LATIN SMALL LETTER N
    u'o'        #  0x6F -> LATIN SMALL LETTER O
    u'p'        #  0x70 -> LATIN SMALL LETTER P
    u'q'        #  0x71 -> LATIN SMALL LETTER Q
    u'r'        #  0x72 -> LATIN SMALL LETTER R
    u's'        #  0x73 -> LATIN SMALL LETTER S
    u't'        #  0x74 -> LATIN SMALL LETTER T
    u'u'        #  0x75 -> LATIN SMALL LETTER U
    u'v'        #  0x76 -> LATIN SMALL LETTER V
    u'w'        #  0x77 -> LATIN SMALL LETTER W
    u'x'        #  0x78 -> LATIN SMALL LETTER X
    u'y'        #  0x79 -> LATIN SMALL LETTER Y
    u'z'        #  0x7A -> LATIN SMALL LETTER Z
    u'{'        #  0x7B -> LEFT CURLY BRACKET
    u'|'        #  0x7C -> VERTICAL LINE
    u'}'        #  0x7D -> RIGHT CURLY BRACKET
    u'~'        #  0x7E -> TILDE
    u'\x7f'     #  0x7F -> CONTROL CHARACTER
    u'\xc4'     #  0x80 -> LATIN CAPITAL LETTER A WITH DIAERESIS
    u'\xb9'     #  0x81 -> SUPERSCRIPT ONE
    u'\xb2'     #  0x82 -> SUPERSCRIPT TWO
    u'\xc9'     #  0x83 -> LATIN CAPITAL LETTER E WITH ACUTE
    u'\xb3'     #  0x84 -> SUPERSCRIPT THREE
    u'\xd6'     #  0x85 -> LATIN CAPITAL LETTER O WITH DIAERESIS
    u'\xdc'     #  0x86 -> LATIN CAPITAL LETTER U WITH DIAERESIS
    u'\u0385'   #  0x87 -> GREEK DIALYTIKA TONOS
    u'\xe0'     #  0x88 -> LATIN SMALL LETTER A WITH GRAVE
    u'\xe2'     #  0x89 -> LATIN SMALL LETTER A WITH CIRCUMFLEX
    u'\xe4'     #  0x8A -> LATIN SMALL LETTER A WITH DIAERESIS
    u'\u0384'   #  0x8B -> GREEK TONOS
    u'\xa8'     #  0x8C -> DIAERESIS
    u'\xe7'     #  0x8D -> LATIN SMALL LETTER C WITH CEDILLA
    u'\xe9'     #  0x8E -> LATIN SMALL LETTER E WITH ACUTE
    u'\xe8'     #  0x8F -> LATIN SMALL LETTER E WITH GRAVE
    u'\xea'     #  0x90 -> LATIN SMALL LETTER E WITH CIRCUMFLEX
    u'\xeb'     #  0x91 -> LATIN SMALL LETTER E WITH DIAERESIS
    u'\xa3'     #  0x92 -> POUND SIGN
    u'\u2122'   #  0x93 -> TRADE MARK SIGN
    u'\xee'     #  0x94 -> LATIN SMALL LETTER I WITH CIRCUMFLEX
    u'\xef'     #  0x95 -> LATIN SMALL LETTER I WITH DIAERESIS
    u'\u2022'   #  0x96 -> BULLET
    u'\xbd'     #  0x97 -> VULGAR FRACTION ONE HALF
    u'\u2030'   #  0x98 -> PER MILLE SIGN
    u'\xf4'     #  0x99 -> LATIN SMALL LETTER O WITH CIRCUMFLEX
    u'\xf6'     #  0x9A -> LATIN SMALL LETTER O WITH DIAERESIS
    u'\xa6'     #  0x9B -> BROKEN BAR
    u'\u20ac'   #  0x9C -> EURO SIGN # before Mac OS 9.2.2, was SOFT HYPHEN
    u'\xf9'     #  0x9D -> LATIN SMALL LETTER U WITH GRAVE
    u'\xfb'     #  0x9E -> LATIN SMALL LETTER U WITH CIRCUMFLEX
    u'\xfc'     #  0x9F -> LATIN SMALL LETTER U WITH DIAERESIS
    u'\u2020'   #  0xA0 -> DAGGER
    u'\u0393'   #  0xA1 -> GREEK CAPITAL LETTER GAMMA
    u'\u0394'   #  0xA2 -> GREEK CAPITAL LETTER DELTA
    u'\u0398'   #  0xA3 -> GREEK CAPITAL LETTER THETA
    u'\u039b'   #  0xA4 -> GREEK CAPITAL LETTER LAMDA
    u'\u039e'   #  0xA5 -> GREEK CAPITAL LETTER XI
    u'\u03a0'   #  0xA6 -> GREEK CAPITAL LETTER PI
    u'\xdf'     #  0xA7 -> LATIN SMALL LETTER SHARP S
    u'\xae'     #  0xA8 -> REGISTERED SIGN
    u'\xa9'     #  0xA9 -> COPYRIGHT SIGN
    u'\u03a3'   #  0xAA -> GREEK CAPITAL LETTER SIGMA
    u'\u03aa'   #  0xAB -> GREEK CAPITAL LETTER IOTA WITH DIALYTIKA
    u'\xa7'     #  0xAC -> SECTION SIGN
    u'\u2260'   #  0xAD -> NOT EQUAL TO
    u'\xb0'     #  0xAE -> DEGREE SIGN
    u'\xb7'     #  0xAF -> MIDDLE DOT
    u'\u0391'   #  0xB0 -> GREEK CAPITAL LETTER ALPHA
    u'\xb1'     #  0xB1 -> PLUS-MINUS SIGN
    u'\u2264'   #  0xB2 -> LESS-THAN OR EQUAL TO
    u'\u2265'   #  0xB3 -> GREATER-THAN OR EQUAL TO
    u'\xa5'     #  0xB4 -> YEN SIGN
    u'\u0392'   #  0xB5 -> GREEK CAPITAL LETTER BETA
    u'\u0395'   #  0xB6 -> GREEK CAPITAL LETTER EPSILON
    u'\u0396'   #  0xB7 -> GREEK CAPITAL LETTER ZETA
    u'\u0397'   #  0xB8 -> GREEK CAPITAL LETTER ETA
    u'\u0399'   #  0xB9 -> GREEK CAPITAL LETTER IOTA
    u'\u039a'   #  0xBA -> GREEK CAPITAL LETTER KAPPA
    u'\u039c'   #  0xBB -> GREEK CAPITAL LETTER MU
    u'\u03a6'   #  0xBC -> GREEK CAPITAL LETTER PHI
    u'\u03ab'   #  0xBD -> GREEK CAPITAL LETTER UPSILON WITH DIALYTIKA
    u'\u03a8'   #  0xBE -> GREEK CAPITAL LETTER PSI
    u'\u03a9'   #  0xBF -> GREEK CAPITAL LETTER OMEGA
    u'\u03ac'   #  0xC0 -> GREEK SMALL LETTER ALPHA WITH TONOS
    u'\u039d'   #  0xC1 -> GREEK CAPITAL LETTER NU
    u'\xac'     #  0xC2 -> NOT SIGN
    u'\u039f'   #  0xC3 -> GREEK CAPITAL LETTER OMICRON
    u'\u03a1'   #  0xC4 -> GREEK CAPITAL LETTER RHO
    u'\u2248'   #  0xC5 -> ALMOST EQUAL TO
    u'\u03a4'   #  0xC6 -> GREEK CAPITAL LETTER TAU
    u'\xab'     #  0xC7 -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'\xbb'     #  0xC8 -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'\u2026'   #  0xC9 -> HORIZONTAL ELLIPSIS
    u'\xa0'     #  0xCA -> NO-BREAK SPACE
    u'\u03a5'   #  0xCB -> GREEK CAPITAL LETTER UPSILON
    u'\u03a7'   #  0xCC -> GREEK CAPITAL LETTER CHI
    u'\u0386'   #  0xCD -> GREEK CAPITAL LETTER ALPHA WITH TONOS
    u'\u0388'   #  0xCE -> GREEK CAPITAL LETTER EPSILON WITH TONOS
    u'\u0153'   #  0xCF -> LATIN SMALL LIGATURE OE
    u'\u2013'   #  0xD0 -> EN DASH
    u'\u2015'   #  0xD1 -> HORIZONTAL BAR
    u'\u201c'   #  0xD2 -> LEFT DOUBLE QUOTATION MARK
    u'\u201d'   #  0xD3 -> RIGHT DOUBLE QUOTATION MARK
    u'\u2018'   #  0xD4 -> LEFT SINGLE QUOTATION MARK
    u'\u2019'   #  0xD5 -> RIGHT SINGLE QUOTATION MARK
    u'\xf7'     #  0xD6 -> DIVISION SIGN
    u'\u0389'   #  0xD7 -> GREEK CAPITAL LETTER ETA WITH TONOS
    u'\u038a'   #  0xD8 -> GREEK CAPITAL LETTER IOTA WITH TONOS
    u'\u038c'   #  0xD9 -> GREEK CAPITAL LETTER OMICRON WITH TONOS
    u'\u038e'   #  0xDA -> GREEK CAPITAL LETTER UPSILON WITH TONOS
    u'\u03ad'   #  0xDB -> GREEK SMALL LETTER EPSILON WITH TONOS
    u'\u03ae'   #  0xDC -> GREEK SMALL LETTER ETA WITH TONOS
    u'\u03af'   #  0xDD -> GREEK SMALL LETTER IOTA WITH TONOS
    u'\u03cc'   #  0xDE -> GREEK SMALL LETTER OMICRON WITH TONOS
    u'\u038f'   #  0xDF -> GREEK CAPITAL LETTER OMEGA WITH TONOS
    u'\u03cd'   #  0xE0 -> GREEK SMALL LETTER UPSILON WITH TONOS
    u'\u03b1'   #  0xE1 -> GREEK SMALL LETTER ALPHA
    u'\u03b2'   #  0xE2 -> GREEK SMALL LETTER BETA
    u'\u03c8'   #  0xE3 -> GREEK SMALL LETTER PSI
    u'\u03b4'   #  0xE4 -> GREEK SMALL LETTER DELTA
    u'\u03b5'   #  0xE5 -> GREEK SMALL LETTER EPSILON
    u'\u03c6'   #  0xE6 -> GREEK SMALL LETTER PHI
    u'\u03b3'   #  0xE7 -> GREEK SMALL LETTER GAMMA
    u'\u03b7'   #  0xE8 -> GREEK SMALL LETTER ETA
    u'\u03b9'   #  0xE9 -> GREEK SMALL LETTER IOTA
    u'\u03be'   #  0xEA -> GREEK SMALL LETTER XI
    u'\u03ba'   #  0xEB -> GREEK SMALL LETTER KAPPA
    u'\u03bb'   #  0xEC -> GREEK SMALL LETTER LAMDA
    u'\u03bc'   #  0xED -> GREEK SMALL LETTER MU
    u'\u03bd'   #  0xEE -> GREEK SMALL LETTER NU
    u'\u03bf'   #  0xEF -> GREEK SMALL LETTER OMICRON
    u'\u03c0'   #  0xF0 -> GREEK SMALL LETTER PI
    u'\u03ce'   #  0xF1 -> GREEK SMALL LETTER OMEGA WITH TONOS
    u'\u03c1'   #  0xF2 -> GREEK SMALL LETTER RHO
    u'\u03c3'   #  0xF3 -> GREEK SMALL LETTER SIGMA
    u'\u03c4'   #  0xF4 -> GREEK SMALL LETTER TAU
    u'\u03b8'   #  0xF5 -> GREEK SMALL LETTER THETA
    u'\u03c9'   #  0xF6 -> GREEK SMALL LETTER OMEGA
    u'\u03c2'   #  0xF7 -> GREEK SMALL LETTER FINAL SIGMA
    u'\u03c7'   #  0xF8 -> GREEK SMALL LETTER CHI
    u'\u03c5'   #  0xF9 -> GREEK SMALL LETTER UPSILON
    u'\u03b6'   #  0xFA -> GREEK SMALL LETTER ZETA
    u'\u03ca'   #  0xFB -> GREEK SMALL LETTER IOTA WITH DIALYTIKA
    u'\u03cb'   #  0xFC -> GREEK SMALL LETTER UPSILON WITH DIALYTIKA
    u'\u0390'   #  0xFD -> GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS
    u'\u03b0'   #  0xFE -> GREEK SMALL LETTER UPSILON WITH DIALYTIKA AND TONOS
    u'\xad'     #  0xFF -> SOFT HYPHEN # before Mac OS 9.2.2, was undefined
)

### Encoding Map

encoding_map = {
    0x0000: 0x00,       #  CONTROL CHARACTER
    0x0001: 0x01,       #  CONTROL CHARACTER
    0x0002: 0x02,       #  CONTROL CHARACTER
    0x0003: 0x03,       #  CONTROL CHARACTER
    0x0004: 0x04,       #  CONTROL CHARACTER
    0x0005: 0x05,       #  CONTROL CHARACTER
    0x0006: 0x06,       #  CONTROL CHARACTER
    0x0007: 0x07,       #  CONTROL CHARACTER
    0x0008: 0x08,       #  CONTROL CHARACTER
    0x0009: 0x09,       #  CONTROL CHARACTER
    0x000A: 0x0A,       #  CONTROL CHARACTER
    0x000B: 0x0B,       #  CONTROL CHARACTER
    0x000C: 0x0C,       #  CONTROL CHARACTER
    0x000D: 0x0D,       #  CONTROL CHARACTER
    0x000E: 0x0E,       #  CONTROL CHARACTER
    0x000F: 0x0F,       #  CONTROL CHARACTER
    0x0010: 0x10,       #  CONTROL CHARACTER
    0x0011: 0x11,       #  CONTROL CHARACTER
    0x0012: 0x12,       #  CONTROL CHARACTER
    0x0013: 0x13,       #  CONTROL CHARACTER
    0x0014: 0x14,       #  CONTROL CHARACTER
    0x0015: 0x15,       #  CONTROL CHARACTER
    0x0016: 0x16,       #  CONTROL CHARACTER
    0x0017: 0x17,       #  CONTROL CHARACTER
    0x0018: 0x18,       #  CONTROL CHARACTER
    0x0019: 0x19,       #  CONTROL CHARACTER
    0x001A: 0x1A,       #  CONTROL CHARACTER
    0x001B: 0x1B,       #  CONTROL CHARACTER
    0x001C: 0x1C,       #  CONTROL CHARACTER
    0x001D: 0x1D,       #  CONTROL CHARACTER
    0x001E: 0x1E,       #  CONTROL CHARACTER
    0x001F: 0x1F,       #  CONTROL CHARACTER
    0x0020: 0x20,       #  SPACE
    0x0021: 0x21,       #  EXCLAMATION MARK
    0x0022: 0x22,       #  QUOTATION MARK
    0x0023: 0x23,       #  NUMBER SIGN
    0x0024: 0x24,       #  DOLLAR SIGN
    0x0025: 0x25,       #  PERCENT SIGN
    0x0026: 0x26,       #  AMPERSAND
    0x0027: 0x27,       #  APOSTROPHE
    0x0028: 0x28,       #  LEFT PARENTHESIS
    0x0029: 0x29,       #  RIGHT PARENTHESIS
    0x002A: 0x2A,       #  ASTERISK
    0x002B: 0x2B,       #  PLUS SIGN
    0x002C: 0x2C,       #  COMMA
    0x002D: 0x2D,       #  HYPHEN-MINUS
    0x002E: 0x2E,       #  FULL STOP
    0x002F: 0x2F,       #  SOLIDUS
    0x0030: 0x30,       #  DIGIT ZERO
    0x0031: 0x31,       #  DIGIT ONE
    0x0032: 0x32,       #  DIGIT TWO
    0x0033: 0x33,       #  DIGIT THREE
    0x0034: 0x34,       #  DIGIT FOUR
    0x0035: 0x35,       #  DIGIT FIVE
    0x0036: 0x36,       #  DIGIT SIX
    0x0037: 0x37,       #  DIGIT SEVEN
    0x0038: 0x38,       #  DIGIT EIGHT
    0x0039: 0x39,       #  DIGIT NINE
    0x003A: 0x3A,       #  COLON
    0x003B: 0x3B,       #  SEMICOLON
    0x003C: 0x3C,       #  LESS-THAN SIGN
    0x003D: 0x3D,       #  EQUALS SIGN
    0x003E: 0x3E,       #  GREATER-THAN SIGN
    0x003F: 0x3F,       #  QUESTION MARK
    0x0040: 0x40,       #  COMMERCIAL AT
    0x0041: 0x41,       #  LATIN CAPITAL LETTER A
    0x0042: 0x42,       #  LATIN CAPITAL LETTER B
    0x0043: 0x43,       #  LATIN CAPITAL LETTER C
    0x0044: 0x44,       #  LATIN CAPITAL LETTER D
    0x0045: 0x45,       #  LATIN CAPITAL LETTER E
    0x0046: 0x46,       #  LATIN CAPITAL LETTER F
    0x0047: 0x47,       #  LATIN CAPITAL LETTER G
    0x0048: 0x48,       #  LATIN CAPITAL LETTER H
    0x0049: 0x49,       #  LATIN CAPITAL LETTER I
    0x004A: 0x4A,       #  LATIN CAPITAL LETTER J
    0x004B: 0x4B,       #  LATIN CAPITAL LETTER K
    0x004C: 0x4C,       #  LATIN CAPITAL LETTER L
    0x004D: 0x4D,       #  LATIN CAPITAL LETTER M
    0x004E: 0x4E,       #  LATIN CAPITAL LETTER N
    0x004F: 0x4F,       #  LATIN CAPITAL LETTER O
    0x0050: 0x50,       #  LATIN CAPITAL LETTER P
    0x0051: 0x51,       #  LATIN CAPITAL LETTER Q
    0x0052: 0x52,       #  LATIN CAPITAL LETTER R
    0x0053: 0x53,       #  LATIN CAPITAL LETTER S
    0x0054: 0x54,       #  LATIN CAPITAL LETTER T
    0x0055: 0x55,       #  LATIN CAPITAL LETTER U
    0x0056: 0x56,       #  LATIN CAPITAL LETTER V
    0x0057: 0x57,       #  LATIN CAPITAL LETTER W
    0x0058: 0x58,       #  LATIN CAPITAL LETTER X
    0x0059: 0x59,       #  LATIN CAPITAL LETTER Y
    0x005A: 0x5A,       #  LATIN CAPITAL LETTER Z
    0x005B: 0x5B,       #  LEFT SQUARE BRACKET
    0x005C: 0x5C,       #  REVERSE SOLIDUS
    0x005D: 0x5D,       #  RIGHT SQUARE BRACKET
    0x005E: 0x5E,       #  CIRCUMFLEX ACCENT
    0x005F: 0x5F,       #  LOW LINE
    0x0060: 0x60,       #  GRAVE ACCENT
    0x0061: 0x61,       #  LATIN SMALL LETTER A
    0x0062: 0x62,       #  LATIN SMALL LETTER B
    0x0063: 0x63,       #  LATIN SMALL LETTER C
    0x0064: 0x64,       #  LATIN SMALL LETTER D
    0x0065: 0x65,       #  LATIN SMALL LETTER E
    0x0066: 0x66,       #  LATIN SMALL LETTER F
    0x0067: 0x67,       #  LATIN SMALL LETTER G
    0x0068: 0x68,       #  LATIN SMALL LETTER H
    0x0069: 0x69,       #  LATIN SMALL LETTER I
    0x006A: 0x6A,       #  LATIN SMALL LETTER J
    0x006B: 0x6B,       #  LATIN SMALL LETTER K
    0x006C: 0x6C,       #  LATIN SMALL LETTER L
    0x006D: 0x6D,       #  LATIN SMALL LETTER M
    0x006E: 0x6E,       #  LATIN SMALL LETTER N
    0x006F: 0x6F,       #  LATIN SMALL LETTER O
    0x0070: 0x70,       #  LATIN SMALL LETTER P
    0x0071: 0x71,       #  LATIN SMALL LETTER Q
    0x0072: 0x72,       #  LATIN SMALL LETTER R
    0x0073: 0x73,       #  LATIN SMALL LETTER S
    0x0074: 0x74,       #  LATIN SMALL LETTER T
    0x0075: 0x75,       #  LATIN SMALL LETTER U
    0x0076: 0x76,       #  LATIN SMALL LETTER V
    0x0077: 0x77,       #  LATIN SMALL LETTER W
    0x0078: 0x78,       #  LATIN SMALL LETTER X
    0x0079: 0x79,       #  LATIN SMALL LETTER Y
    0x007A: 0x7A,       #  LATIN SMALL LETTER Z
    0x007B: 0x7B,       #  LEFT CURLY BRACKET
    0x007C: 0x7C,       #  VERTICAL LINE
    0x007D: 0x7D,       #  RIGHT CURLY BRACKET
    0x007E: 0x7E,       #  TILDE
    0x007F: 0x7F,       #  CONTROL CHARACTER
    0x00A0: 0xCA,       #  NO-BREAK SPACE
    0x00A3: 0x92,       #  POUND SIGN
    0x00A5: 0xB4,       #  YEN SIGN
    0x00A6: 0x9B,       #  BROKEN BAR
    0x00A7: 0xAC,       #  SECTION SIGN
    0x00A8: 0x8C,       #  DIAERESIS
    0x00A9: 0xA9,       #  COPYRIGHT SIGN
    0x00AB: 0xC7,       #  LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    0x00AC: 0xC2,       #  NOT SIGN
    0x00AD: 0xFF,       #  SOFT HYPHEN # before Mac OS 9.2.2, was undefined
    0x00AE: 0xA8,       #  REGISTERED SIGN
    0x00B0: 0xAE,       #  DEGREE SIGN
    0x00B1: 0xB1,       #  PLUS-MINUS SIGN
    0x00B2: 0x82,       #  SUPERSCRIPT TWO
    0x00B3: 0x84,       #  SUPERSCRIPT THREE
    0x00B7: 0xAF,       #  MIDDLE DOT
    0x00B9: 0x81,       #  SUPERSCRIPT ONE
    0x00BB: 0xC8,       #  RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    0x00BD: 0x97,       #  VULGAR FRACTION ONE HALF
    0x00C4: 0x80,       #  LATIN CAPITAL LETTER A WITH DIAERESIS
    0x00C9: 0x83,       #  LATIN CAPITAL LETTER E WITH ACUTE
    0x00D6: 0x85,       #  LATIN CAPITAL LETTER O WITH DIAERESIS
    0x00DC: 0x86,       #  LATIN CAPITAL LETTER U WITH DIAERESIS
    0x00DF: 0xA7,       #  LATIN SMALL LETTER SHARP S
    0x00E0: 0x88,       #  LATIN SMALL LETTER A WITH GRAVE
    0x00E2: 0x89,       #  LATIN SMALL LETTER A WITH CIRCUMFLEX
    0x00E4: 0x8A,       #  LATIN SMALL LETTER A WITH DIAERESIS
    0x00E7: 0x8D,       #  LATIN SMALL LETTER C WITH CEDILLA
    0x00E8: 0x8F,       #  LATIN SMALL LETTER E WITH GRAVE
    0x00E9: 0x8E,       #  LATIN SMALL LETTER E WITH ACUTE
    0x00EA: 0x90,       #  LATIN SMALL LETTER E WITH CIRCUMFLEX
    0x00EB: 0x91,       #  LATIN SMALL LETTER E WITH DIAERESIS
    0x00EE: 0x94,       #  LATIN SMALL LETTER I WITH CIRCUMFLEX
    0x00EF: 0x95,       #  LATIN SMALL LETTER I WITH DIAERESIS
    0x00F4: 0x99,       #  LATIN SMALL LETTER O WITH CIRCUMFLEX
    0x00F6: 0x9A,       #  LATIN SMALL LETTER O WITH DIAERESIS
    0x00F7: 0xD6,       #  DIVISION SIGN
    0x00F9: 0x9D,       #  LATIN SMALL LETTER U WITH GRAVE
    0x00FB: 0x9E,       #  LATIN SMALL LETTER U WITH CIRCUMFLEX
    0x00FC: 0x9F,       #  LATIN SMALL LETTER U WITH DIAERESIS
    0x0153: 0xCF,       #  LATIN SMALL LIGATURE OE
    0x0384: 0x8B,       #  GREEK TONOS
    0x0385: 0x87,       #  GREEK DIALYTIKA TONOS
    0x0386: 0xCD,       #  GREEK CAPITAL LETTER ALPHA WITH TONOS
    0x0388: 0xCE,       #  GREEK CAPITAL LETTER EPSILON WITH TONOS
    0x0389: 0xD7,       #  GREEK CAPITAL LETTER ETA WITH TONOS
    0x038A: 0xD8,       #  GREEK CAPITAL LETTER IOTA WITH TONOS
    0x038C: 0xD9,       #  GREEK CAPITAL LETTER OMICRON WITH TONOS
    0x038E: 0xDA,       #  GREEK CAPITAL LETTER UPSILON WITH TONOS
    0x038F: 0xDF,       #  GREEK CAPITAL LETTER OMEGA WITH TONOS
    0x0390: 0xFD,       #  GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS
    0x0391: 0xB0,       #  GREEK CAPITAL LETTER ALPHA
    0x0392: 0xB5,       #  GREEK CAPITAL LETTER BETA
    0x0393: 0xA1,       #  GREEK CAPITAL LETTER GAMMA
    0x0394: 0xA2,       #  GREEK CAPITAL LETTER DELTA
    0x0395: 0xB6,       #  GREEK CAPITAL LETTER EPSILON
    0x0396: 0xB7,       #  GREEK CAPITAL LETTER ZETA
    0x0397: 0xB8,       #  GREEK CAPITAL LETTER ETA
    0x0398: 0xA3,       #  GREEK CAPITAL LETTER THETA
    0x0399: 0xB9,       #  GREEK CAPITAL LETTER IOTA
    0x039A: 0xBA,       #  GREEK CAPITAL LETTER KAPPA
    0x039B: 0xA4,       #  GREEK CAPITAL LETTER LAMDA
    0x039C: 0xBB,       #  GREEK CAPITAL LETTER MU
    0x039D: 0xC1,       #  GREEK CAPITAL LETTER NU
    0x039E: 0xA5,       #  GREEK CAPITAL LETTER XI
    0x039F: 0xC3,       #  GREEK CAPITAL LETTER OMICRON
    0x03A0: 0xA6,       #  GREEK CAPITAL LETTER PI
    0x03A1: 0xC4,       #  GREEK CAPITAL LETTER RHO
    0x03A3: 0xAA,       #  GREEK CAPITAL LETTER SIGMA
    0x03A4: 0xC6,       #  GREEK CAPITAL LETTER TAU
    0x03A5: 0xCB,       #  GREEK CAPITAL LETTER UPSILON
    0x03A6: 0xBC,       #  GREEK CAPITAL LETTER PHI
    0x03A7: 0xCC,       #  GREEK CAPITAL LETTER CHI
    0x03A8: 0xBE,       #  GREEK CAPITAL LETTER PSI
    0x03A9: 0xBF,       #  GREEK CAPITAL LETTER OMEGA
    0x03AA: 0xAB,       #  GREEK CAPITAL LETTER IOTA WITH DIALYTIKA
    0x03AB: 0xBD,       #  GREEK CAPITAL LETTER UPSILON WITH DIALYTIKA
    0x03AC: 0xC0,       #  GREEK SMALL LETTER ALPHA WITH TONOS
    0x03AD: 0xDB,       #  GREEK SMALL LETTER EPSILON WITH TONOS
    0x03AE: 0xDC,       #  GREEK SMALL LETTER ETA WITH TONOS
    0x03AF: 0xDD,       #  GREEK SMALL LETTER IOTA WITH TONOS
    0x03B0: 0xFE,       #  GREEK SMALL LETTER UPSILON WITH DIALYTIKA AND TONOS
    0x03B1: 0xE1,       #  GREEK SMALL LETTER ALPHA
    0x03B2: 0xE2,       #  GREEK SMALL LETTER BETA
    0x03B3: 0xE7,       #  GREEK SMALL LETTER GAMMA
    0x03B4: 0xE4,       #  GREEK SMALL LETTER DELTA
    0x03B5: 0xE5,       #  GREEK SMALL LETTER EPSILON
    0x03B6: 0xFA,       #  GREEK SMALL LETTER ZETA
    0x03B7: 0xE8,       #  GREEK SMALL LETTER ETA
    0x03B8: 0xF5,       #  GREEK SMALL LETTER THETA
    0x03B9: 0xE9,       #  GREEK SMALL LETTER IOTA
    0x03BA: 0xEB,       #  GREEK SMALL LETTER KAPPA
    0x03BB: 0xEC,       #  GREEK SMALL LETTER LAMDA
    0x03BC: 0xED,       #  GREEK SMALL LETTER MU
    0x03BD: 0xEE,       #  GREEK SMALL LETTER NU
    0x03BE: 0xEA,       #  GREEK SMALL LETTER XI
    0x03BF: 0xEF,       #  GREEK SMALL LETTER OMICRON
    0x03C0: 0xF0,       #  GREEK SMALL LETTER PI
    0x03C1: 0xF2,       #  GREEK SMALL LETTER RHO
    0x03C2: 0xF7,       #  GREEK SMALL LETTER FINAL SIGMA
    0x03C3: 0xF3,       #  GREEK SMALL LETTER SIGMA
    0x03C4: 0xF4,       #  GREEK SMALL LETTER TAU
    0x03C5: 0xF9,       #  GREEK SMALL LETTER UPSILON
    0x03C6: 0xE6,       #  GREEK SMALL LETTER PHI
    0x03C7: 0xF8,       #  GREEK SMALL LETTER CHI
    0x03C8: 0xE3,       #  GREEK SMALL LETTER PSI
    0x03C9: 0xF6,       #  GREEK SMALL LETTER OMEGA
    0x03CA: 0xFB,       #  GREEK SMALL LETTER IOTA WITH DIALYTIKA
    0x03CB: 0xFC,       #  GREEK SMALL LETTER UPSILON WITH DIALYTIKA
    0x03CC: 0xDE,       #  GREEK SMALL LETTER OMICRON WITH TONOS
    0x03CD: 0xE0,       #  GREEK SMALL LETTER UPSILON WITH TONOS
    0x03CE: 0xF1,       #  GREEK SMALL LETTER OMEGA WITH TONOS
    0x2013: 0xD0,       #  EN DASH
    0x2015: 0xD1,       #  HORIZONTAL BAR
    0x2018: 0xD4,       #  LEFT SINGLE QUOTATION MARK
    0x2019: 0xD5,       #  RIGHT SINGLE QUOTATION MARK
    0x201C: 0xD2,       #  LEFT DOUBLE QUOTATION MARK
    0x201D: 0xD3,       #  RIGHT DOUBLE QUOTATION MARK
    0x2020: 0xA0,       #  DAGGER
    0x2022: 0x96,       #  BULLET
    0x2026: 0xC9,       #  HORIZONTAL ELLIPSIS
    0x2030: 0x98,       #  PER MILLE SIGN
    0x20AC: 0x9C,       #  EURO SIGN # before Mac OS 9.2.2, was SOFT HYPHEN
    0x2122: 0x93,       #  TRADE MARK SIGN
    0x2248: 0xC5,       #  ALMOST EQUAL TO
    0x2260: 0xAD,       #  NOT EQUAL TO
    0x2264: 0xB2,       #  LESS-THAN OR EQUAL TO
    0x2265: 0xB3,       #  GREATER-THAN OR EQUAL TO
}
