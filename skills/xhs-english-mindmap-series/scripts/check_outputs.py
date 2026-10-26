#!/usr/bin/env python3
"""Compatibility entry: full release by default; --cover-only is a cover subset."""
import sys
from check_release import HEIGHT, WIDTH, main as release_main, size_of

def main():
    args = sys.argv[1:]
    if "--cover-only" in args:
        args[args.index("--cover-only"):args.index("--cover-only") + 1] = ["--scope", "cover"]
    return release_main(args)

if __name__ == "__main__":
    raise SystemExit(main())
