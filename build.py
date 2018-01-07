import fileinput
import os
import re
import shutil
import sys
import time
import winsound
from PIL import Image


PROJECT_NAME = 'zebra-redux'
RELEASE = False
FLUSH_METADATA = False

NOW = time.strftime('%Y-%m%d-%H%M')
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

BUILD_PATH = os.path.join(BASE_DIR, 'build')
REDUX_PATH = os.path.join(BUILD_PATH, 'Redux')
SCRIPTS_PATH = os.path.join(REDUX_PATH, 'Scripts')
IMAGES_PATH = os.path.join(REDUX_PATH, 'Images')

CONFIG_DEFAULT = {'redux_config_name': 'default',
                  'redux_version': NOW,
                  'redux_title_font': 'Viga-Regular',
                  'redux_title_font_size': '10.00',
                  'redux_pane_radius': '0.00',
                  'redux_dot_size': '7.00',
                  'redux_title_h': '14.00',
                  'redux_module_is_rackmember': 'YES',
                  'redux_module_overlay_mode': 'overlay',
                  'redux_rack_404_bounds': '259.00 40.00 339.00 674.00',
                  'redux_fx_rack_parent': 'Rack 404',
                  'redux_fx_rack_layermask': '80000000',
                  'redux_fx_rack_bounds': '6.00 3738.00 324.00 160.00',
                  }

CONFIG_DRZHNN = {'redux_config_name': 'drzhnn',
                 'redux_version': NOW,
                 'redux_title_font': 'Viga-Regular',
                 'redux_title_font_size': '11.00',
                 'redux_pane_radius': '0.00',
                 'redux_dot_size': '7.00',
                 'redux_title_h': '14.00',
                 'redux_module_is_rackmember': 'NO',
                 'redux_module_overlay_mode': 'overlay',
                 'redux_rack_404_bounds': '259.00 40.00 339.00 674.00',
                 'redux_fx_rack_parent': 'Rack 404',
                 'redux_fx_rack_layermask': '80000000',
                 'redux_fx_rack_bounds': '6.00 3738.00 324.00 160.00',
                 }

CONFIG_FIXED_FXRACK = {'redux_config_name': 'fixed_fxrack',
                       'redux_version': NOW,
                       'redux_title_font': 'Viga-Regular',
                       'redux_title_font_size': '10.00',
                       'redux_pane_radius': '0.00',
                       'redux_dot_size': '7.00',
                       'redux_title_h': '14.00',
                       'redux_module_is_rackmember': 'YES',
                       'redux_module_overlay_mode': 'overlay',
                       'redux_rack_404_bounds': '259.00 40.00 339.00 510.00',
                       'redux_fx_rack_parent': 'Top Panel',
                       'redux_fx_rack_layermask': '1',
                       'redux_fx_rack_bounds': '265.00 554.00 324.00 160.00',
                       }

CONFIGS_TO_BUILD = [CONFIG_DEFAULT, CONFIG_DRZHNN, CONFIG_FIXED_FXRACK]

GARBAGE = ['(?!#FX.)[#].*', '^[ \t]+', '[ \t]+$', '  +', '^\n']


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


def build(config):
    try:
        shutil.rmtree(REDUX_PATH)
    except Exception as e:
        print(e)

    try:
        os.makedirs(REDUX_PATH)
    except Exception as e:
        print(e)
    finally:
        shutil.copytree(os.path.join(BASE_DIR, 'scripts'), SCRIPTS_PATH)
        shutil.copytree(os.path.join(BASE_DIR, 'images'), IMAGES_PATH)

    scripts = []

    for root, _, files in os.walk(SCRIPTS_PATH):
        for filename in files:
            full_path = os.path.join(root, filename)
            scripts.append(full_path)

    for line in fileinput.FileInput(scripts, inplace=1):
        for i, _ in enumerate(GARBAGE):
            line = re.sub(GARBAGE[i], '', line)

        for key in config:
            regex_string = r'\b(%s)\b' % key
            line = re.sub(regex_string, config[key], line)

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
        zip_name = '%s-%s-%s' % (PROJECT_NAME, NOW,
                                 config['redux_config_name'])
        shutil.make_archive(os.path.join(
            BASE_DIR, zip_name), 'zip', BUILD_PATH)

    winsound.Beep(2000, 100)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'release':
        RELEASE = True
        for config in CONFIGS_TO_BUILD:
            build(config)
    else:
        build(CONFIG_DRZHNN)
