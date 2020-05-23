#!/usr/bin/env venvx-auto
import os
import sys
from pathlib import Path
from xattr import getxattr, removexattr
from . import ORIG_PATH_XATTR, TRASH_DIR

ds_file = None

def get_ds_store_orig_path(trash_path):
    if trash_path.parent != TRASH_DIR:
        return None

    global ds_file
    if ds_file is None:
        from ds_store import DSStore
        # Closed implicitly when the process exits
        ds_file = DSStore.open(str(TRASH_DIR / '.DS_Store'), 'r')

    ds_entry = ds_file[trash_path.name]
    print([x for x in ds_file])
    try:
        return ds_entry[b'ptbL'] + ds_entry[b'ptbN']
    except KeyError:
        return None

def get_orig_path(trash_path):
    try:
        orig_path = getxattr(trash_path, ORIG_PATH_XATTR, symlink=True)
    except IOError:
        # getxattr doesn't distinguish failure modes
        if not trash_path.exists():
            sys.stderr.write(f"{trash_path}: No such file or directory\n")
            return None

        orig_path = get_ds_store_orig_path(trash_path)
        if orig_path is None:
            sys.stderr.write(
                f"{trash_path}: could not restore: original path not available\n")
        return orig_path
    return os.fsdecode(orig_path)

def main():
    if len(sys.argv) <= 1:
        sys.stderr.write(
            f'usage: {os.path.basename(sys.argv[0])} file ...\n'
            '       put back file(s) from Trash\n')
        sys.exit(64) # what rm does with no args

    exitcode = 0
    for arg in sys.argv[1:]:
        trash_path = Path(arg)
        orig_path = get_orig_path(trash_path)
        if orig_path is None:
            exitcode = 1
            continue

        try:
            orig_file = open(orig_path, "x")
        except FileExistsError:
            sys.stderr.write(f"overwrite {orig_path}? (y/n [n])\n")
            res = input()
            if res[0] != "y":
                sys.stderr.write(f"not overwritten")
                exitcode = 1
                continue
            orig_file = None

        trash_path.replace(orig_path)
        sys.stderr.write(f"{orig_path}\n")
        removexattr(orig_path, ORIG_PATH_XATTR, symlink=True)
        if orig_file:
            orig_file.close()

    sys.exit(exitcode)

if __name__ == "__main__":
    main()
