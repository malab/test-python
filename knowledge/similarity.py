from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# from nltk.corpus import wordnet as wn

documents = (
"The time of being young, early life",
"a young person (especially a young man or boy)  ",
"young people collectively",
"the time of life between childhood and maturity", 
"early maturity; the state of being young or immature or inexperienced",
"an early period of development",
"the freshness and vitality characteristic of a young person"
)

"""
ndocs = []

for doc in documents:
    ndoc = []
    for w in doc.split():
        if wn.synsets(w):
            new = wn.synsets(w)[0].lemmas()[0].name()
            ndoc.append(new)
        else:
            new = w
        
    ndoc = ' '.join(ndoc)
    ndocs.append(ndoc)
"""
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
sims = list(sims[0])
for i, cada in enumerate(sims):
    print((cada, " for sentence ", documents[int(i)]))


