from Indexer_2 import Indexer_2
import numpy as np


class Query:

    def __init__(self, dict_doc, idf, tfidf):
        self.dict_doc = dict_doc

        self.idf = idf
        self.docs_tf_idf = tfidf
        self.query_idf = {}
        self.query_tf = {}
        self.query_tf_idf = {}

        self.query = []
        self.relevant_docs = []
        self.cos_sim = {}
        self.run_query()

    def get_input(self):
        self.query = str(input("What do you want to search? ")).lower().split(' ')

    def preprocess_query(self):
        # we are passing the inverted indexer
        self.get_input()
        # Query's tf
        self.calc_query_tf()
        # Find relevant docs
        self.find_relevant_docs()
        # Query's tf-idf
        self.calc_tf_idf()
        self.calc_cosine_similarity()


    # Calculate the tf of the query
    def calc_query_tf(self):
        for word in self.query:
            self.query_tf[word] = self.query.count(word)/len(self.query)

    # relevant docs with the query
    def find_relevant_docs(self):
        to_delete = []
        for word in self.query:
            try:
                for rel_doc in self.dict_doc[word]:
                    if rel_doc not in self.relevant_docs:
                        self.relevant_docs.append(rel_doc)
            except KeyError:
                print("We couldnt find the word: {} in documents".format(word))
                to_delete.append(word)
        # print(self.relevant_docs)

    # calculate the tf-idf of the query
    def calc_tf_idf(self):
        for word in self.query:
            try:
                self.query_tf_idf[word] = self.idf[word] * self.query_tf[word]
            except KeyError:
                self.query_tf_idf[word] = 0

    def calc_cosine_similarity(self):
        for doc in self.relevant_docs:
            doc_vector = []
            query_vector = []
            for word in self.query:
                    # Take the relevant doc
                    doc_tfidf = self.docs_tf_idf[doc]
                    # From the relevant doc take the td-idf of the word
                    try:
                        doc_vector.append(doc_tfidf[word])
                    except KeyError:
                        doc_vector.append(0)
                    # From the Query take the tf-idf of the word
                    try:
                        query_vector.append(self.query_tf_idf[word])
                    except KeyError:
                        query_vector.append(0)

            self.cos_sim[doc] = self.some_calcs(doc_vector, query_vector)

    def some_calcs(self, x1, x2):
        sums = sum(x[0]*x[1] for x in zip(x1, x2))
        norm = np.linalg.norm(x1) * np.linalg.norm(x2)
        return sums/norm

    def run_query(self):
        self.preprocess_query()

    def top_k(self, dic_doc, k):
        counter = 1
        sorted_dic = {key: value for key, value in sorted(self.cos_sim.items(), key=lambda item: item[1], reverse=True)}
        for i in sorted_dic.keys():
            print(counter, ": ", dic_doc[i].get_url())
            if counter >= k or counter > len(sorted_dic):
                return
            counter += 1
        relevance = input("Feedback: Which docs were more relevant? (etc 1 2 7) ")
        return
