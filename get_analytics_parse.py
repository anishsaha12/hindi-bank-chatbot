import stanfordnlp
from graphviz import Digraph
from ner_tag_line import ner_tagger
import random, string

nlp = stanfordnlp.Pipeline(lang="hi")

def preprocess_text(sentence):
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))        # remove punct
    sentence = sentence.replace('।','')                                             # remove punct
    sentence = sentence.replace('|','')                                             # remove punct
    sentence = sentence.strip()                                                     # remove punct
    sentence = sentence.replace('  ',' ')                                           # remove extra space
    sentence = sentence.replace('है','')                                             # remove stop word
    sentence = sentence.lower()                                                     # lower case
    return sentence

def gen_dep_parse(text = "एकबार बिस्तर पर रोमरोम से रीत गईसी पड़ीपड़ी वह शिकायत कर बैठी थी मेरा सबकुछ जस का तस रह गया है अशेष"):
    doc = nlp(text)

    k = doc.sentences[0].dependencies_string()
    k = k.split('\n')

    wds = dict()
    for i,li in enumerate(k):
        label, parent_id, rel = [p.strip().replace('(','').replace(')','').replace("'",'') for p in li.split(',')]
        id = i+1
        wds[id] = label

    wds[0] = 'root'
    dot = Digraph(format='svg')

    for i,li in enumerate(k):
        label, parent_id, rel = [p.strip().replace('(','').replace(')','').replace("'",'') for p in li.split(',')]
        id = i+1
        # dot.edge(str(parent_id),str(id),label=rel)
        dot.edge(wds[int(parent_id)],wds[id],label=rel)

    name = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    dot.render("img/dep_parse/"+name)#, view=True)
    return 'img/dep_parse/'+name+'.svg'

# gen_dep_parse()

def gen_pos_parse(text = "एकबार बिस्तर पर रोमरोम से रीत गईसी पड़ीपड़ी वह शिकायत कर बैठी थी मेरा सबकुछ जस का तस रह गया है अशेष"):
    doc = nlp(text)

    k = doc.sentences[0].tokens

    dot = Digraph(format='svg')

    for token in k:
        pos = token.words[0].xpos
        wrd = token.words[0].text
        dot.edge(pos, wrd)
    
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    dot.render("img/pos_parse/"+name)#, view=True)
    return 'img/pos_parse/'+name+'.svg'


def gen_ner_parse(text = "पेमेंट करना है 10000"):
    text = preprocess_text(text)

    k = ner_tagger(text)

    dot = Digraph(format='svg')

    for token in k:
        wrd = token[0]
        ner = token[1]
        dot.edge(ner, wrd)
    
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    dot.render("img/ner_parse/"+name)#, view=True)
    return 'img/ner_parse/'+name+'.svg'