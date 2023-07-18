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

    path_counts = {}
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
            if trashed_file:
                trashed_file.close()
                # This should never happen (the move operation should be atomic), but we want to
                # make sure we don't delete data from the trash if there was an error *after* the
                # file got moved.
                if trashed_path.stat(follow_symlinks=False).st_size != 0:
                    raise RuntimeError("File size in trash should be 0 after error")
                trashed_path.unlink()
                removed = True
            else:
                trashed_path.rmdir()
                if trashed_path in path_counts:
                    path_counts[trashed_path] -= 1

            if trashed_path in path_counts:
                path_counts[trashed_path] -= 1

            exitcode = 1

        while True:
            try:
                if path.is_dir() and not path.is_symlink():
                    trashed_path.mkdir()
                else:
                    trashed_file = trashed_path.open("x")
            except FileExistsError:
                # Almost same format as macOS uses, except this has zero-padding on the hour.
                trashed_path = trashed_path.with_name(trashed_path.name + strftime(" %I.%M.%S %p"))
                # We also add this extra check if it already ends w/ this suffix -- otherwise,
                # if you delete a bunch of files with the same name during the same second, you'll
                # get the same timestamp appended a bunch of times, eventually resulting in a
                # "File name too long" error (in Finder that's hard to do, which I guess is why
                # Finder doesn't do this, but in the CLI it's easy, so we do).
                #
                # Only checking for this in memory, because it's easier and more efficient, and
                # it's less likely to happen across multiple process invocations.
                path_count = path_counts.get(trashed_path, 0)
                path_counts[trashed_path] = path_count + 1
                if path_count > 0:
                    trashed_path = trashed_path.with_name(trashed_path.name + f" ({path_count})")
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
