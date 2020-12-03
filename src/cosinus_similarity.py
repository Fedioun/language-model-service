import math, time, unidecode, re

def main():
    predFile = "/home/afedioun/Dev/ocr/out.txt"
    labelFile = "/home/afedioun/Documents/Datasets/Backend_out/labels.txt"
    predDict = getTokens(predFile)
    labelDict = getTokens(labelFile)


    n = 0
    tot = 0
    for key, value in predDict.items():
        labels = []
        preds = []
        for line in labelDict[key]:
            labels += filter_list([token for token in reduce_string(line).split(" ")])
        for line in predDict[key]:
            preds += filter_list([token for token in reduce_string(line).split(" ")])
        tot += CosineSimilarityBagOfWord(preds, labels)
        n += 1
    print(tot/n, n)

def compute_COS(predDict, labelDict, base):
    page_pred = getTokenFromDict(predDict, base)
    page_label = getTokenFromDict(labelDict, base)
    n = 0
    tot = 0

    for key, value in page_pred.items():
        labels = []
        preds = []
        for line in page_label[key]:
            labels += filter_list([token for token in reduce_string(line).split(" ")])
        for line in page_pred[key]:
            preds += filter_list([token for token in reduce_string(line).split(" ")])
        tot += CosineSimilarityBagOfWord(preds, labels)
        n += 1
    print(tot/n, n)
def filter_list(list):
    nl = []
    for e in list:
        if len(e) > 2:
            nl.append(e)
    return nl

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

def get_id(line, base):
    if base == "hamelin" or  base == "hamelin_blstm":
        return int(line.split(" ")[0].split("_")[0])
    if base == "noel" or  base == "noel_blstm":
        return int(line.split("_")[0])

def getTokenFromDict(dict, base):
    dictio = {}
    for key, value in dict.items():
        #print(value)
        text = value.strip()
        page_id = get_id(key, base)

        if page_id in dictio:
            dictio[page_id].append(text)
        else:
            dictio[page_id] = [text]
    return dictio

def getTokens(file):

    dictio = {}
    with open(file, 'r', encoding="utf8") as pred:
        lines = pred.readlines()
        for line in lines:
            page_id = int(line.split(" ")[0].split("_")[0])
            text = line.split(" ", 1)[1].strip()
            if page_id in dictio:
                dictio[page_id].append(text)
            else:
                dictio[page_id] = [text]
    return dictio




def CosineSimilarityBagOfWord(tokensPrediction, tokensLabel, useL2Norm=True):
    vectorPrediction = getBagOfWordVector(tokensPrediction, useL2Norm)
    vectorLabel = getBagOfWordVector(tokensLabel, useL2Norm)
    numerator = 0

    for token, valuePrediction in vectorPrediction.items():
        #print(token)
        if not token in vectorLabel:
            valueLabel = 0
        else:
            valueLabel = vectorLabel[token]
        #print(numerator)

        numerator += valuePrediction * valueLabel
    if (useL2Norm):
        return numerator

    denominator = ComputeNorm(vectorPrediction) * ComputeNorm(vectorLabel)
    if denominator != 0:
        score = numerator / denominator
    else:
        score = 0
    return score;

def getBagOfWordVector(tokens, useL2Norm=True):
    vector = {}
    for token in tokens:
        if token in vector:
            vector[token] += 1
        else:
            vector[token] = 1

    if (not useL2Norm):
        return vector

    L2Norm = computeNorm(vector)
    for token, value in vector.items():
        vector[token] = vector[token] / L2Norm

    return vector

def computeNorm(vector):
    res = 0
    for value in vector:
        res += vector[value]*vector[value]
    return math.sqrt(res)

"""
static float CosineSimilarityBagOfWord(IList<string> tokensPrediction, IList<string> tokensLabel, bool useL2Norm = true)
        {
            IDictionary<string, float> vectorPrediction = getBagOfWordVector(tokensPrediction, useL2Norm);
            IDictionary<string, float> vectorLabel = getBagOfWordVector(tokensLabel, useL2Norm);
            float numerator = 0.0f;
            foreach (var item in vectorPrediction)
            {
                string token = item.Key;
                float valuePrediction = item.Value;
                float valueLabel = (!vectorLabel.ContainsKey(token)) ? (0.0f) : (vectorLabel[token]);

                numerator += valuePrediction * valueLabel;
            }

            if (useL2Norm)
                return numerator;

            float denominator = ComputeNorm(vectorPrediction) * ComputeNorm(vectorLabel);
            float score = (denominator != 0.0f) ? (numerator / denominator) : (0.0f);

            return score;
        }

        static IDictionary<string, float> getBagOfWordVector(IList<string> tokens, bool useL2Norm = true)
        {
            Dictionary<string, float> vector = new Dictionary<string, float>();
            foreach(string token in tokens)
            {
                if(vector.ContainsKey(token))
                {
                    vector[token] += 1;
                    continue;
                }

                vector.Add(token, 1);
            }

            if (!useL2Norm)
                return vector;

            float L2Norm = ComputeNorm(vector);
            foreach (var token in vector.Keys.ToList())
            {
                vector[token] = vector[token] / L2Norm;
            }

            return vector;
        }

        static float ComputeNorm(IDictionary<string, float> vec)
        {
            float result = 0.0f;
            foreach (var pair in vec)
                result += pair.Value * pair.Value;
            return (float)Math.Sqrt(result);
        }
"""
