#!/usr/bin/env python3
""" cookall
    tool to generate the EPUB files
"""
__author__ = "Jong-Liang Nieh"
__version__ = "0.0.1"

import os
import sys
import shutil
import argparse

SOURCES=('vol01', 'vol02')
BUILD_FOLDER='build'
DIST_FOLDER='dist'

def prepare_folders(build_dir):
    if not os.path.isdir(BUILD_FOLDER):
        os.makedirs(BUILD_FOLDER)
    if not os.path.isdir(DIST_FOLDER):
        os.makedirs(DIST_FOLDER)
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

def cook_book(vol):
    build_dir = os.path.join(BUILD_FOLDER, vol)
    target_fn = os.path.join(DIST_FOLDER, vol + '.epub')

    prepare_folders(build_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add elements to the repo')
    parser.add_argument('volumes', choices=SOURCES, nargs='+',
                    help='select one or more volumes to build (default: %(default)s)')
    args = parser.parse_args()

    for vol in args.volumes:
        if os.path.isdir(vol):
            cook_book(vol)
        else:
            raise Exception("Volmume<{0}> is not existed!".format(vol))
