import os
import numpy as np

# Voir avec Denis pour le charset à priori il s'agit de celui ci-dessous masi trié par ordre lexicographique :
SOURCE_CHARSET = ['', 'à', ' ', 'm', 'o', 'n', 'd', 'i', 'c', 'l', 'e', ',', 's', 'r', 'a', 't', 'p', 'u', 'q', '.', '8', 'R', 'P', 'N', 'b', 'è', 'E', 'é', 'v', 'h', 'z', 'j', 'x', 'f', 'J', 'I', 'y', 'S', 'g', '1', '-', "'", 'î', 'M', ':', 'Z', 'T', 'C', 'O', '9', 'A', '0', '2', '5', 'D', 'V', 'H', 'B', '(', '6', '7', ')', 'ç', ';', '"', 'û', '!', 'ô', 'L', 'F', 'G', 'ê', '4', 'Y', '?', '3', 'â', 'K', 'U', '¤', '€', '°', 'X', '/', 'É', 'ù', 'Q', '%', 'W', '{', 'k', '_', '²', 'w', 'œ', '}', 'ë', '*', '=', '+', 'À']
['J', 'e', ' ', 'v', 'o', 'u', 's', 'a', 'd', 'r', 'c', 'i', 'f', 'n', 'l', 't', '.', 'V', 'z', 'm', 'q', 'é', 'à', 'h', 'è', 'D', ',', 'j', 'p', 'M', 'P', 'b', "'", 'g', 'x', 'E', 'S', 'L', 'C', ':', '0', '3', '4', '2', '9', '7', '8', '5', 'A', 'y', '-', 'R', 'G', 'N', '6', ';', 'î', '1', 'I', 'B', '°', '(', 'Y', 'Z', 'W', ')', 'ç', 'ê', 'ô', '?', 'H', 'â', '/', 'U', 'Q', '"', 'O', 'F', 'T', 'É', '*', 'ë', 'X', 'K', '%', '€', 'û', 'k', 'w', '+', 'ù', '¤', '!', '=', '{', 'À', '}', '²', 'œ', '_']




def main():
    SOURCE_CHARSET
    probas_file = "./probas_samples.txt"
    arrays, names = load_probas(probas_file)
    print(greedy_decode(arrays, SOURCE_CHARSET))



# Decodage greedy
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

        print(greed_ctc, len(greed_ctc))
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


# Basename : nom du fichier où sauvegarder
# Probas : treille de probas sous forme de matrice
# Names : noms des images de ligne
def write_greedy(basename, probas, names, output_folder, charset):
    greedy = greedy_decode(probas, charset)
    greedy_output_file_name = os.path.join(output_folder, "greedy" + "_" + basename + '.txt')
    with open(greedy_output_file_name, "w", encoding="utf8") as outfile :
        for k in range(len(greedy)):

            outfile.write(names[k] +  " " + greedy[k] + "\n")


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

# Arrays : tableau de matrices de probas
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


main()
