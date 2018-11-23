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
import zipfile

SOURCES=('vol01', 'vol02')

FOLDER_BUILD='build'
FOLDER_RELEASE='dist'
FOLDER_METAINFO='META-INF'
FOLDER_BOOKROOT='EPUB'
FILENAME_PACKAGEOPF='package.opf'
FILENAME_NAV='nav.xhtml'
FILEPATH_PACKAGEOPF=os.path.join(FOLDER_BOOKROOT, FILENAME_PACKAGEOPF)
FILEPATH_NAV=os.path.join(FOLDER_BOOKROOT, FILENAME_NAV)

CONSTSTR_MIMETYPE='application/epub+zip'
CONSTSTR_METAINFO="""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="{0}/{1}" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>""".format(FOLDER_BOOKROOT, FILENAME_PACKAGEOPF)

BOOK_ITEMS = []

def prepare_folders(build_dir):
    if not os.path.isdir(FOLDER_BUILD):
        os.makedirs(FOLDER_BUILD)
    if not os.path.isdir(FOLDER_RELEASE):
        os.makedirs(FOLDER_RELEASE)
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    os.makedirs(os.path.join(build_dir, FOLDER_METAINFO))
    os.makedirs(os.path.join(build_dir, FOLDER_BOOKROOT))

def prepare_mimetype(build_dir):
    outfn = os.path.join(build_dir, 'mimetype')
    with open(outfn, 'w') as fout:
        fout.write(CONSTSTR_MIMETYPE)

def prepare_metainfo(build_dir):
    outfn = os.path.join(build_dir, FOLDER_METAINFO, 'container.xml')
    with open(outfn, 'w') as fout:
        fout.write(CONSTSTR_METAINFO)

def prepare_fixtures(src_vol, build_dir):
    for root, dirs, files in os.walk(src_vol):
        dirs[:] = [d for d in dirs if (d != 'content')]
        for fname in files:
            path_src = os.path.join(root, fname)
            rel_pathname = os.path.relpath(path_src, src_vol)
            path_dest = os.path.join(build_dir, FOLDER_BOOKROOT, rel_pathname)
            dest_folder = os.path.dirname(path_dest)
            if not os.path.isdir(dest_folder):
                os.makedirs(dest_folder)
            shutil.copy(path_src, path_dest)

def generate_docs(build_dir):
    pass

def generate_toc(build_dir):
    pass

def generate_opf(build_dir):
    print(BOOK_ITEMS)

def package_book(build_dir, target_fn):
    base_fname = os.path.join(FOLDER_RELEASE, target_fn)
    zip_fname = base_fname + '.zip'
    epub_fname = os.path.join(FOLDER_RELEASE, target_fn + '.epub')

    if os.path.isfile(zip_fname):
        os.remove(zip_fname)
    if os.path.isfile(epub_fname):
        os.remove(epub_fname)

    shutil.make_archive(base_fname, 'zip', build_dir)
    os.rename(zip_fname, epub_fname)

def cook_book(vol):
    del BOOK_ITEMS[:]
    build_dir = os.path.join(FOLDER_BUILD, vol)
    prepare_folders(build_dir)
    prepare_mimetype(build_dir)
    prepare_metainfo(build_dir)
    prepare_fixtures(vol, build_dir)
    generate_docs(build_dir)
    generate_toc(build_dir)
    generate_opf(build_dir)
    package_book(build_dir, vol)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add elements to the repo')
    parser.add_argument('-v', '--volume', dest='volumes', choices=SOURCES, action='append',
                    help='select one or more volumes to build (default: %(default)s)')
    args = parser.parse_args()

    if (args.volumes is None) or (len(args.volumes) == 0):
        VOL_LIST = SOURCES
    else:
        VOL_LIST = args.volumes
    for vol in VOL_LIST:
        print(vol)
        if os.path.isdir(vol):
            cook_book(vol)
        else:
            raise Exception("Volmume<{0}> is not existed!".format(vol))
