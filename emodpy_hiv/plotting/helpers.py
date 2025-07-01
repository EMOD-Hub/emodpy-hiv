import os


def get_filenames(dir_or_filename: str,
                  file_prefix: str = None,
                  file_extension: str = None):
    """
    Get a list of filenames from a directory or a single file.
    If a directory is provided, it will list all files in that directory.
    If a file is provided, it will check if it matches the prefix and extension.

    Args:
        dir_or_filename (string, required):
            Directory or filename to search.
        file_prefix (string, optional)
            Prefix to filter files by.
        file_extension (string, optional):
            Extension to filter files by.
    Returns:
        List of filenames that match the criteria.
    """

    dir_filenames = []

    # Check if the input is a directory or a file
    if os.path.isdir(dir_or_filename):
        # If it's a directory, list all files in the directory
        for base_fn in os.listdir(dir_or_filename):
            fn = os.path.join(dir_or_filename, base_fn)
            if not os.path.isfile(fn):
                continue
            if file_prefix and not base_fn.startswith(file_prefix):
                continue
            if file_extension and not base_fn.endswith(file_extension):
                continue
            dir_filenames.append(fn)

    elif os.path.isfile(dir_or_filename):
        if (file_prefix and dir_or_filename.startswith(file_prefix)) or \
           (file_extension and dir_or_filename.endswith(file_extension)):
            dir_filenames.append(dir_or_filename)
        elif file_prefix:
            raise ValueError(f"'{dir_or_filename}' does not start with the specified prefix '{file_prefix}'.")
        elif file_extension:
            raise ValueError(f"'{dir_or_filename}' does not end with the specified extension '{file_extension}'.")
        else:
            dir_filenames.append(dir_or_filename)

    else:
        raise ValueError(f"'{dir_or_filename}' is neither a valid directory nor a file.")

    dir_filenames = sorted(dir_filenames)
    return dir_filenames
