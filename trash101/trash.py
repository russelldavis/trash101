#!/usr/bin/env venvx-auto
import os
import sys
from pathlib import Path
from time import strftime
from xattr import setxattr

def main():
    if len(sys.argv) <= 1:
        sys.stderr.write(
            f'usage: {os.path.basename(sys.argv[0])} file ...\n'
            '       move file(s) to Trash\n')
        sys.exit(64) # what rm does with no args

    exitcode = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        trash_path = Path.home() / ".Trash" / path.name

        while True:
            try:
                trash_file = open(trash_path, "x")
            except FileExistsError:
                # almost same format as macOS uses, except this has zero-padding on the hour
                trash_path = trash_path.with_name(trash_path.name + strftime(" %I.%M.%S %p"))
            else:
                break
        try:
            path.replace(trash_path)
        except FileNotFoundError:
            sys.stderr.write(f"{path}: No such file or directory\n")
            trash_path.unlink()
            exitcode = 1
        trash_file.close()

        # Resolve symlinks in the directory but not the file itself
        orig_path = path.parent.resolve() / path.name
        setxattr(trash_path, "trash101_orig_path", os.fsencode(orig_path), symlink=True)
        # subprocess.check_call(["xattr", "-w", "-s", "trash101_orig_path", orig_path, trash_path])

    sys.exit(exitcode)


if __name__ == "__main__":
    main()
