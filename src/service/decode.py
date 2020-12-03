import settings, os, requests, json
import subprocess
import traceback
import sys

def decode(input_file):
    scale = settings.ACCOUSTIC_SCALE
    dictionnary = []
    codeset = {}

    for k in range(len(settings.CHARS_TABLE)):
        codeset[settings.CHARS_CODESET[k]] = settings.CHARS_TABLE[k].encode("utf8")

    with open(settings.DICTIONNARY) as input:
        for word in input:
            dictionnary.append(word.strip().split(" ")[0])

    #input_file = "./data/proba/train2011-0_0_1.png_proba.txt"
    print("Input :", input_file)
    try:
        print(
        '--beam=' + str(settings.BEAM),
        '--word-symbol-table=' + settings.DICTIONNARY,
        '--acoustic-scale=' + str(scale), #str(settings.ACCOUSTIC_SCALE),
        '--allow-partial=true',
        settings.LANGUAGE_MODEL,
        'ark,t:' + input_file,
        'ark,t:' + settings.TMP_TRANSCRIPT)


        out = subprocess.run(
            [
                'decode-faster',
                '--beam=' + str(settings.BEAM),
                '--word-symbol-table=' + settings.DICTIONNARY,
                '--acoustic-scale=' + str(scale), #str(settings.ACCOUSTIC_SCALE),
                '--allow-partial=true',
                settings.LANGUAGE_MODEL,
                'ark,t:' + input_file,
                'ark,t:' + settings.TMP_TRANSCRIPT
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
            check=True,
            shell=False
            )
        print(out)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(e)

    with open("result.txt", "a", encoding="utf8") as output:
        t = transcribe(settings.TMP_TRANSCRIPT, dictionnary, codeset)

        output.write(t + "\n")
    return t

def decode_two_pass(input_file):
    verbose = True
    dictionnary = []
    codeset = {}

    for k in range(len(settings.CHARS_TABLE)):
        codeset[settings.CHARS_CODESET[k]] = settings.CHARS_TABLE[k].encode("utf8")

    with open(settings.DICTIONNARY) as input:
        for word in input:
            dictionnary.append(word.strip().split(" ")[0])

    try:
        if verbose:
            print(
                'latgen-faster',
                '--beam=' + str(settings.BEAM),
                '--lattice-beam=' + str(settings.LATTICE_BEAM),
                '--word-symbol-table=' + settings.DICTIONNARY,
                '--acoustic-scale=' + str(settings.ACCOUSTIC_SCALE), #str(settings.ACCOUSTIC_SCALE),
                settings.LANGUAGE_MODEL,
                'ark:' + input_file,
                'ark,t:' + settings.TMP_LATTICE
            )
        out = subprocess.run(
            [
                'latgen-faster',
                '--beam=' + str(settings.BEAM),
                '--lattice-beam=' + str(settings.LATTICE_BEAM),
                '--word-symbol-table=' + settings.DICTIONNARY,
                '--acoustic-scale=' + str(settings.ACCOUSTIC_SCALE), #str(settings.ACCOUSTIC_SCALE),
                settings.LANGUAGE_MODEL,
                'ark:' + input_file,
                'ark,t:' + settings.TMP_LATTICE
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
            check=True,
            shell=False
            )
        print(out)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(e)

    try:
        out = subprocess.run(
            [
                'lattice-add-penalty',
                '--word-ins-penalty=' + str(settings.WORDS_PENALTY),
                'ark:' + settings.TMP_LATTICE,
                'ark,t:' + settings.TMP_LATTICE_PENALTY
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
            check=True,
            shell=False
            )
        print(out)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(e)

    try:
        out = subprocess.run(
            [
                'lattice-scale',
                '--acoustic-scale=' + str(settings.ACCOUSTIC_SCALE),
                'ark:' + settings.TMP_LATTICE_PENALTY,
                'ark,t:' + settings.TMP_LATTICE_SCALE
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
            check=True,
            shell=False
            )
        print(out)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(e)

    try:
        out = subprocess.run(
            [
                'lattice-best-path',
                '--acoustic-scale=' + str(settings.ACCOUSTIC_SCALE),
                'ark:' + settings.TMP_LATTICE_SCALE,
                'ark,t:' + settings.TMP_TRANSCRIPT
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
            check=True,
            shell=False
            )
        print(out)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(e)

    with open("result.txt", "w", encoding="utf8") as output:
        transcriptions = transcribe(settings.TMP_TRANSCRIPT, dictionnary, codeset)
        for t in transcriptions:
            output.write(t + "\n")
    return transcriptions




def transcribe(inputFile, dictionnary, codeset):
    results = []
    with open(inputFile, "r+", encoding="UTF8") as input:
        lines = input.read().split("\n")
        for line in lines:
            words_id = line.strip().split(" ")[1:]
            #print(words_id)
            transcription = ""
            for k in words_id:
                #print(k)
                transcription += dictionnary[int(k)]

            result = ""
            for k in range(len(transcription)):
                if transcription[k].isalpha():
                    if k == len(transcription) - 1:
                        result += transcription[k]
                    elif transcription[k + 1].isdigit():
                        code = transcription[k]
                        p = k + 1
                        while p < len(transcription) and transcription[p].isdigit():
                            code += transcription[p]
                            p += 1
                        result += codeset[code].decode("utf8")
                    else:
                        result += transcription[k]
            results.append(result)
        return results
