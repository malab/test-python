"""
Non-interactive demonstration of the clusterers with simple 2-D data.
"""

from nltk import cluster
import numpy

# example from figure 14.10, page 519, Manning and Schutze

vectors = [numpy.array(f) for f in [[0.5, 0.5], [1.5, 0.5], [1, 3]]]
means = [[4, 2], [4, 2.01]]

clusterer = cluster.EMClusterer(means, bias=0.1)
clusters = clusterer.cluster(vectors, True, trace=True)

print('Clustered:', vectors)
print('As:       ', clusters)
print()

for c in range(2):
    print('Cluster:', c)
    print('Prior:  ', clusterer._priors[c])
    print('Mean:   ', clusterer._means[c])
    print('Covar:  ', clusterer._covariance_matrices[c])
    print()

# classify a new vector
vector = numpy.array([2, 2])
print('classify(%s):' % vector, end=' ')
print(clusterer.classify(vector))

# show the classification probabilities
vector = numpy.array([2, 2])
print('classification_probdist(%s):' % vector)
pdist = clusterer.classification_probdist(vector)
for sample in pdist.samples():
    print('%s => %.0f%%' % (sample,
                pdist.prob(sample) *100))

#
#     The following demo code is broken.
#
#     # use a set of tokens with 2D indices
#     vectors = [numpy.array(f) for f in [[3, 3], [1, 2], [4, 2], [4, 0], [2, 3], [3, 1]]]

#     # test the EM clusterer with means given by k-means (2) and
#     # dimensionality reduction
#     clusterer = cluster.KMeans(2, euclidean_distance, svd_dimensions=1)
#     print 'Clusterer:', clusterer
#     clusters = clusterer.cluster(vectors)
#     means = clusterer.means()
#     print 'Means:', clusterer.means()
#     print

#     clusterer = cluster.EMClusterer(means, svd_dimensions=1)
#     clusters = clusterer.cluster(vectors, True)
#     print 'Clusterer:', clusterer
#     print 'Clustered:', str(vectors)[:60], '...'
#     print 'As:', str(clusters)[:60], '...'
#     print

#     # classify a new vector
#     vector = numpy.array([3, 3])
#     print 'classify(%s):' % vector,
#     print clusterer.classify(vector)
#     print

#     # show the classification probabilities
#     vector = numpy.array([2.2, 2])
#     print 'classification_probdist(%s)' % vector
#     pdist = clusterer.classification_probdist(vector)
#     for sample in pdist:
#         print '%s => %.0f%%' % (sample, pdist.prob(sample) *100)
