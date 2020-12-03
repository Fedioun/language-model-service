import settings, shutil
import logging, os, tqdm
import time
import src.charset_adaptation
from src.greedy import write_greedy
import src.utils.utils as utils

def decode_probas():
    files = sorted(os.listdir(settings.INPUT_FOLDER))

    for file in tqdm.tqdm(files):
        transcriptions = get_transcription(file)

        output_file_name = os.path.join(settings.OUTPUT_FOLDER, settings.MODEL_NAME + "_" + file.split(".")[0] + '.txt')
        with open(output_file_name, "w", encoding="utf8") as outfile :
            for t in transcriptions:
                #print(t[0], t[1])
                outfile.write(t[0] +  " " + t[1] + "\n")

def get_transcription(file):
    basename = file.split(".")[0]
    #updated = os.listdir(settings.INPUT_FOLDER_UPDATED)
    probas, names = src.charset_adaptation.get_updated_probas(file)

    if settings.GREEDY == True:
        write_greedy(basename, probas, names)

    print("Saving probas ", file)
    tmpfile = os.path.join(settings.SERVICE_INPUT_FOLDER, basename + ".tmp")

    utils.save_probas(probas, tmpfile, names=names)
    utils.clean_service_tmp_files(basename)
    shutil.move(tmpfile, os.path.join(settings.SERVICE_INPUT_FOLDER, basename + ".tra"))

    print("Done")

    begin = time.time()
    found = False

    while not found:
        outFiles = os.listdir(settings.SERVICE_OUTPUT_FOLDER)
        for f in outFiles:
            if f.startswith(file.split(".")[0]) and f.endswith(".txt"):
                found = True
    print("Decoding done")
    print(time.time() - begin)
    time.sleep(3)



    transcriptions = src.decode.transcribe(
        os.path.join(settings.SERVICE_OUTPUT_FOLDER, basename + ".txt")
    )
    return transcriptions



def transcribe(inputFile):

    dictionnary = []
    with open(settings.DICTIONNARY) as input:
            for word in input:
                dictionnary.append(word.strip().split(" ")[0])

    results = []
    with open(inputFile, "r+", encoding="UTF8") as input:
        lines = input.readlines()
        print(inputFile, len(lines))
        n = 0

        for line in lines:
            #print(line)
            if len(line.strip()) > 0:
                words_ids  = line.strip().split(" ")
                id = words_ids[0]
                words_ids = words_ids[1:]

                if "".join(words_ids).isdigit():
                    #print(line)

                    if len(words_ids) == 0:
                        continue
                    #print(line.strip())
                    result = ""
                    for k in words_ids:
                        result += decode_string(dictionnary[int(k)])
                    results.append((id, result))
        return results

def decode_string(code_string):
    result = ""
    pos = 1
    spe_char = ""
    # End charac
    code_string += "Z" # Tampon charac, will not appear in transcription
    #print("codestring : ", code_string)
    while pos < len(code_string):
        #print(code_string[pos-1], code_string[pos])
        # Two letters
        if code_string[pos].isalpha() and code_string[pos - 1].isalpha():
            result += code_string[pos - 1]

        if code_string[pos].isdigit() and code_string[pos - 1].isalpha():
            # Start spec char
            spe_char += code_string[pos - 1]


        if code_string[pos].isdigit() and code_string[pos - 1].isdigit():
            spe_char += code_string[pos - 1]
            #Continue spec char

        if code_string[pos].isalpha() and code_string[pos - 1].isdigit():

            spe_char += code_string[pos - 1]
            if spe_char.startswith("d"):
                result += spe_char[1:]
            else:
                try:
                    result += settings.CODESET[spe_char]
                except Exception as e:
                    #print(line.strip().split(" "))
                    result += spe_char
            spe_char = ""
        #print("res : ", result, " spe : ", spe_char)
        pos += 1
    return result
