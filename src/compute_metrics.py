
import time, unidecode, re, os
import src.cosinus_similarity as cosinus_similarity

def levenshteinDistance(str1, str2):
    m = len(str1)
    n = len(str2)
    lensum = float(m + n)
    d = []
    for i in range(m+1):
        d.append([i])
    del d[0][0]
    for j in range(n+1):
        d[0].append(j)
    for j in range(1,n+1):
        for i in range(1,m+1):
            if str1[i-1] == str2[j-1]:
                d[i].insert(j,d[i-1][j-1])
            else:
                minimum = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+1)
                d[i].insert(j, minimum)
    ldist = d[-1][-1]
    ratio = (lensum - ldist)/lensum
    return {'distance':ldist, 'ratio':ratio}

def wordsLevenshteinDistance(str1, str2):
    m = len(str1)
    n = len(str2)
    lensum = float(m + n)
    d = []
    for i in range(m+1):
        d.append([i])
    del d[0][0]
    for j in range(n+1):
        d[0].append(j)
    for j in range(1,n+1):
        for i in range(1,m+1):
            if str1[i-1] == str2[j-1]:
                d[i].insert(j,d[i-1][j-1])
            else:
                minimum = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+1)
                d[i].insert(j, minimum)
    ldist = d[-1][-1]
    ratio = (lensum - ldist)/lensum
    return {'distance':ldist, 'ratio':ratio}

def reduce_string(str):
    tmp = str.lower()
    res = ""
    for c in tmp:
        if c.isalpha():
            res +=c
        else:
            res += " "
    res = unidecode.unidecode(res)
    return re.sub(' +', ' ',res).strip()


def compute_WER(predictions_dict, labels_dict, reduce=False):
    n = 0
    sum = 0
    errsum = 0
    lensum = 0
    numerr = 0
    for key, value in labels_dict.items():
        try:
            prediction = predictions_dict[key].strip()
            #print(reduce_string(labels_dict[key]) +  "\n" + reduce_string(predictions_dict[key]))
            if reduce:
                truth = reduce_string(labels_dict[key])
                pred = reduce_string(prediction)
            else:
                truth = labels_dict[key]
                pred = prediction
            prediction_words = prediction.split(" ")
            truth_words = truth.split(" ")
            #print(truth, pred)
            res = wordsLevenshteinDistance(prediction_words, truth_words)
            sum += res["distance"]
            #errsum += res["distance"] / (len(truth) + 1)
            lensum += (len(truth_words))
            n+= 1
            #print(key)
            #print(predictions_dict[key])
        except Exception as e:
            numerr += 1
    print(numerr, " errors on ", len(labels_dict) , "images")
    print("WER : ", n, sum/lensum)

def compute_CER(predictions_dict, labels_dict, reduce=False):
        n = 0
        sum = 0
        errsum = 0
        lensum = 0
        numerr = 0
        for key, value in labels_dict.items():
            try:
                prediction = predictions_dict[key].strip()
                #print(reduce_string(labels_dict[key]) +  "\n" + reduce_string(predictions_dict[key]))
                if reduce:
                    truth = reduce_string(labels_dict[key])
                    pred = reduce_string(prediction)
                else:
                    truth = labels_dict[key]
                    pred = prediction
                #print(truth, pred)
                res = levenshteinDistance(truth, pred)
                sum += res["distance"]
                #errsum += res["distance"] / (len(truth) + 1)
                lensum += (len(truth))
                n+= 1
                #print(key)
                #print(predictions_dict[key])
            except Exception as e:
                numerr += 1
        print(numerr, " errors on ", len(labels_dict) , "images")
        print("CER : ", n, sum/lensum)

def format_id(base, line):
    #print(line)
    if base == "hamelin" or base == "hamelin_blstm":
        return line.split(" ")[0].split("/")[-1].split(".")[0]
    if base == "iam":
        if len(line.split(' ')[0].split('/')) > 1:
            return line.split(' ')[0].split('/')[1]
        else:
            return line.split(' ')[0]
    if base == "rimes":
        return line.split(' ')[0]
    if base == "noel" or base == "noel_blstm":
        if len(line.split(' ')[0].split('/')) > 1:
            return line.split(' ')[0].split('/')[1]
        else:
            return line.split(' ')[0]
    return line


def compute_metrics(model, base, base_dict, preds_root_folder=None):
    print("Computing ", model, " on ", base)
    labels_root_folder = "./data/labels/"
    if preds_root_folder == None:
        preds_root_folder = "./data/output/"
    pred_name = model + "_" + base_dict[base]

    label_file = os.path.join(labels_root_folder, "labels_" + base + ".txt")
    pred_file = os.path.join(preds_root_folder, pred_name)

    labels_dict = {}
    predictions_dict = {}
    with open(label_file, "r", encoding="utf8") as labels:
        lines = labels.readlines()
        for line in lines:
            #print(line.split(" ")[0])
            labels_dict[format_id(base, line)] = line.split(" ", 1)[1]

    with open(pred_file, "r", encoding="utf8") as predictions:
        lines = predictions.readlines()
        for line in lines:
            predictions_dict[format_id(base, line)] = line.split(" ", 1)[1].strip()


    compute_CER(predictions_dict, labels_dict, reduce=False)
    compute_WER(predictions_dict, labels_dict, reduce=False)
    #cosinus_similarity.compute_COS(predictions_dict, labels_dict, base)


if __name__ == "__main__":


    compute_WER(predictions_dict, labels_dict, reduce=False)
    bases = ["hamelin", "iam", "noel", "rimes", "noel_blstm", "hamelin_blstm"]
    models = ["greedy", "m2gram-wiki"]
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
            compute_metrics(m, b, base_dict)
