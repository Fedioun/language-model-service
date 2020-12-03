#!/usr/bin/python
# -*- coding: utf8 -*-
import os

BEAM = 16
LATTICE_BEAM = 5
ACCOUSTIC_SCALE = 1.3
WORD_INS_PENALTY = -3
GENERATE_UNITS = True
GENERATE_TOKENS = True
GENERATE_LEXICON = True
GENERATE_GRAMMAR = True
GENERATE_WORDS = True


WORKING_FOLDER = "./data"
GRAMMAR_FOLDER = "./data/grammar"
VOCABULARY_FOLDER = "./data/vocabulary"

UNITS = os.path.join(WORKING_FOLDER, "texts/units.txt")
LEXICON = os.path.join(WORKING_FOLDER, "texts/lexicon.txt")
LEXICON_DIS = os.path.join(WORKING_FOLDER, "texts/lexicon_disambig.txt")
TOKENS = os.path.join(WORKING_FOLDER, "texts/tokens.txt")

TOKENS_FST = os.path.join(WORKING_FOLDER, 'fst_syntax/Token_FST_syntax')
LEXICON_FST = os.path.join(WORKING_FOLDER, 'fst_syntax/Lexicon_FST_syntax')
GRAMMAR_FST = os.path.join(WORKING_FOLDER, 'fst_syntax/Grammar_FST_syntax')

TOKENS_FST_BIN = os.path.join(WORKING_FOLDER, 'FST/Tokens.fst')
LEXICON_FST_BIN = os.path.join(WORKING_FOLDER, 'FST/Lexicon.fst')
GRAMMAR_FST_BIN = os.path.join(WORKING_FOLDER, "../grammar/TG9.fst")
LG_FST_BIN = os.path.join(WORKING_FOLDER, 'FST/LG.fst')
TLG_FST_BIN = os.path.join(WORKING_FOLDER, 'FST/TLG.fst')

INPUT ="/tmp/tmpprobs.tra"
TMP_INPUT= "/tmp/tmpprobs_outcharset.tra"
TMP_TRANSCRIPT = "/tmp/tmp_transcript.txt"
TMP_LATTICE = "/tmp/tmp_lattice.lat"
TMP_LATTICE_PENALTY = "/tmp/tmp_lattice_penalty.lat"
TMP_LATTICE_SCALE = "/tmp/tmp_lattice_scale.lat"

CODESET = {
    "s1" : ":",
    "s2" : "%",
    "s3" : "-",
    "s4" : "_",
    "s5" : "¤",
    "s6" : " ",
    "s7" : "(",
    "s8" : "=",
    "s9" : "+",
    "s10" : "€",
    "s11": ";",
    "s12": ".",
    "s13" : "!",
    "s14" : ")",
    "s15" : "}",
    "s16" : "²",
    "s17" : ",",
    "s18" : "{",
    "s19" : "'",
    "s20" : "/",
    "s22" : "\\",
    "s21" : "°",
    "s23" : "?",
    "s24" : "*",
    "s25" : "#",
    "s26" : "&",
    #####################
    "c1" : "û",
    "c2" : "ê",
    "c3" : "â",
    "c4" : "ô",''
    "c5" : "ç",
    "c6" : "É",
    "c7" : "î",
    "c8" : "À",
    "c9" : "é",
    "c10" : "ù",
    "c11" : "è",
    "c12" : "à",
    "c13" : "œ",     # ??

    "c14" : "ë",
    "c15" : "&",
}

