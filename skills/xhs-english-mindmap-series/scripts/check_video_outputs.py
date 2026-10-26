#!/usr/bin/env python3
"""Compatibility entry: video + exact English text subset, per question ID."""
import sys
from check_release import main as release_main

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_video_outputs.py TOPIC_FOLDER")
        return 2
    return release_main([sys.argv[1], "--scope", "video"])

if __name__ == "__main__":
    raise SystemExit(main())
