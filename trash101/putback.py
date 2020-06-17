#!/usr/bin/env venvx-auto
import os
import sys
from pathlib import Path
from xattr import getxattr, removexattr
from . import ORIG_PATH_XATTR, eprint

def main():
    if len(sys.argv) <= 1:
        eprint(
            f'usage: {os.path.basename(sys.argv[0])} file ...\n'
            f'       put back file(s) from Trash'
        )
        sys.exit(64) # what rm does with no args

    exitcode = 0
    for arg in sys.argv[1:]:
        trash_path = Path(arg)

        try:
            orig_path = getxattr(trash_path, ORIG_PATH_XATTR, symlink=True)
        except IOError:
            # getxattr doesn't distinguish failure modes
            if trash_path.exists():
                eprint(
                    f"{trash_path}: trashed file does not contain original path "
                    f"metadata; not restoring"
                )
            else:
                eprint(f"{trash_path}: No such file or directory")
            exitcode = 1
            continue

        orig_path = Path(os.fsdecode(orig_path))
        orig_file = None
        try:
            if trash_path.is_dir() and not trash_path.is_symlink():
                orig_path.mkdir()
            else:
                orig_file = orig_path.open("x")
        except FileExistsError:
            if orig_path.is_dir() and not orig_path.is_symlink():
                eprint(f"{orig_path}: already exists as a dir; not restoring")
                exitcode = 1
                continue
            eprint(f"overwrite {orig_path}? (y/n [n])")
            res = input()
            if res[0] != "y":
                eprint("not overwritten")
                exitcode = 1
                continue

        trash_path.replace(orig_path)
        eprint(f"{orig_path}\n")
        removexattr(orig_path, ORIG_PATH_XATTR, symlink=True)
        if orig_file:
            orig_file.close()

    sys.exit(exitcode)

if __name__ == "__main__":
    main()
