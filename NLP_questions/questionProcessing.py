import numpy as np
import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfTransformer

stopWords = {

}

df = pd.read_csv("../../../../Datasets/quora_duplicate_questions.tsv", delimiter='\t')

# encode questions to unicode
df['question1'] = df['question1'].apply(lambda x: unicode(str(x),"utf-8"))
df['question2'] = df['question2'].apply(lambda x: unicode(str(x),"utf-8"))

allQuestions = np.concatenate((df['question1'].values, df['question2'].values))
allSimilarities = np.concatenate((df['is_duplicate'].values, df['is_duplicate'].values))
dataSize = np.shape(allQuestions)
trainPercent = 0.8
trainSize = np.shape(allQuestions)[0] * trainPercent
trainDataX = allQuestions[:trainSize]
trainDataX2 = []
rx = re.compile('\W+')
for i in trainDataX:
    if len(i) > 100:
        res = rx.sub(' ', i).strip()
        trainDataX2.append(res)

trainDataX = trainDataX2
print("size of train: {}".format(np.shape(trainDataX)))
testDataX = allQuestions[trainSize:]
print("size of test: {}".format(np.shape(testDataX)))
print(type(trainDataX))

tfidfTrans = TfidfTransformer(smooth_idf=False)
tfidfTrans.fit_transform(trainDataX)
print(tfidfTrans)

print(allQuestions)
