#!/usr/bin/env venvx-auto
import os
import sys
from pathlib import Path
from time import strftime
from xattr import setxattr
from . import ORIG_PATH_XATTR, eprint

def main():
    if len(sys.argv) <= 1:
        eprint(
            f'usage: {os.path.basename(sys.argv[0])} file ...\n'
            f'       move file(s) to Trash'
        )
        sys.exit(64) # what rm does with no args

    exitcode = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        trash_path = Path.home() / ".Trash" / path.name
        trash_file = None

        while True:
            try:
                if path.is_dir() and not path.is_symlink():
                    trash_path.mkdir()
                else:
                    trash_file = trash_path.open("x")
            except FileExistsError:
                # almost same format as macOS uses, except this has zero-padding on the hour
                trash_path = trash_path.with_name(trash_path.name + strftime(" %I.%M.%S %p"))
            else:
                break

        try:
            path.replace(trash_path)
        except FileNotFoundError:
            eprint(f"{path}: No such file or directory")
            if trash_file:
                trash_file.close()
                trash_path.unlink()
            else:
                trash_path.rmdir()
            exitcode = 1
            continue

        if trash_file:
            trash_file.close()

        # Resolve symlinks in the directory but not the file itself
        orig_path = path.parent.resolve() / path.name
        try:
            setxattr(trash_path, ORIG_PATH_XATTR, os.fsencode(orig_path), symlink=True)
            # subprocess.check_call(["xattr", "-w", "-s", "trash101_orig_path", orig_path, trash_path])
        except OSError:
            # Some filesystems don't support xattrs
            pass

    sys.exit(exitcode)


if __name__ == "__main__":
    main()
