import tensorflow as tf
import numpy as np

#------------------------------
# avoid decoding problems
import sys
import os
#reload(sys)
#sys.setdefaultencoding('utf8')

import pandas as pd
from tqdm import tqdm

# df = pd.read_csv("/media/eightbit/8bit_5tb/NLP_data/Quora/DuplicateQuestion/quora_duplicate_questions.tsv",delimiter='\t')
df = pd.read_csv("quora_duplicate_questions.tsv",delimiter='\t')

# encode questions to unicode
df['question1'] = df['question1'].apply(lambda x: unicode(str(x),"utf-8"))
df['question2'] = df['question2'].apply(lambda x: unicode(str(x),"utf-8"))

if os.path.exists('data/1_df.pkl'):
    print("found model")
    df = pd.read_pickle('data/1_df.pkl')
else:
    print("creating model")
    # exctract word2vec vectors
    import spacy
    nlp = spacy.load('en')

    vecs1 = [doc.vector for doc in nlp.pipe(df['question1'], n_threads=50)]
    vecs1 =  np.array(vecs1)
    df['q1_feats'] = list(vecs1)

    vecs2 = [doc.vector for doc in nlp.pipe(df['question2'], n_threads=50)]
    vecs2 =  np.array(vecs2)
    df['q2_feats'] = list(vecs2)

    # save features
    pd.to_pickle(df, 'data/1_df.pkl')

from scipy.spatial.distance import euclidean
vec1 = df[df['qid1']==97]['q1_feats'].values
vec2 = df[df['qid2']==98]['q2_feats'].values
dist = euclidean(vec1[0], vec2[0])
print("dist btw duplicate: %f" % (dist))


vec1 = df[df['qid1']==91]['q1_feats'].values
vec2 = df[df['qid2']==92]['q2_feats'].values
dist = euclidean(vec1[0], vec2[0])
print("dist btw non-duplicate: %f" % (dist))

##############################################################################
# CREATE TRAIN DATA
##############################################################################
# shuffle df
df = df.reindex(np.random.permutation(df.index))

# set number of train and test instances
num_train = int(df.shape[0] * 0.88)
num_test = df.shape[0] - num_train
print("Number of training pairs: %i"%(num_train))
print("Number of testing pairs: %i"%(num_test))

# init data data arrays
X_train = np.zeros([num_train, 2, 300])
X_test  = np.zeros([num_test, 2, 300])
Y_train = np.zeros([num_train])
Y_test = np.zeros([num_test])

# format data
b = [a[None,:] for a in list(df['q1_feats'].values)]
q1_feats = np.concatenate(b, axis=0)

b = [a[None,:] for a in list(df['q2_feats'].values)]
q2_feats = np.concatenate(b, axis=0)

# fill data arrays with features
X_train[:,0,:] = q1_feats[:num_train]
X_train[:,1,:] = q2_feats[:num_train]
Y_train = df[:num_train]['duplicate'].values

X_test[:,0,:] = q1_feats[num_train:]
X_test[:,1,:] = q2_feats[num_train:]
Y_test = df[num_train:]['duplicate'].values

del b
del q1_feats
del q2_feats
#------------------------------

n_input = 300
n_hidden_1 = 128
n_hidden_2 = 128
n_output = 128



# stdN = 1.0
# weights={
#     'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1], mean=0.0, stddev=stdN)),
#     'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2], mean=0.0, stddev=stdN)),
#     'out': tf.Variable(tf.random_normal([n_hidden_2, n_output], mean=0.0, stddev=stdN))
# }

# biases={
#     'h1': tf.Variable(tf.random_normal([n_hidden_1], mean=0.0, stddev=stdN)),
#     'h2': tf.Variable(tf.random_normal([n_hidden_2], mean=0.0, stddev=stdN)),
#     'out': tf.Variable(tf.random_normal([n_output], mean=0.0, stddev=stdN))
# }

# def createSiameseNNFeed(x, weights, biases):
#     layer_1 = tf.add(tf.matmul(x, weights['h1']), biases['h1'])
#     layer_1 = tf.nn.relu(layer_1)

#     layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['h2'])
#     layer_2 = tf.nn.relu(layer_2)

#     layer_out = tf.add(tf.matmul(layer_2, weights['out']), biases['out'])
#     layer_out = tf.nn.softmax(layer_out)

#     return layer_out

# # placeholder inputs
# y = tf.placeholder("float", [None, 1])
# x1_input = tf.placeholder("float", [None, n_input])
# x2_input = tf.placeholder("float", [None, n_input])

# def contrastive_loss(y_true, y_pred):
#     margin = 1
#     return tf.reduce_mean(tf.matmul(y_true, tf.square(y_pred) + (1 - y_true) * tf.square(tf.max(margin - y_pred, 0))))

# def createSiameseNN(x1_input, x2_input, y, weights, biases):
#     with tf.variable_scope('Siamese') as scope:
#         S1 = createSiameseNNFeed(x1_input, weights, biases)
#         scope.reuse_variables()
#         S2 = createSiameseNNFeed(x2_input, weights, biases)

#     print(S1)
#     learning_rate = 0.001
#     # dist between two siames outputs
#     print(tf.sub(S1, S2))
#     print(tf.square(tf.sub(S1, S2)))
#     print(tf.reduce_sum(tf.square(tf.sub(S1, S2)), 1))
#     print(tf.sqrt(tf.reduce_sum(tf.square(tf.sub(S1, S2)), 1)))
#     euc_dist = tf.reshape(tf.sqrt(tf.reduce_sum(tf.square(tf.sub(S1, S2)), 1)), [None, 1])
#     euc_dist = np.transpose(euc_dist)
#     print(euc_dist)
#     print(y)
#     # euc_dist = tf.cast(euc_dist, tf.float32)
#     # LEARNING
#     # loss_euc = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=euc_dist))
#     loss_euc = tf.reduce_mean(contrastive_loss(y, euc_dist))
#     optimiser = tf.train.AdamOptimizer(learning_rate).minimize(loss_euc)
#     # ACCURACY
#     correct_pred = tf.equal(tf.cast(euc_dist < 0.5, tf.float32), y)
#     accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
#     return optimiser, accuracy

# siaNN, accuracy = createSiameseNN(x1_input, x2_input, y, weights, biases)
# epochs = 1
# batchSize = 130#128
# batchRate = int(np.floor(np.shape(X_train)[0] / batchSize))

# init = tf.global_variables_initializer()

# with tf.Session() as sess:
#     sess.run(init)

#     print(np.shape(X_train))
#     print(np.shape(Y_train))
#     for i in range(epochs):
#         for b in range(batchRate - 1):

#             startB = b*batchSize
#             endB = (b+1)*batchSize
#             x1Batch = np.reshape(X_train[startB:endB, 0, :], (batchSize, n_input))
#             print(np.shape(x1Batch))
#             x2Batch = np.reshape(X_train[startB:endB, 1, :], (batchSize, n_input))
#             print(np.shape(x2Batch))
#             yBatch = np.reshape(Y_train[startB:endB], (batchSize, 1))
#             print(np.shape(yBatch))

#             sess.run(siaNN, {x1_input: x1Batch, x2_input: x2Batch, y: yBatch})

#             train_accuracy = accuracy.eval({x1_input: x1Batch, x2_input: x2Batch, y: yBatch})
#             print("train accuracy, {}: {}".format(i, train_accuracy))

#     test_accuracy = accuracy.eval({x1_input: X_test[:,0,:], x2_input: X_test[:, 1, :], y: Y_test})
#     print("test accuracy: {}".format(test_accuracy))


#     sess.close()


