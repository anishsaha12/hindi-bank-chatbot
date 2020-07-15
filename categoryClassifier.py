import pickle
import numpy as np
from keras.models import load_model
from posTagger import *

with open('categoryClassifier/max_len.pkl', 'rb') as f:
    max_len = pickle.load(f)

with open('categoryClassifier/idx2word.pkl', 'rb') as f:
    idx2word = pickle.load(f)

with open('categoryClassifier/word2idx.pkl', 'rb') as f:
    word2idx = pickle.load(f)

with open('categoryClassifier/word2pos.pkl', 'rb') as f:
    word2pos = pickle.load(f)
    
with open('categoryClassifier/pos2idx.pkl', 'rb') as f:
    pos2idx = pickle.load(f)
    
with open('categoryClassifier/idx2category.pkl', 'rb') as f:
    idx2category = pickle.load(f)

model = load_model('categoryClassifier/word_pos_emb_bilstm_category_classifier.h5')

def categoryClassifier(line):
    input_to_tag = line.rstrip()
    input_tokens = input_to_tag.split(' ')
    X_word = []
    
    for w in input_tokens:
        try:
            X_word.append(word2idx[w])
        except:
            X_word.append(word2idx["UNK"])

    # pos tag the inpt line
    pos_tagged = posTagger(line)
    
    X_pos = []
    for w in pos_tagged:
        try:
            X_pos.append(pos2idx[w])
        except:
            X_pos.append(pos2idx["UNK"])


    X_word = [X_word]
    X_word = pad_sequences(maxlen=max_len, sequences=X_word, value=word2idx["PAD"], padding='post', truncating='post')

    X_pos = [X_pos]
    X_pos = pad_sequences(maxlen=max_len, sequences=X_pos, value=word2pos["PAD"], padding='post', truncating='post')

    y_pred = model.predict([X_word,
                            X_pos
                            ])

    p = np.argmax(y_pred[0], axis=-1)

    result = idx2category[p]

    return result