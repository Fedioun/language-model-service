import os, settings
import numpy as np

def remove_duplicate(list):
    final_list = []
    for l in list:
        if l not in final_list:
            final_list.append(l)
    return final_list


def remove_blank_line(list):
    final = []
    for l in list:
        if l == '' or l is None or l == '\n' or l == ' ':
            pass
        else:
            final.append(l)
    return final


def write2file(list, fileout):
    if os.path.exists(fileout):
        os.remove(fileout)
    list = remove_duplicate(list)
    with open(fileout, 'a+', encoding="UTF8") as out:
        for item in list:
            if item[-1] != "\n":
                item+="\n"
            out.write(item)


def read2list(filein):
    lines = []
    with open(filein, 'r', encoding="UTF8") as fbuffer:
        for line in fbuffer:
            lines.append(line.rstrip('\n'))
    listout = []
    for i in lines:
        i = i.rstrip('\n')
        if i not in listout:
            listout.append(i)
    return listout


def file_concat(filelist, fileout=None):
    contents = []
    for file in filelist:
        contents += read2list(file)
    contents = remove_duplicate(contents)
    contents = remove_blank_line(contents)
    if fileout is not None:
        write2file(contents, fileout)
    return contents

def load_probas(probas_file):
    with open(probas_file, encoding="utf8") as probas:
        arrays = []
        names = []
        rows = []
        lines = probas.read().split("\n")
        stline = 0
        if lines[0].startswith("blank"):
            stline = 1
        for k in range(stline, len(lines)-1):
            #print(lines[k])
            if " [" in lines[k]:
                name = lines[k].split(" ")[0]

            elif " ]" in lines[k]:
                tmp = []
                for i in lines[k].strip().split(" ")[:-1]:
                    tmp.append(float(i.strip()))

                rows.append(np.asarray(tmp))
                arrays.append(np.asarray(rows))
                names.append(name)

                if False:
                    print("tmp",np.asarray(tmp).shape)
                    print("row",np.asarray(rows).shape)
                    print("evdd",np.asarray(arrays).shape)
                    time.sleep(1)
                rows = []
            else:
                tmp = []
                for i in lines[k].strip().split(" "):
                    tmp.append(float(i.strip()))
                rows.append(np.asarray(tmp))
        return arrays, names

def save_probas(arrays, output_file, names=None, charset=None):

    with open(output_file, "w", encoding="utf8") as file:
        if charset is not None:
            file.write("blank")
            for c in charset:
                if c != " ":
                    file.write(" " + c)
                else:
                    file.write(" <sp>")
            file.write("\n")

        for k in range(len(arrays)):
            if names is not None:
                file.write(names[k] +  " [ ")
            else:
                file.write(str(k) + " [ ")
            for rows in arrays[k]:

                file.write("\n")
                for col in rows:
                    file.write(str(col) + " ")
            file.write("]\n")

def get_charset_from_file():
    charset = []
    input_file = os.path.join(settings.MODEL_FOLDER, "units.txt")
    with open(input_file, "r", encoding="utf8") as units:
        lines = units.readlines()
        for line in lines:

            token = line.split(" ")[0]
            print(token)
            if token in settings.DICTIONARY:
                charset.append(settings.DICTIONARY[token])
            else:
                charset.append(token)
    return charset

def clean_service_tmp_files(basename):
    path = os.path.join(settings.SERVICE_OUTPUT_FOLDER, basename + ".txt")
    if os.path.exists(path):
        os.remove(path)
    path = os.path.join(settings.SERVICE_OUTPUT_FOLDER, basename + ".txt")
    if os.path.exists(path):
        os.remove(path)
    path = os.path.join(settings.SERVICE_OUTPUT_FOLDER, "add_pen_" + basename + ".tra")
    if os.path.exists(path):
        os.remove(path)
    path = os.path.join(settings.SERVICE_OUTPUT_FOLDER, "alignments_" + basename + ".tra")
    if os.path.exists(path):
        os.remove(path)
    path = os.path.join(settings.SERVICE_OUTPUT_FOLDER, "scale_" + basename + ".tra")
    if os.path.exists(path):
        os.remove(path)
    path = os.path.join(settings.SERVICE_OUTPUT_FOLDER, "lats_" + basename + ".tra")
    if os.path.exists(path):
        os.remove(path)
    path = os.path.join(settings.SERVICE_OUTPUT_FOLDER, "words_" + basename + ".tra")
    if os.path.exists(path):
        os.remove(path)