SOURCE_CHARSET = ['J', 'e', ' ', 'v', 'o', 'u', 's', 'a', 'd', 'r', 'c', 'i', 'f', 'n', 'l', 't', '.', 'V', 'z', 'm', 'q', 'é', 'à', 'h', 'è', 'D', ',', 'j', 'p', 'M', 'P', 'b', "'", 'g', 'x', 'E', 'S', 'L', 'C', ':', '0', '3', '4', '2', '9', '7', '8', '5', 'A', 'y', '-', 'R', 'G', 'N', '6', ';', 'î', '1', 'I', 'B', '°', '(', 'Y', 'Z', 'W', ')', 'ç', 'ê', 'ô', '?', 'H', 'â', '/', 'U', 'Q', '"', 'O', 'F', 'T', 'É', '*', 'ë', 'X', 'K', '%', '€', 'û', 'k', 'w', '+', 'ù', '¤', '!', '=', '{', 'À', '}', '²', 'œ', '_']

CHARSET = ['', 'à', ' ', 'm', 'o', 'n', 'd', 'i', 'c', 'l', 'e', ',', 's', 'r', 'a', 't', 'p', 'u', 'q', '.', '8', 'R', 'P', 'N', 'b', 'è', 'E', 'é', 'v', 'h', 'z', 'j', 'x', 'f', 'J', 'I', 'y', 'S', 'g', '1', '-', "'", 'î', 'M', ':', 'Z', 'T', 'C', 'O', '9', 'A', '0', '2', '5', 'D', 'V', 'H', 'B', '(', '6', '7', ')', 'ç', ';', '"', 'û', '!', 'ô', 'L', 'F', 'G', 'ê', '4', 'Y', '?', '3', 'â', 'K', 'U', '¤', '€', '°', 'X', '/', 'É', 'ù', 'Q', '%', 'W', '{', 'k', '_', '²', 'w', 'œ', '}', 'ë', '*', '=', '+', 'À']
# Experimental from wassim works, on chars-wiki
['', "q", "G",  "2",  "û",  "ê", "y", "d", "O",  ":",  "%",  "â", "l", "W", "B",  "-", "t",  "_", "J",  "5",  "¤",  " ",  "(", "g", "R",  "=", "o", "Z", "E",  "0",  "8", "w", "b", "M", "j", "U",  "+",   "€", "H",  "3", "r", "z", "e", "P",   ";",  "ô", "X", "C",   ".",  "ç",  "É", "m", "u", "K",  "6",   "!", "h", "S",   ")",  "î",   "}",  "À",   "²", "p", "F",  "1", "x", "c", "N",  "9",  "é", "a", "k", "V", "A",   ",", "s", "I",  "4",   "ù",   "è",   "à",   "{", "f", "Q",   "'", "n", "Y", "D", "/",   "œ", "v",   "°", "L",   "7", "\"",   "ë", "i", "T",   "?",   "*", "#", "&"]

# Created from imprefect transcription (FR+EN) Not working
["", "g", "û",  "Y",  "G",  "M", "w", "d", "O",  "m",  "!",  "N", "l", "t", "D",  "-", "t",  "_", "d",  "b",  "¤",  " ",  "(", "g", "j",  "=", "o", "Z", "E",  "W",  "8", "w", "b", "5", "j", " ",  "+",   "n", "H",  "3", "i", "y", "e", "f",   "o",  "2", "v", "F",   "p",  "P",  "Q", "m", "u", "1",  "c",   "q", "h", "l",   "r",  "R",   "s",  "S",   ":", "e", "F",  "1", "u", "E", "N",  "9",  "T", "A", "0", "V", "B",   ",", "k", "I",  "a",   "H",   "I",   "-",   '"', "G", "h",   ".", "n", "x", "D", "/",   "œ", "v",   "°", "3",   "7", "\"",   "L", "i", "T",   ",",   "*", "'", "&"]

# Original charset (models wiki)
['', 'à', ' ', 'm', 'o', 'n', 'd', 'i', 'c', 'l', 'e', ',', 's', 'r', 'a', 't', 'p', 'u', 'q', '.', '8', 'R', 'P', 'N', 'b', 'è', 'E', 'é', 'v', 'h', 'z', 'j', 'x', 'f', 'J', 'I', 'y', 'S', 'g', '1', '-', "'", 'î', 'M', ':', 'Z', 'T', 'C', 'O', '9', 'A', '0', '2', '5', 'D', 'V', 'H', 'B', '(', '6', '7', ')', 'ç', ';', '"', 'û', '!', 'ô', 'L', 'F', 'G', 'ê', '4', 'Y', '?', '3', 'â', 'K', 'U', '¤', '€', '°', 'X', '/', 'É', 'ù', 'Q', '%', 'W', '{', 'k', '_', '²', 'w', 'œ', '}', 'ë', '*', '=', '+', 'À']

