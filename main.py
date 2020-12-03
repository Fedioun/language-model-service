# -*- coding: UTF-8 -*-
import shutil, os, time, tqdm, sys
import src.charset_adaptation, settings
import src.decode
from src.compute_metrics import compute_metrics, wordsLevenshteinDistance, levenshteinDistance
from src.execute_service import execute_service, execute_two_pass_service

def main(argv):
    if len(argv) > 0:
        if argv[0] == "--decode" or argv[0] == "-d":
            src.decode.decode_probas()
        elif argv[0] == "--command" or argv[0] == "-c":
            execute_two_pass_service(debug=True)
            #execute_service(debug=True)
        elif argv[0] == "--metrics" or argv[0] == "-m":
            metrics_computation(argv[1])
        elif argv[0] == "--test" or argv[0] == "-t":


            str1 = ["Walla", "j'aime", "les", "crêpes"]
            str2 = ["Walla", "j'aim", "les", "crêpes"]
            res = wordsLevenshteinDistance(str1, str2)
            print(res['distance']/len(str2))
            st1 = "abcd"
            st2 = "abce"
            res = levenshteinDistance(st1, st2)
            print(res['distance']/len(st2))


        else:
            print("Unrecognized option: use -t/--train for training and no option for prediction")
    else:
        src.decode.decode_probas()
    return 0

def metrics_computation(input_folder):
    bases = ["rimes", "noel"]
    models = ["mg_french_wiki"] #"m2gram-wiki", "m2gram-FR+EN_new"
    base_dict = {
        'hamelin' : "GFCN_proba_test_hamelin_162E.txt",
        'iam' : "GFCN_proba_test_bg_iam_162E.txt",
        'rimes' : "GFCN_proba_test_bg_rimes_162E.txt",
        'noel' : "GFCN_proba_test_noel_162E.txt",
        "noel_blstm" : "NoelRimes_noel_probas.txt",
        "hamelin_blstm" : "NoelRimes_hamelin_probas.txt"
    }
    for b in bases:
        for m in models:
            compute_metrics(m, b, base_dict, preds_root_folder=input_folder)

if __name__ == "__main__":
    main(sys.argv[1:])
