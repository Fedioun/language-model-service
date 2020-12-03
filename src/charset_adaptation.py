# -*- coding: UTF-8 -*-
import numpy as np
from shutil import copyfile
import os, settings
import src.utils.utils as utils
import time, tqdm

def get_updated_probas(file):
    #if not file in updated:
    print("Charset adaptation")
    probas, names = utils.load_probas(os.path.join(settings.INPUT_FOLDER, file))
    if "GFCN" in file:
        charset = sorted(settings.SOURCE_CHARSET.copy())
        charset.append('')
    else:
        charset = settings.SOURCE_CHARSET.copy()
        charset.insert(0, '')

    return update_charset(charset, settings.CHARSET, probas), names

def update_charset(currentCharset, newCharset, arrays, verbose=True):
    out = []
    n = 0
    for probas in arrays:
        output = np.full((len(newCharset)+1, len(probas)), -100000, dtype=np.float32)
        probas = np.transpose(probas)
        n = 0
        for c in range(len(currentCharset)):
            try:
                i = newCharset.index(currentCharset[c])
                n+=1
                output[i] = probas[c]
            except ValueError as e:
                print(e)
        out.append(np.transpose(output))
    if verbose:
        print(str(n) + " charac in common")
    return out
