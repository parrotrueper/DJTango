# Compatibility shim for tests and legacy imports.
# Some test modules import ttvttm.TTVTTM even though the main application module is ttvttm.ttvttm.
from . import ttvttm as _ttvttm
from .ui_utils import (
    apply_track_type_color,
    get_contrast_color,
    track_type_key_from_row,
)

__all__ = [
    name for name in dir(_ttvttm) if not name.startswith("__")
] + [
    "apply_track_type_color",
    "get_contrast_color",
    "track_type_key_from_row",
]

globals().update({name: getattr(_ttvttm, name) for name in dir(_ttvttm) if not name.startswith("__")})
globals().update({
    "apply_track_type_color": apply_track_type_color,
    "get_contrast_color": get_contrast_color,
    "track_type_key_from_row": track_type_key_from_row,
})


def __getattr__(name: str):
    if name in __all__:
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return __all__
