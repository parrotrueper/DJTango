# Minimal mutagen.id3 package initializer to expose the symbols required by the vendored mutagen wrappers.
from ._file import ID3, ID3FileType, delete
from ._util import error, BitPaddedInt
from ._specs import Encoding, PictureType

__all__ = [
    "ID3",
    "ID3FileType",
    "delete",
    "error",
    "BitPaddedInt",
    "Encoding",
    "PictureType",
]
