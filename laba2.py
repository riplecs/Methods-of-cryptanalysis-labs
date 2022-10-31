# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 12:47:22 2022

@author: Daria
"""
import re
import math
import random
import numpy as np
import pandas as pd


file = open('znedoleni.txt', 'r')

alphabet = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
m = len(alphabet)

text = ''
for line in file:
    text += line
text = text.replace('ґ', 'г')
clean_text = re.sub(f'[^{alphabet}]', '', text.lower())

L_text = len(clean_text)
alph = list(alphabet)

letter_freqs = [clean_text.count(i)/L_text for i in alph]
print(pd.DataFrame(np.matrix(letter_freqs), columns = alph, index = ['']))

bigrams = [f'{i}{j}' for i in alph for j in alph]

def count_enters(text, bigram):
    count, start = 0, 0
    while start < len(text):
        pos = text.find(bigram, start)
        if pos != -1:
            start = pos + 1
            count += 1
        else:
            break
    return count

bigram_freqs = [count_enters(clean_text, i)/(L_text - 1) 
                for i in bigrams]

print(pd.DataFrame(np.array(bigram_freqs).reshape((m, m)), 
                   columns = alph, index = alph))

entropy_per_letter = sum(-f*math.log2(f) for f in letter_freqs)
print(entropy_per_letter)
entropy_per_bigram = sum((-f*math.log2(f) if f > 0 else 0) 
                         for f in bigram_freqs)/2
print(entropy_per_bigram)
letter_index =  sum(clean_text.count(i)*(clean_text.count(i) - 1)
                   for i in alph)/(L_text*(L_text - 1))
print(letter_index)
bi_index =  sum(count_enters(clean_text, i)*(count_enters(clean_text, i) - 1)
                   for i in bigrams)/(L_text*(L_text - 1))
print(bi_index)


def gen_texts(text, l, n):
    texts = []
    for i in range(n):
        start = random.randint(0, L_text - l - 1)
        texts.append(text[start : start + l])
    return texts

def gen_Vigenere_key():
    r = random.choice([1, 5, 10])
    return random.choices(range(m), k = r)

def  Vigenere(text):
    key = gen_Vigenere_key()
    text = [alph.index(t) for t in text]
    cipher_text = [(t + key[text.index(t)%len(key)])%m for t in text]
    return ''.join([alph[c] for c in cipher_text])

    
def gen_affine_keys(l):
    a = random.randint(1, m**l - 1)
    while math.gcd(a, m) != 1:
        a = random.randint(1, m**l - 1)
    b = random.randint(0, m**l - 1)
    return a, b

def convert_bigrams(text):
    return [(text[i]*m + text[i + 1])%m**2 
            for i in range(0, len(text) - 1, 2)]


def deconvert_bigrams(cipher_text):
    new_cipher_text = []
    for c in cipher_text:
        new_cipher_text.append(c//m)
        new_cipher_text.append(c%m)
    return new_cipher_text
    

def Affine(text, l):
    a, b = gen_affine_keys(l)
    text = [alph.index(t) for t in text]
    if l == 2:
        text = convert_bigrams(text)
    cipher_text = [(a*t+b)%m**l for t in text]
    if l == 2:
        cipher_text = deconvert_bigrams(cipher_text)
    return ''.join(alph[c] for c in cipher_text)

def uniform_text(l, length):
    Zm = alph if l == 1 else bigrams
    length = length//l
    return ''.join([random.choice(Zm) for i in range(length)])
    

def fibonacci_text(l, length):
    Zm = range(m) if l == 1 else convert_bigrams([alph.index(t) 
                                    for t in ''.join([b for b in bigrams])])
    length = length//l
    s0, s1 = random.choices(Zm, k = 2)
    y = [s0, s1]
    for i in range(length - 2):
        y.append((y[i] + y[i + 1])%m**l)
    if l == 2:
        y = deconvert_bigrams(y)
    return ''.join([alph[y_i] for y_i in y])
    

def criterion2_0(text):
    return all(elem in np.unique(text) for elem in Afrq)
        

def criterion2_1(text, threshold2 = 0.8):
    Aaf = [elem for elem in np.unique(text) if elem in Afrq]
    return len(list(set(Afrq)&set(Aaf))) > len(Afrq)*threshold2
    
def criterion2_2(L, l, text):
    return all([Afrq_text_freqs >= Afrq_alph_freqs])
    
def criterion2_3(L, l, text):
    return sum(Afrq_text_freqs) >= sum(Afrq_alph_freqs)

def criterion4(L, l, text):
    text_nums = [text.count(i) for i in Zm]
    index = sum(i*(i - 1) for i in text_nums)/(L*(L - 1))
    true_index = letter_index if l == 1 else bi_index
    return abs(index - true_index) <= 0.001

letter_freqs_median = np.median(letter_freqs)
bigram_freqs_median = np.median(bigram_freqs)

for L in (10, 100, 1000, 10000):
    N = (10000 if L != 10000 else 1000)
    texts = gen_texts(clean_text, L, N)
    for l in (1, 2):
        Zm = alph if l == 1 else bigrams
        freqs = letter_freqs if l == 1 else bigram_freqs
        threshold  = letter_freqs_median if l == 1 else bigram_freqs_median
        Afrq = [Zm[freqs.index(i)] for i in freqs if i > threshold]
        Afrq_alph_freqs = [freqs[Zm.index(el)] for el in Afrq]
        a, b = 0, 0
        '''
        for text in texts:
            Afrq_text_freqs = [count_enters(text, i)/(L - l + 1) 
                               for i in Afrq]
            a += (1 - int(criterion4(L, l, [text[i:i + l] 
                                        for i in range(L - l + 1)])))
            cipher_text = Vigenere(text)
            b += int(criterion4(L, l, [cipher_text[i:i + l] 
                                   for i in range(L - l + 1)]))
        print('_____Criterion 4.0_____')
        print(f'L = {L}, l = {l}')
        print('False positive = ', a/N)  
        print('False negative = ', b/N)      '''        
        
        

l = 2
print(criterion4(10000, l, clean_text[:10000]))
print(criterion4(10000, l, uniform_text(l, 10000)))
print(criterion4(10000, l, fibonacci_text(l, 10000)))

