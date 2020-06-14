import sys

ORIG_PATH_XATTR = "trash101_orig_path"

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
