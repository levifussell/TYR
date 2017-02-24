import numpy as np
import pandas as pd
import cPickle
import os

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

categories = ['alt.atheism', 'soc.religion.christian', 'comp.graphics', 'sci.med']

# twenty_train = fetch_20newsgroups(subset='train',
        # categories=categories, shuffle=True, random_state=42)

# count_vect = CountVectorizer()
# X_train_counts = count_vect.fit_transform(twenty_train.data)

# tf_transformer = TfidfTransformer().fit(X_train_counts)

# qs = ["Where is a zebra?", "What is a zebra?"]
# qsT = tf_transformer.transform(count_vect.transform(qs))
# print(qsT)
# print(np.shape(qsT))
# qComp = cosine_similarity(qsT)
# print(qComp)

def classify(q1, q2):
    tfidf, count = createOrLoadModel()

    q1T = tfidf.transform(count.transform(q1))
    q2T = tfidf.transform(count.transform(q2))

    cosSim = cosine_similarity(q1T, q2T)
    return cosSim >= 0.5

def createOrLoadModel():
    if os.path.exists('TFIDF.cpickle'):
        print('FOUND MODEL')
        with open('TFIDF.cpickle') as f:
            tfidf = cPickle.load(f)
        with open('COUNT.cpickle') as f:
            count = cPickle.load(f)

        return tfidf, count
    else:
        print('NEW MODEL')
        df = pd.read_csv("quora_duplicate_questions.tsv", delimiter='\t')

        # encode questions to unicode
        df['question1'] = df['question1'].apply(lambda x: unicode(str(x),"utf-8"))
        df['question2'] = df['question2'].apply(lambda x: unicode(str(x),"utf-8"))

        # allQuestions = np.concatenate((df['question1'].values, df['question2'].values))
        # allSimilarities = np.concatenate((df['is_duplicate'].values, df['is_duplicate'].values))
        # dataSize = np.shape(allQuestions)
        trainPercent = 0.8
        # trainSize = np.shape(allQuestions)[0] * trainPercent
        # trainDataX = allQuestions[:trainSize]
        trainDataQ1 = df['question1'].values[:(np.shape(df['question1'])[0] * trainPercent)]
        trainDataQ2 = df['question2'].values[:(np.shape(df['question2'])[0] * trainPercent)]
        trainDataSim = df['is_duplicate'].values[:(np.shape(df['is_duplicate'])[0] * trainPercent)]

        testDataQ1 = df['question1'].values[(np.shape(df['question1'])[0] * trainPercent):]
        testDataQ2 = df['question2'].values[(np.shape(df['question2'])[0] * trainPercent):]
        testDataSim = df['is_duplicate'].values[(np.shape(df['is_duplicate'])[0] * trainPercent):]
        # rx = re.compile('\W+')
        # for i in trainDataX:
            # if len(i) > 100:
                # res = rx.sub(' ', i).strip()
                # trainDataX2.append(res)

        # trainDataX = trainDataX2
        # print("size of train: {}".format(np.shape(trainDataX)))
        # testDataX = allQuestions[trainSize:]
        # testDataY = allSimilarities[trainSize:]
        # print(testDataY)
        # print("size of test: {}".format(np.shape(testDataX)))
        # print(type(trainDataX))
        print(np.shape(testDataQ1))
        print(np.shape(testDataQ2))
        print(np.shape(testDataSim))

        trainDataQs = np.concatenate((trainDataQ1, trainDataQ2))
        count_vect = CountVectorizer()
        X_train_counts = count_vect.fit_transform(trainDataQs)
        tfidfTrans = TfidfTransformer(smooth_idf=False)
        tfidfTrans.fit_transform(X_train_counts)

        # TEST
        #CALC Q1
        q1T = tfidfTrans.transform(count_vect.transform(testDataQ1))
        print(np.shape(q1T))
        #CALC Q2
        q2T = tfidfTrans.transform(count_vect.transform(testDataQ2))
        print(np.shape(q2T))
        #PERFORM cosine similarity
        probThresh = 0.5
        numCorrect = 0
        for i in range(0, np.shape(q1T)[0]):
            aCos = cosine_similarity(q1T[i, :], q2T[i, :])
            pred = (int)(aCos[0][0] >= 0.5)
            # print(aCos[0][0])
            # print(pred)
            # print(testDataSim[i])
            # print('---------------------------------')
            if pred == testDataSim[i]:
                numCorrect += 1
            # print(aCos)
            # print('--------------------------')
        print("correc num:{}".format(numCorrect))
        accuracy = float(numCorrect) / float(np.shape(q1T)[0])
        print("accuracy: {}".format(accuracy))

        # save the model
        with open('TFIDF.cpickle', 'wb') as f:
            cPickle.dump(tfidfTrans, f)
        with open('COUNT.cpickle', 'wb') as f:
            cPickle.dump(count_vect, f)

        return tfidfTrans, count_vect
