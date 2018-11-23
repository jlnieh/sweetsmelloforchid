#!/usr/bin/env python3
""" cookall
    tool to generate the EPUB files
"""
__author__ = "Jong-Liang Nieh"
__version__ = "0.0.1"

import os
import sys
import shutil
import datetime
import argparse
import zipfile

SOURCES=('vol01', 'vol02')

FOLDER_BUILD='build'
FOLDER_RELEASE='dist'
FOLDER_METAINFO='META-INF'
FOLDER_BOOKROOT='EPUB'
FOLDER_CONTENTS='contents'
FOLDER_TEMPLATES='templates'

FILENAME_CONTENT_TEMPLATE='content.xhtml'
FILENAME_PACKAGEOPF='package.opf'
# FILENAME_NAV='nav.xhtml'
# FILEPATH_NAV=os.path.join(FOLDER_BOOKROOT, FILENAME_NAV)

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
        dirs[:] = [d for d in dirs if d not in (FOLDER_CONTENTS, FOLDER_TEMPLATES)]
        for fname in files:
            path_src = os.path.join(root, fname)
            rel_pathname = os.path.relpath(path_src, src_vol)
            path_dest = os.path.join(build_dir, FOLDER_BOOKROOT, rel_pathname)
            dest_folder = os.path.dirname(path_dest)
            if not os.path.isdir(dest_folder):
                os.makedirs(dest_folder)
            shutil.copy(path_src, path_dest)

PATTERN_PAGETITLE='<title></title>'
def convert_doc(fname_src, fname_template, build_dir, fname_base):
    fname_dest = os.path.join(build_dir, FOLDER_BOOKROOT, fname_base)

    str_pagetitle = ''
    with open(fname_src, 'r', encoding='utf-8') as fin:
        for line in fin:
            if line.startswith('## '):
                str_pagetitle = line[3:].strip()


    with open(fname_template, 'r', encoding='utf-8') as fin, open(fname_dest, 'w', encoding='utf-8') as fout:
        for line in fin:
            if line.find(PATTERN_PAGETITLE) >= 0:
                line = line.replace(PATTERN_PAGETITLE, '<title>' + str_pagetitle + '</title>')
            fout.write(line)

def generate_docs(src_vol, build_dir):
    path_src_root = os.path.join(src_vol, FOLDER_CONTENTS)
    fname_template = os.path.join(src_vol, FOLDER_TEMPLATES, FILENAME_CONTENT_TEMPLATE)

    for root, dirs, files in os.walk(path_src_root):
        for fname in files:
            (fbase, fext) = os.path.splitext(fname)
            if '.md' != fext:
                continue
            BOOK_ITEMS.append(fbase)
            convert_doc(os.path.join(root, fname), fname_template, build_dir, fbase + '.xhtml')

    BOOK_ITEMS.sort()

def generate_toc(src_vol, build_dir):
    pass

PATTERN_MODIFIEDDATETIME = '<meta property="dcterms:modified"></meta>'
def generate_opf(src_vol, build_dir):
    str_now = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec='seconds')
    str_items = ''
    str_itemref = ''
    for item in BOOK_ITEMS:
        str_items += '        <item href="{0}.xhtml" id="{0}" media-type="application/xhtml+xml"/>\n'.format(item)
        str_itemref += '        <itemref idref="{0}"/>\n'.format(item)

    fname_src = os.path.join(src_vol, FOLDER_TEMPLATES, FILENAME_PACKAGEOPF)
    fname_dest= os.path.join(build_dir, FOLDER_BOOKROOT, FILENAME_PACKAGEOPF)
    with open(fname_src, 'r', encoding='utf-8') as fin, open(fname_dest, 'w', encoding='utf-8') as fout:
        for line in fin:
            if line.find(PATTERN_MODIFIEDDATETIME) >= 0:
                line = line.replace(PATTERN_MODIFIEDDATETIME, '<meta property="dcterms:modified">' + str_now + '</meta>')
            elif line.find('</manifest>') >= 0:
                fout.write(str_items)
            elif line.find('</spine>') >= 0:
                fout.write(str_itemref)
            fout.write(line)

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
    return epub_fname

def verify_book(epub_fname):
    pass

def cook_book(vol):
    del BOOK_ITEMS[:]
    build_dir = os.path.join(FOLDER_BUILD, vol)
    prepare_folders(build_dir)
    prepare_mimetype(build_dir)
    prepare_metainfo(build_dir)
    prepare_fixtures(vol, build_dir)
    generate_docs(vol, build_dir)
    generate_toc(vol, build_dir)
    generate_opf(vol, build_dir)
    epub_fname = package_book(build_dir, vol)
    verify_book(epub_fname)

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
        if os.path.isdir(vol):
            cook_book(vol)
        else:
            raise Exception("Volmume<{0}> is not existed!".format(vol))
