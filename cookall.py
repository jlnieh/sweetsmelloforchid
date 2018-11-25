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
FILENAME_NAV='nav.xhtml'

CONSTSTR_MIMETYPE='application/epub+zip'
CONSTSTR_METAINFO="""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="{0}/{1}" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>""".format(FOLDER_BOOKROOT, FILENAME_PACKAGEOPF)

BOOK_ITEMS = []
TOC_ITEMS = []

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


def splitSubHeader(line):
    subHeaderPos = line.find('    ')
    if (subHeaderPos > 0):
        return (line[:subHeaderPos], line[subHeaderPos+4:])
    else:
        return (line, '')

PATTERN_PAGETITLE='<!--PAGE_TITLE-->'
PATTERN_PAGEBODY='<!--PAGE_BODY-->'
def convert_doc(fname_src, fname_template, build_dir, fname_base):
    fname_dest = os.path.join(build_dir, FOLDER_BOOKROOT, fname_base)

    pageTitle = ''
    strContent = ''
    pg_id = fname_base[0:3]
    h2_id = 0
    h4_id = 0
    curPara = []
    with open(fname_src, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.rstrip()
            if len(line) == 0:
                if(len(curPara)>0):
                    strContent += '</{0}>\n'.format(curPara.pop())
            elif line.startswith('## '):
                (pageTitle, pageSubTitle) = splitSubHeader(line[3:])
                h2_id += 1
                localHeaderId = '{0}h2{1:02}'.format(pg_id, h2_id)
                TOC_ITEMS.append((fname_base, localHeaderId, 2, pageTitle))
                h4_id = 0

                while(len(curPara)>0):
                    strContent += '</{0}>\n'.format(curPara.pop())
                strContent += """<header><h2 id="{0}">{1}</h2>{2}</header>\n""".format(localHeaderId, pageTitle, pageSubTitle)
            elif line.startswith('#### '):
                (poemTitle, posmDate) = splitSubHeader(line[5:])
                h4_id += 1
                localHeaderId = '{0}h4{1:02}{2:03}'.format(pg_id, h2_id, h4_id)
                TOC_ITEMS.append((fname_base, localHeaderId, 4, poemTitle))

                while(len(curPara)>0):
                    strContent += '</{0}>\n'.format(curPara.pop())
                strContent += """<article id="{0}"><header><h3 class="poem-title">{1}</h3><p class="poem-date">{2}</p></header>""".format(localHeaderId, poemTitle, posmDate)
                curPara.append('article')
            elif line.startswith('##### '):
                poemTitle = line[6:]

                if(len(curPara)>1):
                    strContent += '</{0}>\n'.format(curPara.pop())
                strContent += '<h4>{0}</h4>'.format(poemTitle)
            elif line.startswith('> '):
                if(len(curPara)<2):
                    strContent += '<p class="poem">'
                    curPara.append('p')
                strContent += line[2:]
            else:
                if(len(curPara)<1):
                    strContent += '<p>'
                    curPara.append('p')
                strContent += line
    while(len(curPara)>0):
        strContent += '</{0}>\n'.format(curPara.pop())

    with open(fname_template, 'r', encoding='utf-8') as fin, open(fname_dest, 'w', encoding='utf-8') as fout:
        for line in fin:
            if line.find(PATTERN_PAGETITLE) >= 0:
                line = line.replace(PATTERN_PAGETITLE, pageTitle)
            elif line.find(PATTERN_PAGEBODY) >= 0:
                line = line.replace(PATTERN_PAGEBODY, strContent)
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

PATTERN_TOC = '<!--TOC-->'
def generate_toc(src_vol, build_dir):
    str_items = ''
    cur_lvl = 0
    for item in TOC_ITEMS:
        if item[2] > cur_lvl:
            if cur_lvl > 0:
                indentSpace = '\n' + ' ' * (cur_lvl * 2 + 12)
                str_items += indentSpace + '<ol>'
        elif item[2] < cur_lvl:
            indentSpace = '\n' + ' ' * (item[2] * 2 + 12)
            str_items += '</li>' + indentSpace + '</ol>'
        else:
            str_items += '</li>'
        indentSpace = '\n' + ' ' * (item[2] * 2 + 12)
        str_items += indentSpace + '<li><a href="{0}#{1}">{2}</a>'.format(item[0], item[1], item[3])
        cur_lvl = item[2]
    if 2 == cur_lvl:
        str_items += '</li>'
    else:   # 4 == cur_lvl
        indentSpace = '\n' +  ' ' * 16
        str_items += '</li>' + indentSpace  + '</ol></li>'

    fname_src = os.path.join(src_vol, FOLDER_TEMPLATES, FILENAME_NAV)
    fname_dest= os.path.join(build_dir, FOLDER_BOOKROOT, FILENAME_NAV)
    with open(fname_src, 'r', encoding='utf-8') as fin, open(fname_dest, 'w', encoding='utf-8') as fout:
        for line in fin:
            if line.find(PATTERN_TOC) >= 0:
                line = line.replace(PATTERN_TOC, str_items)
            fout.write(line)

PATTERN_MODIFIEDDATETIME = '<!--DATE_MODIFIED-->'
PATTERN_MANIFEST = '<!--LIST_MANIFEST-->'
PATTERN_SPINE = '<!--LIST_SPINE-->'
def generate_opf(src_vol, build_dir):
    str_now = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec='seconds')
    str_items = ''
    str_itemref = ''
    for item in BOOK_ITEMS:
        if '' == str_items:
            lineHeader = ''
        else:
            lineHeader = '\n' + ' ' * 8
        str_items += lineHeader + '<item href="{0}.xhtml" id="{0}" media-type="application/xhtml+xml"/>'.format(item)
        str_itemref += lineHeader + '<itemref idref="{0}"/>'.format(item)

    fname_src = os.path.join(src_vol, FOLDER_TEMPLATES, FILENAME_PACKAGEOPF)
    fname_dest= os.path.join(build_dir, FOLDER_BOOKROOT, FILENAME_PACKAGEOPF)
    with open(fname_src, 'r', encoding='utf-8') as fin, open(fname_dest, 'w', encoding='utf-8') as fout:
        for line in fin:
            if line.find(PATTERN_MODIFIEDDATETIME) >= 0:
                line = line.replace(PATTERN_MODIFIEDDATETIME, str_now)
            elif line.find(PATTERN_MANIFEST) >= 0:
                line = line.replace(PATTERN_MANIFEST, str_items)
            elif line.find(PATTERN_SPINE) >= 0:
                line = line.replace(PATTERN_SPINE, str_itemref)
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
    del TOC_ITEMS[:]

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
