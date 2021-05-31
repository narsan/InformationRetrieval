import nltk
import xlrd
from urllib.request import urlopen
import re
import urllib.parse
from urllib.request import urlopen
from urllib.parse import quote
import csv

'''for reading HTML'''
# page = urlopen(new_url)
# html_bytes = page.read()
# html = html_bytes.decode("utf-8")


loc = "IR_Spring2021_ph12_7k.xlsx"
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
doc_dictionary = {}
inverted_index = {}


# 7001
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
                                    pass
                            elif token[:-1] == bon_mazi or token[:-1] == bon_mozare:
                                if token[:-1] in inverted_dict:
                                    for idd in inverted_dict[token]:
                                        list(inverted_dict[token[:-1]]).append(idd)
                                    inverted_dict.pop(token)
                                else:
                                    pass
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
                changed = token.replace("ا", "آ")
        if changed in inverted_dict:
            # print(changed)
            for idd in inverted_dict[token]:
                inverted_dict[changed].append(idd)
            inverted_dict.pop(token)
        # else:
        #     inverted_dict[changed] = inverted_dict.pop(token)
    return inverted_dict


for i in range(1, 10):
    # print(i)
    url = sheet.cell_value(i, 2)
    first = url.rsplit('/', 1)[0] + '/'
    second = url.rsplit('/', 1)[1]
    new_url = first + quote(second)
    doc_id = int(sheet.cell_value(i, 0))
    content = sheet.cell_value(i, 1)
    doc_dictionary[content] = [new_url, doc_id]
    nltk_tokens = nltk.word_tokenize(content)
    for index in nltk_tokens:
        if index in inverted_index:
            if doc_id not in inverted_index[index]:
                inverted_index[index].append(doc_id)
        else:
            inverted_index[index] = [doc_id]

    # print('url = ', new_url)
    # print('doc_id = ', doc_id)
    # print('content = ', content)
print("before: ", len(inverted_index))
inverted_index = remove_links(inverted_index)
print("after links removed: ", len(inverted_index))
inverted_index = unify_the_letters(inverted_index)
print("after unifying letters", len(inverted_index))
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
print(inverted_index)




# print(inverted_index)


# page = urlopen(url)
# html_bytes = page.read()
# html = html_bytes.decode("utf-8")
# print(html)
