from PIL import Image
import fileinput
import os
import re
import shutil
import sys
import time
import winsound


PROJECT_NAME = 'zebra-redux'
RELEASE = False
FLUSH_METADATA = False

now = time.strftime('%Y-%m%d-%H%M')
base_dir = os.path.dirname(os.path.realpath(__file__))
zip_name = '%s-%s' % (PROJECT_NAME, now)

build_path = os.path.join(base_dir, 'build')
redux_path = os.path.join(build_path, 'Redux')
scripts_path = os.path.join(redux_path, 'Scripts')
images_path = os.path.join(redux_path, 'Images')

variables = {'label_font': 'RopaSans-Italic',
             'label_font_size': '12.00',
             'label_small_font': 'Viga-Regular',
             'label_small_font_size': '10.00',
             'display_font': 'RopaSans-Italic',
             'display_font_size': '13.00',
             'button_font': 'RopaSans-Italic',
             'button_font_size': '13.00',
             'title_font': 'Viga-Regular',
             'title_font_size': '11.00',
             'slider_head_size': '2.00',
             'slider_sensitivity': '0.20',
             'redux_version': now,
             'redux_pane_radius': '0.00',
             'redux_dot_size': '7.00',
             'redux_title_h': '14.00'
             }

garbage = ['(?!#FX.)[#].*', '^[ \t]+', '[ \t]+$', '  +', '^\n']


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


def main():
    try:
        shutil.rmtree(redux_path)
    except Exception as e:
        print(e)

    try:
        os.makedirs(redux_path)
    except Exception as e:
        print(e)
    finally:
        shutil.copytree(os.path.join(base_dir, 'scripts'), scripts_path)
        shutil.copytree(os.path.join(base_dir, 'images'), images_path)


    scripts = []

    for root, _, files in os.walk(scripts_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            scripts.append(full_path)

    for line in fileinput.FileInput(scripts, inplace=1):
        for i, _ in enumerate(garbage):
            line = re.sub(garbage[i], '', line)

        for key in variables:
            regex_string = r'\b(%s)\b' % key
            line = re.sub(regex_string, variables[key], line)

        print(line, end='')

    if FLUSH_METADATA:
        for root, dirs, files in os.walk(images_path):
            for file in files:
                fname = os.path.join(root, file)
                try:
                    flush_metadata(fname)
                except Exception as e:
                    print(e)

    if RELEASE:
        shutil.make_archive(os.path.join(base_dir, zip_name), 'zip', build_path)

    winsound.Beep(2000, 100)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        RELEASE = True
    main()
