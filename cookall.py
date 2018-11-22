#!/usr/bin/env python3
""" cookall
    tool to generate the EPUB files
"""
__author__ = "Jong-Liang Nieh"
__version__ = "0.0.1"

import os
import sys
import argparse

SOURCES=('vol01', 'vol02')

def cook_book(vol):
    pass

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
