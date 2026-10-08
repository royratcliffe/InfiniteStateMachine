import os

STRING_PREFIX = "(string)"
SECTION_PREFIX = "(* --- "
SECTION_SUFFIX = " --- *)"

# The order in which sections should appear in the output .st file.
# Interface sections should appear before Implementation sections.
# Everything else will appear after the listed sections.
SECTION_ORDERING = ["Interface", "Implementation"]


def unwrap_string(value):
    """Strip the CODESYS "(string)" type-tag prefix used on raw string values."""
    if isinstance(value, str) and value.startswith(STRING_PREFIX):
        return value[len(STRING_PREFIX) :]
    return value


def object_name(data, fallback):
    """Return the object's declared name (payload.meta.Graph.@Value.Name), or fallback."""
    try:
        name = data["payload"]["meta"]["Graph"]["@Value"]["Name"]
    except (KeyError, TypeError):
        return fallback
    name = unwrap_string(name)
    # If the name is valid, prepend it with the fallback path.
    return f"{fallback}-{name}" if isinstance(name, str) and name else fallback


def fallback_from_path(path):
    """Return the fallback path derived from the given path."""
    # Construct the object name using the fallback derived from the file path.
    # The fallback derives from the file path by taking all parts except the first and last,
    # the last part, and joining them with forward slash or backslash depending on the OS.
    return os.sep.join([part.rsplit("_", 1)[0] for part in path.parts[0:-1]])
