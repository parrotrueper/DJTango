from djtango.qt_compat import QColor


def track_type_key_from_row(row):
    if row < 0:
        raise ValueError("No track type selected")
    return row + 1


def apply_track_type_color(TYPE, row, color):
    key = track_type_key_from_row(row)
    if key not in TYPE:
        raise KeyError(f"Track type key not found: {key}")
    type_entry = TYPE[key]
    extra = type_entry[6:] if len(type_entry) > 6 else ()
    TYPE[key] = (
        type_entry[0],
        type_entry[1],
        color.red(),
        color.green(),
        color.blue(),
        color.alpha(),
    ) + extra
    return TYPE[key]


def get_contrast_color(color):
    luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue())
    return QColor(0, 0, 0) if luminance > 186 else QColor(255, 255, 255)


def get_type_font_color(type_entry):
    if len(type_entry) > 6 and type_entry[6] is not None:
        return QColor(type_entry[6], type_entry[7], type_entry[8], type_entry[9])
    return None


def set_type_font_color(type_entry, color):
    if len(type_entry) > 6:
        return type_entry[:6] + (color.red(), color.green(), color.blue(), color.alpha())
    return type_entry + (color.red(), color.green(), color.blue(), color.alpha())
