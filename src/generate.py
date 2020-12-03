import tqdm, time

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


def replace_charset():
    base = "iam"
    pred_file = "./data/output/CHARS-FR+EN_GFCN_proba_test_bg_iam_162E.txt"
    output_file = "./test.txt"
    charset_file = "./data/charset.txt"
    input_charset =  ["q", "G",  "2",  "û",  "ê", "y", "d", "O",  ":",  "%",  "â", "l", "W", "B",  "-", "t",  "_", "J",  "5",  "¤",  " ",  "(", "g", "R",  "=", "o", "Z", "E",  "0",  "8", "w", "b", "M", "j", "U",  "+",   "€", "H",  "3", "r", "z", "e", "P",   ";",  "ô", "X", "C",   ".",  "ç",  "É", "m", "u", "K",  "6",   "!", "h", "S",   ")",  "î",   "}",  "À",   "²", "p", "F",  "1", "x", "c", "N",  "9",  "é", "a", "k", "V", "A",   ",", "s", "I",  "4",   "ù",   "è",   "à",   "{", "f", "Q",   "'", "n", "Y", "D", "/",   "œ", "v",   "°", "L",   "7", "\"",   "ë", "i", "T",   "?",   "*", "#", "&"]

    target_charset = ["g", "û",  "Y",  "G",  "M", "w", "d", "O",  "m",  "!",  "N", "l", "t", "D",  "-", "t",  "_", "d",  "b",  "¤",  " ",  "(", "g", "j",  "=", "o", "Z", "E",  "W",  "8", "w", "b", "5", "j", " ",  "+",   "n", "H",  "3", "i", "y", "e", "f",   "o",  "2", "v", "F",   "p",  "P",  "Q", "m", "u", "1",  "c",   "q", "h", "l",   "r",  "R",   "s",  "S",   ":", "e", "F",  "1", "u", "E", "N",  "9",  "T", "A", "0", "V", "B",   ",", "k", "I",  "a",   "H",   "I",   "-",   '"', "G", "h",   ".", "n", "x", "D", "/",   "œ", "v",   "°", "3",   "7", "\"",   "L", "i", "T",   ",",   "*", "'", "&"]

    output = open(output_file, "w", encoding="utf8")

    with open(pred_file, "r", encoding="utf8") as predictions:
        lines = predictions.readlines()
        for line in lines:
            pred = line.split(" ", 1)[1].strip()
            newpred = ""
            for c in pred:
                for k in range(len(input_charset)):
                    if c == input_charset[k]:
                        newpred += target_charset[k]
            output.write(line.split(" ", 1)[0] + " " + newpred + "\n")


def generate_words(charset):
    output_file = "./words.txt"

    with open(output_file, "w", encoding="utf8") as out:
        out.write("<eps> 0\n")
        n = 1
        for k in charset:
            found = False
            for key, value in DICTIONARY.items():
                if k == value:
                    out.write(key + " " + str(n) + "\n")
                    found = True
            if k.isdigit():
                out.write("d" + k + " " + str(n) + "\n")
                found = True
            if not found:
                out.write(k + " " + str(n) + "\n")
            n+= 1
        out.write("#0 " + str(n))


def main():
    replace_charset()
    #exit()
    base = "iam"
    pred_file = "./test.txt"
    label_file = "./data/labels/labels_iam.txt"
    charset_file = "./data/charset.txt"
    input_charset = ["q", "G",  "2",  "û",  "ê", "y", "d", "O",  ":",  "%",  "â", "l", "W", "B",  "-", "t",  "_", "J",  "5",  "¤",  " ",  "(", "g", "R",  "=", "o", "Z", "E",  "0",  "8", "w", "b", "M", "j", "U",  "+",   "€", "H",  "3", "r", "z", "e", "P",   ";",  "ô", "X", "C",   ".",  "ç",  "É", "m", "u", "K",  "6",   "!", "h", "S",   ")",  "î",   "}",  "À",   "²", "p", "F",  "1", "x", "c", "N",  "9",  "é", "a", "k", "V", "A",   ",", "s", "I",  "4",   "ù",   "è",   "à",   "{", "f", "Q",   "'", "n", "Y", "D", "/",   "œ", "v",   "°", "L",   "7", "\"",   "ë", "i", "T",   "?",   "*", "#", "&"]
    target_charset = ["g", "û",  "Y",  "G",  "M", "w", "d", "O",  "m",  "!",  "N", "l", "t", "D",  "-", "t",  "_", "d",  "b",  "¤",  " ",  "(", "g", "j",  "=", "o", "Z", "E",  "W",  "8", "w", "b", "5", "j", " ",  "+",   "n", "H",  "3", "i", "y", "e", "f",   "o",  "2", "v", "F",   "p",  "P",  "Q", "m", "u", "K",  "c",   "q", "h", "l",   "r",  "R",   "s",  "S",   ":", "e", "F",  "1", "u", "E", "N",  "9",  "T", "A", "0", "V", "B",   ",", "k", "I",  "a",   "H",   "I",   "-",   '"', "G", "h",   ".", "n", "x", "D", "/",   "œ", "v",   "°", "L",   "7", "\"",   "L", "i", "T",   ",",   "*", "'", "&"]

    output = open(charset_file, "w", encoding="utf8")

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

    print(labels_dict)
    for k in range(len(input_charset)):
        best_score = 100000000
        best = ""

        for i in tqdm.tqdm(input_charset):
            score = 0
            if True: #if input_charset[k] == target_charset[k]:
                for key, pred in predictions_dict.items():

                    try:


                        pred = pred.replace(input_charset[k], i)

                        label = labels_dict[key]

                        if True:
                            print(input_charset[k], i)
                            print(pred)
                            print(label)
                            time.sleep(0.1)
                        score += levenshteinDistance(label, pred)["distance"]
                    except Exception as e:
                        pass
                        #print(e, ne)
                    else:
                        pass


                if score < best_score:
                    best_score = score
                    best = i
                if False:
                    time.sleep(0.1)
                    print(reduce_string(pred))
                    print(reduce_string(label))
                    print(score)
                    print(best_score)
        print(best_score)
        print(input_charset[k], "best : ", best)
        output.write(best + "\n")



if __name__ == "__main__":
    main()
