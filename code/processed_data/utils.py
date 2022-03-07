import itertools
from tqdm import tqdm
import numpy as np
from bisect import bisect_left
import spacy
from spacy.lang.de import German
nlp = German()
tokenizer = nlp.tokenizer

def index_sorted_list(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise ValueError


def lookup_embeddings(text, vocab, embedding_matrix):
    'For a given list of words, create embedding matrix'
    embeddings = np.zeros([len(text), embedding_matrix.shape[1]])

    for iword, word in enumerate(text):
        for token in tokenizer(str(word)):
            try:
                embeddings[iword] = embedding_matrix[index_sorted_list(vocab, word)]
            except ValueError:
                pass

    return embeddings


def word_attribute_association(w, A, B, vocab, embedding_matrix):
    # s(w,A,B) = mean_a cos(w,a) - mean_b cos(w,b)
    A_embed = lookup_embeddings(A, vocab, embedding_matrix)
    B_embed = lookup_embeddings(B, vocab, embedding_matrix)
    w_embed = lookup_embeddings(w, vocab, embedding_matrix)

    wA = np.dot(w_embed / np.linalg.norm(w_embed, axis=1)[:, np.newaxis],
                (A_embed / np.linalg.norm(A_embed, axis=1)[:, np.newaxis]).T).sum()
    wB = np.dot(w_embed / np.linalg.norm(w_embed, axis=1)[:, np.newaxis],
                (B_embed / np.linalg.norm(B_embed, axis=1)[:, np.newaxis]).T).sum()

    return wA / len(A) - wB / len(B)


def test_statistic(A, B, X, Y, vocab, embedding_matrix):
    wA = 0

    for ix in X:
        wA += word_attribute_association([ix], A, B, vocab, embedding_matrix)

    wB = 0

    for iy in Y:
        wB -= word_attribute_association([iy], A, B, vocab, embedding_matrix)

    return wA + wB


def calculate_pvalue(A, B, X, Y, vocab, embedding_matrix, alpha=0.05):
    # check out-of-vocab words
    A = list(set(A).intersection(vocab))
    B = list(set(B).intersection(vocab))
    X = list(set(X).intersection(vocab))
    Y = list(set(Y).intersection(vocab))

    test_stat_orig = test_statistic(A, B, X, Y, vocab, embedding_matrix)

    union = set(X + Y)
    subset_size = len(union) // 2

    larger = 0
    total = 0

    for subset in tqdm(set(itertools.combinations(union, subset_size))):
        total += 1
        Xi = list(set(subset))
        Yi = list(union - set(subset))
        if test_statistic(A, B, Xi, Yi, vocab, embedding_matrix) > test_stat_orig:
            larger += 1
    if larger / float(total) < alpha:
        print(
            "The difference between the attributes {} and {} \nfor the given target words is significant.".format(A, B))
    else:
        print(
            "The difference between the attributes {} and {} \nfor the given target words is not significant.".format(A,
                                                                                                                      B))

    return larger / float(total)