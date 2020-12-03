import unidecode, re, tqdm, time
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

def main():
    pred_file = "/lm/data/output/greedy_NoelRimes_noel_probas.txt"
    label_file = "/lm/data/labels/labels_noel.txt"
    new_label_file = "/lm/data/labels/noel_new.txt"

    labels = open(label_file, "r", encoding="utf8")
    labels_lines = labels.readlines()
    preds = open(pred_file, "r", encoding="utf8")
    preds_lines = preds.readlines()
    output = open(new_label_file, "w", encoding="utf8")

    print(len(labels_lines), len(preds_lines))
    for p in tqdm.tqdm(preds_lines):
        pred = " ".join(p.split(" ")[1:])
        best = ""
        best_score = 8000

        for l in labels_lines:

            label =  " ".join(l.split(" ")[1:])
            score = levenshteinDistance(label, pred)["distance"]

            if score < best_score:
                best_score = score
                best = label
            if False:
                time.sleep(0.1)
                print(reduce_string(pred))
                print(reduce_string(label))
                print(score)
                print(best_score)
        output.write(p.split(" ")[0] + " " + best)



if __name__ == "__main__":
    main()
