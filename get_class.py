import json
import string
from categoryClassifier import *

f = open('./data/keywords.json',encoding='utf8')
a = json.load(f)
intents = a['intents']

kws = [set(inte['keyword']) for inte in intents]

def preprocess_text(sentence):
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))        # remove punct
    sentence = sentence.replace('।','')                                             # remove punct
    sentence = sentence.replace('|','')                                             # remove punct
    sentence = sentence.strip()                                                     # remove punct
    sentence = sentence.replace('  ',' ')                                           # remove extra space
    sentence = sentence.lower()                                                     # lower case
    return sentence

def get_txt_class(find='मुझे अकाउंट का बैलेंस देखना है | '):
    doc_class = categoryClassifier(find)
    
    find = preprocess_text(find)
    wds = set(find.split(' '))
    res = dict()
    for i,kw in enumerate(kws):
        if len(kw)==0:
            res[i] = len(kw.intersection(wds))
        else:
            res[i] = len(kw.intersection(wds))#/len(kw)
    if max(res.values()) == 0:
        return "",{}
    txt_class = intents[max(res, key=res.get)]["intent"]+'-'+intents[max(res, key=res.get)]["description"]
    return txt_class, res

# get_txt_class('मेरे अकाउंट के लिए बेनेफिशरी add करना है')[0]