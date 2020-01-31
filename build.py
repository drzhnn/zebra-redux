import fileinput
import os
import re
import shutil
import sys
import time
import winsound
from PIL import Image


PROJECT_NAME = 'zebrahz-redux'
RELEASE = False
FLUSH_METADATA = False

NOW = time.strftime('%Y-%m%d-%H%M')
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

BUILD_PATH = os.path.join(BASE_DIR, 'build')
REDUX_PATH = os.path.join(BUILD_PATH, 'Redux')
SCRIPTS_PATH = os.path.join(REDUX_PATH, 'Scripts')
IMAGES_PATH = os.path.join(REDUX_PATH, 'Images')

GARBAGE = ['(?!#FX.)(?!#AmCmp.)[#].*', '^[ \t]+', '[ \t]+$', '  +', '^\n']


def flush_metadata(filename):

    tmp_name = filename + '.tiff'

    def to_tmp():
        with Image.open(filename) as _:
            _.save(tmp_name)

    def to_png():
        with Image.open(tmp_name) as _:
            _.save(filename)

    to_tmp()
    to_png()
    os.remove(tmp_name)


def build():
    try:
        shutil.rmtree(REDUX_PATH)
    except Exception as e:
        print(e)

    try:
        os.makedirs(REDUX_PATH)
        os.makedirs(SCRIPTS_PATH)
    except Exception as e:
        print(e)
    finally:
        shutil.copyfile(os.path.join(BASE_DIR, 'scripts', 'ZebraHZ.txt'), os.path.join(SCRIPTS_PATH, 'ZebraHZ.txt'))
        shutil.copyfile(os.path.join(BASE_DIR, 'scripts', 'Zebra2.txt'), os.path.join(SCRIPTS_PATH, 'Zebra2.txt'))
        shutil.copytree(os.path.join(BASE_DIR, 'images'), IMAGES_PATH)

    scripts = [os.path.join(SCRIPTS_PATH, 'ZebraHZ.txt'), os.path.join(SCRIPTS_PATH, 'Zebra2.txt')]

    for s in scripts:

        for line in fileinput.FileInput(s, inplace=1):
            for i, _ in enumerate(GARBAGE):
                line = re.sub(GARBAGE[i], '', line)

            print(line, end='')

        if FLUSH_METADATA:
            for root, dirs, files in os.walk(IMAGES_PATH):
                for file in files:
                    fname = os.path.join(root, file)
                    try:
                        flush_metadata(fname)
                    except Exception as e:
                        print(e)

        if RELEASE:
            zip_name = '%s-%s' % (PROJECT_NAME, NOW)
            shutil.make_archive(os.path.join(
                BASE_DIR, zip_name), 'zip', BUILD_PATH)

        winsound.Beep(440, 100)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'release':
        RELEASE = True
    build()
