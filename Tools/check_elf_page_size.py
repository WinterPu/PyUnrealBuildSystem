#!/usr/bin/env python3

# Released into the public domain. No attribution required.

__doc__ = """
This script reads an ELF file and prints the page size of the first LOAD segment.
"""


# third_party
# to install, run `pip install pyelftools`
from elftools.elf.elffile import ELFFile

import os
import sys
import argparse

def get_page_size(elf_file_path):
  with open(elf_file_path, 'rb') as file:
    elf = ELFFile(file)
    for segment in elf.iter_segments():
      if segment.header.p_type == 'PT_LOAD':
        print(f"Page Size of {elf_file_path}: {segment.header.p_align}")
        break

def main():
    parser = argparse.ArgumentParser(description="Process ELF files or directories containing .so files.")
    parser.add_argument('-path', type=str, help='Path to a .so file or a directory containing .so files.')

    args = parser.parse_args()
    path = args.path

    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith('.so'):
                elf_file = os.path.join(path, filename)
                get_page_size(elf_file)
    elif os.path.isfile(path) and path.endswith('.so'):
        get_page_size(path)
    else:
        print(f"Invalid path: {path}. It should be a .so file or a directory containing .so files.")
        sys.exit(1)

if __name__ == '__main__':
    main()