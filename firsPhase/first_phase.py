import os
import simplejson
import xlrd
from future.moves import itertools
from nltk import word_tokenize
import csv
from past.builtins import reduce

'''for reading HTML'''
# page = urlopen(new_url)
# html_bytes = page.read()
# html = html_bytes.decode("utf-8")

loc = "IR_Spring2021_ph12_7k.xlsx"
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
doc_dictionary = {}
inverted_index = {}
resulted_tokens = {}
value_list = []
resulted_doc_list = []


def remove_links(inverted_dict):
    sub_list = ['jpg', 'https']
    res = list(inverted_dict.keys())
    for key in res:
        for item in sub_list:
            if item in key:
                inverted_dict.pop(key)
    return inverted_dict


def remove_punctuations(inverted_dict):
    keys = [':', '.', '،', '(', ')', ']', '[', '!', '@', '?', "''", '""', '##', '#', '*', '**']
    for key in keys:
        inverted_dict.pop(key, None)
    return inverted_dict


def remove_prefix(inverted_dict):
    prefix = ['ها', 'های', 'ترین', 'تر', 'ات']
    for pref in prefix:
        inverted_dict.pop(pref, None)
    return inverted_dict


def find_verbs_root(inverted_dict):
    with open('verbs.csv', encoding="utf8") as csv_file_read:
        csv_reader = csv.reader(csv_file_read, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                bon_mozare = row[0]
                bon_mazi = row[1]
                line_count += 1
                for token in list(inverted_dict.keys()):
                    if len(token) > 3:
                        if token[-2:] == 'یم' or token[-2:] == 'ید' or token[-2:] == 'ند' or token[-1] == 'ی' or token[-1] == 'م':
                            if token[:-2] == bon_mazi or token[:-2] == bon_mozare:
                                if token[:-2] in inverted_dict:
                                    for idd in inverted_dict[token]:
                                        list(inverted_dict[token[:-2]]).append(idd)
                                    inverted_dict.pop(token)
                                else:
                                    for idd in inverted_dict[token]:
                                        inverted_dict[token[:-2]] = [idd]
                                    inverted_dict.pop(token)
                            elif token[:-1] == bon_mazi or token[:-1] == bon_mozare:
                                if token[:-1] in inverted_dict:
                                    for idd in inverted_dict[token]:
                                        list(inverted_dict[token[:-1]]).append(idd)
                                    inverted_dict.pop(token)
                                else:
                                    for idd in inverted_dict[token]:
                                        inverted_dict[token[:-1]] = [idd]
                                    inverted_dict.pop(token)
    return inverted_dict


# all verbs have Pronoun except one so we handle this using pronouns
# and we make sure that verb root is valid and it is available in our lists
def handling_present_tenses(inverted_dict):
    with open('verbs.csv', encoding="utf8") as csv_file_read:
        csv_reader = csv.reader(csv_file_read, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                bon_mozare = row[0]
                bon_mazi = row[1]
                line_count += 1
                for token in list(inverted_dict.keys()):
                    if len(token) >= 5:
                        if token[0:2] == 'می':
                            if token[-2:] == 'یم' or token[-2:] == 'ید' or token[-2:] == 'ند':
                                verb_root = token[2:-2]
                                if verb_root in inverted_dict:
                                    for idd in inverted_dict[token]:
                                        list(inverted_dict[verb_root]).append(idd)
                                    inverted_dict.pop(token)
                                else:
                                    for idd in inverted_dict[token]:
                                        inverted_dict[verb_root] = [idd]
                                    inverted_dict.pop(token)
                            elif token[-1] == 'ی' or token[-1] == 'م':
                                verb_root = token[2:-1]
                                if verb_root == bon_mozare or verb_root == bon_mazi:
                                    if verb_root in inverted_dict:
                                        for idd in inverted_dict[token]:
                                            list(inverted_dict[verb_root]).append(idd)
                                        inverted_dict.pop(token)
                                    else:
                                        for idd in inverted_dict[token]:
                                            inverted_dict[verb_root] = [idd]
                                        inverted_dict.pop(token)
                            else:
                                verb_root = token[2:]
                                if verb_root == bon_mozare or verb_root == bon_mazi:
                                    if verb_root in inverted_dict:
                                        for idd in inverted_dict[token]:
                                            list(inverted_dict[verb_root]).append(idd)
                                        inverted_dict.pop(token)
                                    else:
                                        for idd in inverted_dict[token]:
                                            inverted_dict[verb_root] = [idd]
                                        inverted_dict.pop(token)
    return inverted_dict


def homogenization(inverted_dict):
    for token in list(inverted_dict.keys()):
        check_token = token[:-1]
        if token[-1] == 'ء':
            if check_token in inverted_dict:
                for idd in inverted_dict[token]:
                    inverted_dict[check_token].append(idd)
                inverted_dict.pop(token)
    return inverted_dict


def remove_frequent_tokens(inverted_dict):
    for token in list(inverted_dict.keys()):
        if len(inverted_dict[token]) >= 3000:
            inverted_dict.pop(token)
    return inverted_dict


def find_plurals_root(inverted_dict):
    with open('plural.csv', encoding="utf8") as csv_file_read:
        csv_reader = csv.reader(csv_file_read, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                mofrad = row[0]
                jam = row[1]
                line_count += 1
                for token in list(inverted_dict.keys()):
                    if token == jam:
                        if mofrad in inverted_dict:
                            for idd in inverted_dict[token]:
                                inverted_dict[mofrad].append(idd)
                            inverted_dict.pop(token)
                        else:
                            for idd in inverted_dict[token]:
                                inverted_dict[mofrad] = [idd]
                            inverted_dict.pop(token)
    return inverted_dict


def remove_stop_words(inverted_dict):
    stop_words = [word for word in open('StopWords.txt' , 'r' , encoding='utf8').read().split('\n')]
    for word in stop_words:
        if word in inverted_dict:
            inverted_dict.pop(word)
    return inverted_dict


def unify_the_letters(inverted_dict):
    changed = ''
    for token in list(inverted_dict.keys()):
        if "ي" in token:
            changed = token.replace("ي", "ی")
        if "ك" in token:
            changed = token.replace("ك", "ک")
        if len(token) > 0:
            if "ا" == token[0]:
                changed = token.replace("آ", "ا")
        if changed in inverted_dict:
            # print(changed)
            for idd in inverted_dict[token]:
                inverted_dict[changed].append(idd)
            inverted_dict.pop(token)
        else:
            for idd in inverted_dict[token]:
                inverted_dict[changed] = [idd]
            inverted_dict.pop(token)
    return inverted_dict


def creating_inverted_index():
    for ii in range(1, 7001):
        print(ii)
        url = sheet.cell_value(ii, 2)
        doc_id = int(sheet.cell_value(ii, 0))
        content = sheet.cell_value(ii, 1)
        doc_dictionary[doc_id] = url
        nltk_tokens = word_tokenize(content)
        for index in nltk_tokens:
            if index in inverted_index:
                if doc_id not in inverted_index[index]:
                    inverted_index[index].append(doc_id)
            else:
                inverted_index[index] = [doc_id]


def write_dict(dict_name, filename):
    with open(filename, "w", encoding='utf-8') as json_file:
        simplejson.dump(dict_name, json_file, ensure_ascii=False)


def read_dict(filename):
    with open(filename , 'r', encoding='utf8') as json_file:
        data = simplejson.load(json_file)
    return data


if os.stat('results.txt').st_size == 0:
    creating_inverted_index()
    print("before: ", len(inverted_index))
    inverted_index = remove_links(inverted_index)
    print("after links removed: ", len(inverted_index))
    # inverted_index = unify_the_letters(inverted_index)
    # print("after unifying letters", len(inverted_index))
    inverted_index = remove_prefix(inverted_index)
    print("after remove prefix", len(inverted_index))
    inverted_index = homogenization(inverted_index)
    print("after homogenization", len(inverted_index))
    inverted_index = find_verbs_root(inverted_index)
    print("after rooting", len(inverted_index))
    inverted_index = remove_frequent_tokens(inverted_index)
    print("after remove frequents", len(inverted_index))
    inverted_index = find_plurals_root(inverted_index)
    print("after plural rooting", len(inverted_index))
    inverted_index = remove_punctuations(inverted_index)
    print("after punctuation removed: ", len(inverted_index))
    inverted_index = remove_stop_words(inverted_index)
    print("after stopwords removed: ", len(inverted_index))
    inverted_index = handling_present_tenses(inverted_index)
    print("after handling present tenses: ", len(inverted_index))
    write_dict(inverted_index , 'results.txt')
else:
    inverted_index = read_dict('results.txt')
    # query = input('enter your query')
    query = 'دریافت منابع تریپتوفان'
    query_token = word_tokenize(query)
    for t in query_token:
        resulted_tokens[t] = sorted(inverted_index[t])
        value_list.append(list(resulted_tokens[t]))
    for i in range(len(query_token)):
        if len(query_token) - i == 0 :
            break
        print(f'results which contains {len(query_token)-i} words')
        for combination in list(itertools.combinations(value_list, len(query_token) - i)):
            resulted_doc_list = list(reduce(set.intersection, [set(item) for item in combination]))
            for d_id in sorted(resulted_doc_list):
                res_url = sheet.cell_value(d_id, 2)
                print(d_id, res_url)
                for item in combination:
                    item.remove(d_id)











