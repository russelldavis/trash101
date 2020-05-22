#!/usr/bin/env venvx-auto
import os
import sys
from pathlib import Path
from xattr import getxattr, removexattr

ORIG_PATH_XATTR = "trash101_orig_path"

def main():
    if len(sys.argv) <= 1:
        sys.stderr.write(
            f'usage: {os.path.basename(sys.argv[0])} file ...\n'
            '       put back file(s) from Trash\n')
        sys.exit(64) # what rm does with no args

    exitcode = 0
    for arg in sys.argv[1:]:
        trash_path = Path(arg)

        try:
            orig_path = getxattr(trash_path, ORIG_PATH_XATTR, symlink=True)
        except IOError:
            # getxattr doesn't distinguish failure modes
            if trash_path.exists():
                sys.stderr.write(f"{trash_path}: could not restore: original path not available\n")
            else:
                sys.stderr.write(f"{trash_path}: No such file or directory\n")
            exitcode = 1
            continue

        orig_path = os.fsdecode(orig_path)
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
