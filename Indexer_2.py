from nltk.stem import *
import math
import nltk
import string
from nltk.corpus import stopwords
import concurrent.futures
from multiprocessing.dummy import Pool

cachedStopWords = stopwords.words("english")


class Indexer_2:

    def __init__(self, docs):
        self.docs = docs
        self.doc_dict = {}
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=8)
        self.count = 0

    # removes punctuation, removes numbers, lower all letters and tokenize words
    def tokenize(self, read):
        translator = read.translate(str.maketrans('', '', string.punctuation))
        not_numbs = ''.join([i for i in translator if not i.isdigit()])
        not_numbs = not_numbs.lower()
        not_numbs = (not_numbs.encode('ascii', 'ignore')).decode("utf-8")
        nltk_tokens = nltk.word_tokenize(not_numbs)
        return nltk_tokens

    # deletes stop words
    def delete_stop_words(self, words):
        new_words = [w for w in words if w not in cachedStopWords]
        return new_words

    # performs lemmatization on words
    def lemmatization(self, words):
        lemmatizer = WordNetLemmatizer()
        result = [lemmatizer.lemmatize(w, pos='v') for w in words]
        return result

    def delete_puncts(self, read):
        puncts = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
        for i in read:
            if i in puncts:
                read = read.replace(i, ' ')
        return read

    # calculates tf
    def get_tf(self, ntlk_tokens):
        tf = {}
        for word in ntlk_tokens:
            tf[word] = ntlk_tokens.count(word)/len(ntlk_tokens)
        #print("Tf: ", tf)
        return tf

    # calculates idf
    def get_idf(self, doc_dict):
        idf = {}
        unique = self.get_uniques(doc_dict)
        for i in unique:
            count = 0
            for j in doc_dict.values():
                if i in j:
                    count += 1
            idf[i] = math.log10(len(doc_dict)/count+1)
        #print("idf: ", idf)
        return idf

    # calculates tfidf
    def get_tfidf(self, data, idf_s):
        tfidf = {}
        for key, value in data.items():
            tfidf[key] = self.get_tf(value)
        for doc, tf_values in tfidf.items():
            for token, score in tf_values.items():
                tf = score
                idf = idf_s[token]
                tf_values[token] = tf * idf
        #print("tfidf: ", tfidf)
        return tfidf

    def get_uniques(self, data):
        unique = []
        for i in data.values():
            unique = unique + i
        dist = nltk.FreqDist(unique)
        # print(list(dist.keys()))
        return list(dist.keys())

    # get inverted indexer
    def get_indexer(self, data):
        unique = self.get_uniques(data)
        indexer = {}
        for w in unique:
            for docs, token in data.items():
                if w in token:
                    if w in indexer.keys():
                        indexer[w].append(docs)
                    else:
                        indexer[w] = [docs]
        # print("inverted Indexer: ", indexer)
        return indexer

    def process_doc(self):
        for i in self.docs:
            # doc = self.delete_puncts(doc)
            tokens = self.tokenize(i.get_text())
            final_doc = self.lemmatization(tokens)
            self.doc_dict[i.get_num()] = final_doc


    def run_multithread(self):
        # self.file.seek(0)
        # for doc in self.file.readlines():
        #     doc = self.delete_puncts(doc)
        #     tokens = self.tokenize(doc)
        #     final_doc = self.lemmatization(tokens)
        #     self.doc_dict[self.count] = final_doc
        #     self.count += 1

        # with concurrent.futures.ThreadPoolExecutor(max_workers=8) as thread:
        #     res = thread.map(self.process_doc, self.file.readlines())
        self.process_doc()

        # print(self.doc_dict)
        return self.doc_dict

    def get_dict(self):
        return self.doc_dict
