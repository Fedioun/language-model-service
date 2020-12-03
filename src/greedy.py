import os, settings
import numpy as np


def greedy_decode(arrays, charset):
    results = []
    for probas in arrays:
        greed_ctc = []
        for k in probas:
            greed_ctc.append(np.argmax(k))
        last = 10000
        greed = []
        for k in greed_ctc:
            if k != last:
                greed.append(k)
            last = k

        #print(greed_ctc, len(greed_ctc))
        #print(greed)
        ref = charset
        pred = greed
        nb_ref = len(ref)
        r = ""
        for j in range(len(pred)):
            c = int(pred[j])
            if (c>=0 and c<nb_ref):
                #print(ref[c])
                #print(r)
                r += ref[c]
        results.append(r)
    return results

def write_greedy(basename, probas, names):
    greedy = greedy_decode(probas, settings.CHARSET)
    greedy_output_file_name = os.path.join(settings.OUTPUT_FOLDER, "greedy" + "_" + basename + '.txt')
    with open(greedy_output_file_name, "w", encoding="utf8") as outfile :
        for k in range(len(greedy)):

            outfile.write(names[k] +  " " + greedy[k] + "\n")
