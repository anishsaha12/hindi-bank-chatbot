import xml.etree.ElementTree as ET
import json
import string

tree = ET.parse('../data/bank_chatbot_dataset.xml')
dataset = tree.getroot()

def preprocess_text(sentence):
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))        # remove punct
    sentence = sentence.replace('।','')                                             # remove punct
    sentence = sentence.replace('|','')                                             # remove punct
    sentence = sentence.strip()                                                     # remove punct
    sentence = sentence.replace('  ',' ')                                           # remove extra space
    sentence = sentence.lower()                                                     # lower case
    return sentence

dat = dict()

for intent in dataset:
    int_cls = intent.attrib['name']
    
    lines = []
    for dialog in intent:
        if dialog.tag == "customer":
            text = dialog.tag+'- '+preprocess_text(dialog.text)
            lines.append(text)
        elif dialog.tag == "client":
            text = dialog.tag+'- '+dialog.text
            lines.append(text)
        elif dialog.tag == "expand-intent":
            exp_intent = dataset.find('intent[@name="'+dialog.attrib['name']+'"][@variation="'+dialog.attrib['variation']+'"]')
            for exp_dialog in exp_intent:
                if exp_dialog.tag == "customer" or exp_dialog.tag == "client":
                    text = exp_dialog.tag+'- '+preprocess_text(exp_dialog.text)
                    lines.append(text)
        else:
            print(dialog.tag)
    try:
        oh = dat[int_cls]
    except:
        dat[int_cls] = lines

f1 = open('../data/raw_data_dict.json', 'w', encoding='utf8')

# f1.write(json.dumps(dat))
print(dat, file=f1)
f1.close()


## check for duplicate sentences