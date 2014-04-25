import os
__author__ = 'srd1g10'


def sorted_ls(path):
    """
    Sort by name
    """
    return list(sorted(os.listdir(path)))


def get_list_of_files(folder):
    """
    Returns list of files in folder with the folder prepended.
    """
    out = sorted_ls(folder)
    if out:
        list_of_files = [os.path.join(folder, f) for f in out]
        return list_of_files
    else:
        raise IOError("Error opening {0}, skipping.".format(folder))