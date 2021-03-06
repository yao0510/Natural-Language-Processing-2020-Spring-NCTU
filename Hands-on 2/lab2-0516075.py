# -*- coding: utf-8 -*-
"""lab2-0516075.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rUDTWZX3o-r0AuvOZ2Y7p41a21cyrR8h

#NLTK
"""

import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
nltk.download('averaged_perceptron_tagger')
try:
    nltk.data.find('tokenizers')
except LookupError:
    nltk.download('punkt')
import pandas as pd
from collections import Counter

"""## Fetching the Corpus
`get_corpus()` reads the CSV file, and then return a list of the news headlines
"""

def get_corpus():
    df = pd.read_csv('https://raw.githubusercontent.com/bshmueli/108-nlp/master/reuters.csv') # https://bit.ly/nlp-reuters
    print("Dataset columns", df.columns)
    print("Dataset size", len(df))
    # Use content instead of title
    corpus = df.content.to_list()
    title = df.title.to_list()
    return title, corpus, len(corpus)

"""## Computing bigram frequencies
`get_ngram(corpus)` computes the bigram frequencies which both pos are 'NNP' in a given corpus. It returns a list of 2-tuples. Each tuple contains the bigram and its frequency.
"""

def get_ngram(corpus):
    vocabulary = Counter()
    for document in corpus:
        document = document.replace("’", "'")
        document = document.replace("‘", "'")
        document = document.replace("”", '"')
        document = document.replace("“", '"')
        twograms = list(nltk.ngrams(pos_tag(word_tokenize(document)), 2))
        for idx, value in enumerate(twograms):
            if (value[0][1] == 'NNP' or value[0][1] == 'NNPS') and (value[1][1] == 'NNP' or value[1][1] == 'NNPS'):
                vocabulary.update([value[0][0] + ' ' + value[1][0]])
    return vocabulary

title, corpus, N = get_corpus()
frequent_vocab = get_ngram(corpus)
print(frequent_vocab.most_common(5))

"""#SpaCy"""

import spacy
import math
nlp_model = spacy.load("en_core_web_sm")

"""## Fetching the Corpus
`get_corpus()` reads the CSV file, and then return a list of the news headlines
"""

def get_corpus():
    df = pd.read_csv('https://raw.githubusercontent.com/bshmueli/108-nlp/master/buzzfeed.csv') # https://bit.ly/nlp-buzzfeed
    print("Dataset columns", df.columns)
    print("Dataset size", len(df))
    # Use content instead of title
    corpus = df.content.to_list()
    for idx, doc in enumerate(corpus):
        # Replace empty corpus to empty string
        if str(doc) == 'nan':
            print("empty content {} !!!!".format(idx))
            corpus[idx] = ''
    title = df.title.to_list()
    return title, corpus, len(corpus)

def tokenize(document):
    # Replace spectial punctuation
    document = document.replace("’", "'")
    document = document.replace("‘", "'")
    document = document.replace("”", '"')
    document = document.replace("“", '"')
    lemma_pos = []
    doc = nlp_model(document)
    for token in doc:
        # Remove stopwords, punctuation, and space
        if not token.is_stop and not token.is_punct and token.pos_ != 'SPACE':
            lemma_pos.append(token.lemma_ + '_' + token.pos_)
    return lemma_pos

"""## Computing word frequencies
`get_vocab(corpus)` computes the word frequencies in a given corpus. It returns a list of 2-tuples. Each tuple contains the token and its frequency.
"""

def get_vocab(corpus):
    vocabulary = Counter()
    total_lemma_pos = []
    for document in corpus:
        lemma_pos = tokenize(document)
        total_lemma_pos.append(lemma_pos)
        vocabulary.update(lemma_pos)
    return vocabulary, total_lemma_pos

"""## Compute TF-IDF Vector
`doc_to_vec(doc, vocab)` returns a TFIDF vector for document `doc`, corresponding to the presence of a word in `vocab`  
`compute_idf(vocab, corpus)` returns a IDF vector for counting frequencies in all document
"""

def compute_idf():
    idf_vec = []
    for token, freq in vocab:
        appear = 0
        for doc_id, doc in enumerate(total_lemma_pos):
            lemma_pos = total_lemma_pos[doc_id]
            if token in lemma_pos:
                appear += 1
        idf_vec.append(math.log(N / appear))
    return idf_vec

def doc2vec(document):
    lemma_pos = tokenize(document)
    # Compute tf vectors
    tf_vec = []
    for token, freq in vocab:
        tf_vec.append(lemma_pos.count(token))
    # Handle empty content
    if sum(tf_vec) == 0:
        tf_vec = [0 for _ in tf_vec]
    else:
        tf_vec = [float(_) / sum(tf_vec) for _ in tf_vec]
    # Compute tf-idf vectors
    tfidf_vec = [tf * idf for tf, idf in zip(tf_vec, idf_vec)]
    return tfidf_vec

"""Cosine similarity between two numerical vectors"""

def cosine_similarity(vec_a, vec_b):
    assert len(vec_a) == len(vec_b)
    if sum(vec_a) == 0 or sum(vec_b) == 0:
        return 0 # hack
    a_b = sum(i[0] * i[1] for i in zip(vec_a, vec_b))
    a_2 = sum([i * i for i in vec_a])
    b_2 = sum([i * i for i in vec_b])
    return a_b/(math.sqrt(a_2) * math.sqrt(b_2))

def doc_similarity(doc_a, doc_b):
    return cosine_similarity(doc2vec(doc_a), doc2vec(doc_b))

"""## Find Similar Documents
Find and print the $k$ most similar titles to a given title
"""

def k_similar(seed_id, k):
    seed_doc = corpus[seed_id]
    print('> "{}"'.format(title[seed_id]))
    similarities = [doc_similarity(seed_doc, doc) for id, doc in enumerate(corpus)]
    top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i])[-k:] # https://stackoverflow.com/questions/13070461/get-indices-of-the-top-n-values-of-a-list
    nearest = [[title[id], similarities[id]] for id in top_indices]
    print()
    for story in reversed(nearest):
        print('* "{}" ({})'.format(story[0], story[1]))

"""## Test our program"""

SELECTED_CORPUS = 75
title, corpus, N = get_corpus()
vocab, total_lemma_pos= get_vocab(corpus)
vocab = vocab.most_common(512)
idf_vec = compute_idf()
k_similar(SELECTED_CORPUS, 5)