# Delete input after decoding
CONSUME = False


OUTPUT_PATH = "/tmp/"

GRAMMAR = "G9.fst"
VOCABULARY = "words"

GREEDY = False
# Service

SERVICE = "/eesen/src/decoderbin/decode-faster-service"
TWO_PASS_SERVICE = "/eesen/src/decoderbin/decode-faster-two-pass-service"

INPUT_FOLDER_UPDATED = "/lm/data/input_updated"
INPUT_FOLDER = "/lm/data/input"
OUTPUT_FOLDER = "/lm/data/output"
SERVICE_INPUT_FOLDER = "/lm/data/service_input/"
SERVICE_OUTPUT_FOLDER = "/tmp/"


MODELS_ROOT_FOLDER = "/lm/models/"
"/home/afedioun/Documents/Language_models/models"

MODEL_NAME = "mg_french_wiki"
"CHARS-FR+EN"
"m2gram-FR+EN"

"mg_french_wiki"
"chars-wiki"

MODEL_FOLDER = os.path.join(MODELS_ROOT_FOLDER, MODEL_NAME, "lm/")

files = os.listdir(os.path.join(MODEL_FOLDER))
LANGUAGE_MODEL = os.path.join(MODEL_FOLDER, [x for x in files if x.endswith(".fst")][0])
DICTIONNARY = os.path.join(MODEL_FOLDER, "words.txt")



try:
    from local_settings import *
except ImportError:
    pass
'''
/eesen/src/decoderbin/decode-faster-service --beam=13 --acoustic-scale=2.21 --word-symbol-table=/lm/models/mg_french_wiki/lm/words.txt --model=/lm/models/mg_french_wiki/lm/TLG9.fst --input-folder=/tmp/ --output-folder=/tmp/;
/eesen/src/decoderbin/decode-faster --beam=13 --acoustic-scale=2.21 --word-symbol-table=/lm/models/m2gram-FR+EN/lm/words.txt /lm/models/m2gram-FR+EN/lm/TLG9.fst ark,t:/lm/data/input_updated/GFCN_noel_sample.txt ark,t:/tmp/stuff.tra;


/eesen/src/decoderbin/decode-faster-two-pass         --beam=13 --lattice-beam=5 --acoustic-scale=2.21 --word-symbol-table=/lm/models/m2gram-FR+EN_new/lm/words.txt --allow-partial=True --word-ins-penalty=-3         /lm/models/m2gram-FR+EN_new/lm/TLG9.fst          ark,t:/lm/data/input_updated/wiki_GFCN_proba_test_bg_iam_162E.txt ark,t:/tmp/rspec.tra ark:lat_wspec.tra ark,t:/tmp/trans_wspec.tra ark,t:/tmp/w_spec.tra ark,t:/tmp/a_spec.tra
./decode-faster-two-pass-service --beam=13 --lattice-beam=5 --acoustic-scale=2.21 --word-symbol-table=/lm/models/m2gram-FR+EN_new/lm/words.txt --allow-partial=True --word-ins-penalty=-3 --model=/lm/models/m2gram-FR+EN_new/lm/TLG9.fst --input-folder=/lm/proba/                 --output-folder=/lm/proba/;

'''""

dict =  {
    'A': 'a',
    'r': ')',
    't': 'W',
    'i': 'r',
    'c': '6',
    'l': 'S',
    'e': 'p',
    's': '}',
    'd': 'U',
    'a': '6',
    'm': '}',
    'n': ':',
    '\n': '€',
    '1': 'U',

}
