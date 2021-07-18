import os
import simplejson
import xlrd
from nltk import word_tokenize
from parsivar import Normalizer, Tokenizer, FindStems
from collections import Counter
import math

loc = "IR_Spring2021_ph12_7k.xlsx"
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

doc_dictionary = {}
inverted_index = {}
champion_list = {}


def write_dict(dict_name, filename):
    with open(filename, "w", encoding='utf-8') as json_file:
        simplejson.dump(dict_name, json_file, ensure_ascii=False)


def read_dict(filename):
    with open(filename, 'r', encoding='utf8') as json_file:
        data = simplejson.load(json_file)
    return data


def remove_frequent_tokens(inverted_dict):
    for token in list(inverted_dict.keys()):
        if len(inverted_dict[token]) >= 3000:
            inverted_dict.pop(token)
    return inverted_dict


def remove_stop_words(inverted_dict):
    stop_words = [word for word in open('StopWords.txt', 'r', encoding='utf8').read().split('\n')]
    for word in stop_words:
        if word in inverted_dict:
            inverted_dict.pop(word)
    return inverted_dict


def tf_idf(tf, nt, N):
    tfIdf = (1 + math.log(tf)) * (math.log(N / nt))
    return tfIdf


def cosine_score(query_term , inverted_index_dict):
    scores = {}
    total_score_docs = {}
    scr = 0
    for term, count in Counter(query_term).items():
        count = float("{:.4f}".format(tf_idf(count, 1, 7000)))
        scr += count
        scores[term] = count
        for pair in inverted_index_dict[term]:
            if pair[0] in total_score_docs:
                total_score_docs[pair[0]] += pair[1]
            else:
                total_score_docs[pair[0]] = pair[1]
    for key, value in list(total_score_docs.items()):
        if value < scr / 2:
            total_score_docs.pop(key)

    total_score_docs = dict(sorted(total_score_docs.items(), key=lambda item: item[1], reverse=True))
    return total_score_docs


def create_champion_list():
    for term in inverted_index:
        top_scores = []
        max_val = inverted_index[term][0][1]
        for pair in inverted_index[term]:
            if pair[1] > max_val:
                max_val = pair[1]
        for pair in inverted_index[term]:
            if pair[0] not in top_scores and pair[1] > max_val / 2:
                top_scores.append((pair[0] , pair[1]))
        champion_list[term] = top_scores


def position(text, my_list):
    r = []
    point = 0  # Where we're in the text.
    for token in my_list:
        found_start = text.index(token, point)
        found_end = found_start + len(token)
        r.append(found_start)
        point = found_end
    return r


def creating_inverted_index():
    already_in = False
    my_stemmer = FindStems()
    my_normalizer = Normalizer()
    my_tokenizer = Tokenizer()
    for ii in range(1, 7001):
        url = sheet.cell_value(ii, 2)
        doc_id = int(sheet.cell_value(ii, 0))
        content = sheet.cell_value(ii, 1)
        normalized_text = my_normalizer.normalize(content)
        doc_dictionary[doc_id] = url
        words = my_tokenizer.tokenize_words(normalized_text)
        for token, count in Counter(words).items():
            token = my_stemmer.convert_to_stem(token)
            if token not in inverted_index:
                inverted_index[token] = [(doc_id, count), ]
            else:
                count = float("{:.4f}".format(tf_idf(count, len(inverted_index[token]), 7000)))
                for term in inverted_index[token]:
                    if doc_id == term[0]:
                        already_in = True
                if not already_in:
                    inverted_index[token].append((doc_id, count))
                already_in = False


if os.stat('results2.txt').st_size == 0 or os.stat('champions.txt').st_size == 0:
    print('here')
    creating_inverted_index()
    create_champion_list()
    write_dict(inverted_index, 'results2.txt')
    write_dict(champion_list, 'champions.txt')

else:
    inverted_index = read_dict('results2.txt')
    champion_list = read_dict('champions.txt')
    query = input('enter your query: ')
    # query = 'استخراج و تولید زغال سنگ'
    query_token = word_tokenize(query)
    k = int(input("enter the number of results you want to see: "))
    result = cosine_score(query_token , inverted_index)
    '''for using champion lists uncomment below line '''
    # result = cosine_score(query_token , champion_list)
    res = {a: result[a] for a in list(result)[:k]}
    for d_id in res.keys():
        res_url = sheet.cell_value(d_id, 2)
        print('document', d_id, 'with url:', res_url)
