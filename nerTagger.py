import pickle
import numpy as np
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from posTagger import *

with open('nerTagger/max_len.pkl', 'rb') as f:
    max_len = pickle.load(f)

with open('nerTagger/max_len_char_prefix.pkl', 'rb') as f:
    max_len_char_prefix = pickle.load(f)

with open('nerTagger/max_len_char_suffix.pkl', 'rb') as f:
    max_len_char_suffix = pickle.load(f)

with open('nerTagger/word2pos.pkl', 'rb') as f:
    word2pos = pickle.load(f)
    
with open('nerTagger/word2idx.pkl', 'rb') as f:
    word2idx = pickle.load(f)

with open('nerTagger/pos2idx.pkl', 'rb') as f:
    pos2idx = pickle.load(f)

with open('nerTagger/char2idx.pkl', 'rb') as f:
    char2idx = pickle.load(f)

with open('nerTagger/idx2tag.pkl', 'rb') as f:
    idx2tag = pickle.load(f)


model = load_model('nerTagger/word_pos_char_emb_bilstm_ner_tagger.h5')


def nerTagger(line):
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

    sent_seq = []
    for i in range(max_len):
        word_seq = []
        for j in range(max_len_char_prefix):
            try:
                charIdx = char2idx.get(input_tokens[i][j])
                if charIdx is not None:
                    word_seq.append(charIdx)
                else:
                    word_seq.append(char2idx.get("UNK"))
            except:
                word_seq.append(char2idx.get("PAD"))
        sent_seq.append(word_seq)

    X_char_prefix = [sent_seq]

    sent_seq = []
    for i in range(max_len):
        word_seq = []
        for j in range(max_len_char_suffix):
            try:
                charIdx = char2idx.get(input_tokens[i][-max_len_char_suffix + j])
                if charIdx is not None:
                    word_seq.append(charIdx)
                else:
                    word_seq.append(char2idx.get("UNK"))
            except:
                word_seq.append(char2idx.get("PAD"))
        sent_seq.append(word_seq)

    X_char_suffix = [sent_seq]

    y_pred = model.predict([X_word,
                            X_pos,
                            np.array(X_char_prefix).reshape((len(X_char_prefix),
                                                                max_len, max_len_char_prefix)),
                            np.array(X_char_suffix).reshape((len(X_char_suffix),
                                                                max_len, max_len_char_suffix))
                            ])

    p = np.argmax(y_pred[0], axis=-1)

    result = []
    for w, pred in zip(input_tokens, p):
        if w != 0:
            result.append([w, idx2tag[pred]])

    return result


# print(ner_tagger("आपके मोबाइल पे बैंक से एक OTP आएगा . कृपया बताइये ."))