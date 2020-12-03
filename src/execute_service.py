import settings, os
import subprocess
import traceback
import sys



def execute_service(debug=False):
    args = [
        settings.SERVICE,
        '--beam=' + str(settings.BEAM),
        '--word-symbol-table=' + settings.DICTIONNARY,
        '--acoustic-scale=' + str(settings.ACCOUSTIC_SCALE),
        '--allow-partial=true',
        '--model=' + settings.LANGUAGE_MODEL,
        '--input_folder=' + settings.SERVICE_INPUT_FOLDER,
        '--output_folder=' + settings.SERVICE_OUTPUT_FOLDER
    ]
    if debug:
        for a in args:
            print(a)

    out = subprocess.run(
        args,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
        check=True,
        shell=False
        )

def execute_two_pass_service(debug=False):

    args = [
        settings.TWO_PASS_SERVICE,
        '--beam=' + str(settings.BEAM),
        '--word-symbol-table=' + settings.DICTIONNARY,
        '--acoustic-scale=' + str(settings.ACCOUSTIC_SCALE),
        '--lattice-beam=' + str(settings.LATTICE_BEAM),
        '--word-ins-penalty=' + str(settings.WORD_INS_PENALTY),
        '--allow-partial=true',
        '--model=' + settings.LANGUAGE_MODEL,
        '--input_folder=' + settings.SERVICE_INPUT_FOLDER,
        '--output_folder=' + settings.SERVICE_OUTPUT_FOLDER
    ]
    if debug:
        for a in args:
            print(a)

    out = subprocess.run(
        args,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
        check=True,
        shell=False
        )
