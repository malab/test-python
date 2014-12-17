'''
Created on 4/11/2014

@author: aurelio
'''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Similar(object):
    '''
    classdocs
    '''
    def analyze(self):
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(self.documents)
        
        sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
        sims = list(sims[0])
        return sims[1]
        """
        for i, cada in enumerate(sims):
            return((cada, " for sentence ", self.documents[int(i)]))
        """
    def __init__(self, docs):
        '''
        Constructor
        '''
        self.documents = docs
        
docs = []
doc1 = 'Islam'
doc2 = 'Musulmanes'
docs.append(doc1.replace('_', ' '))
docs.append(doc2.replace('_', ' '))
sim = Similar(docs).analyze()

from pprint import pprint
pprint(sim)

