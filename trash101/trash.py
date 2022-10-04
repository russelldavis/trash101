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
        trashed_path = Path.home() / ".Trash" / path.name
        trashed_file = None
        # Resolve symlinks in the directory but not the file itself
        resolved_path = path.parent.resolve() / path.name

        if resolved_path.as_posix().startswith(trashed_path.parent.as_posix() + "/"):
            eprint(f"{path}: Already in trash")
            exitcode = 1
            continue

        def on_error():
            # It should still exist if there was an error, but to be safe,
            # don't remove what's in the trash if the source isn't still there.
            if path.exists():
                if trashed_file:
                    trashed_file.close()
                    trashed_path.unlink()
                else:
                    trashed_path.rmdir()
            exitcode = 1

        while True:
            try:
                if path.is_dir() and not path.is_symlink():
                    trashed_path.mkdir()
                else:
                    trashed_file = trashed_path.open("x")
            except FileExistsError:
                # almost same format as macOS uses, except this has zero-padding on the hour
                trashed_path = trashed_path.with_name(trashed_path.name + strftime(" %I.%M.%S %p"))
            else:
                break

        try:
            path.replace(trashed_path)
        except FileNotFoundError:
            eprint(f"{path}: No such file or directory")
            on_error()
            continue
        except PermissionError as err:
            eprint(err)
            on_error()
            continue
        except Exception:
            on_error()
            raise

        if trashed_file:
            trashed_file.close()

        setxattr(trashed_path, ORIG_PATH_XATTR, os.fsencode(resolved_path), symlink=True)
        # subprocess.check_call(["xattr", "-w", "-s", "trash101_orig_path", orig_path, trashed_path])

    sys.exit(exitcode)


if __name__ == "__main__":
    main()
