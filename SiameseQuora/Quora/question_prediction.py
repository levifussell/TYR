import os
import sys
import pandas as pd
import numpy as np
import spacy
from siamese import *
from keras.models import load_model
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

np.set_printoptions(precision=4)
if os.path.exists('final_tf_idf_vec.h5'):
	model = load_model('final_tf_idf_vec.h5',custom_objects={'contrastive_loss': contrastive_loss})
	if os.path.exists("raw_question.tsv"):
		raw_question = pd.read_csv("raw_question.tsv",delimiter = '\t')

		if os.path.exists('current_question.tsv'):
			current_question = pd.read_csv("current_question.tsv",delimiter = '\t')
			for i in current_question:
				for j in raw_question:
					pred = model.predict([i,j],batch_size=128)
					print(pred)
		else:
			raw_question['question'] = raw_question['question'].apply(lambda x: unicode(str(x),"utf-8"))


			# merge texts
			questions = list(raw_question['question'])

			tfidf = TfidfVectorizer(lowercase=False, )
			tfidf.fit_transform(questions)

			# dict key:word and value:tf-idf score
			word2tfidf = dict(zip(tfidf.get_feature_names(), tfidf.idf_))
			del questions



			nlp = spacy.load('en')
    
    		vecs1 = []
    		for qu in tqdm(list(raw_question['question'])):
    			doc = nlp(qu) 
    			mean_vec = np.zeros([len(doc), 300])
    			for word in doc:
        			# word2vec
        			vec = word.vector
        			#print(vec)
        			#print(word)
            		# fetch df score
            		try:
                		idf = word2tfidf[str(word)]
            		except:
                		#print word
                		idf = 0
            		# compute final vec
            		mean_vec += vec * idf
        		mean_vec = mean_vec.mean(axis=0)
        		vecs1.append(mean_vec)
        	print(list(vecs1))
    		raw_question['q1_feats'] = list(vecs1)

    		print(raw_question['q1_feats'])


    		b = [a[None,:] for a in list(raw_question['q1_feats'].values)]
    		q1_feats = np.concatenate(b, axis=0)
    		raw_question_vec = np.zeros([raw_question.shape[0],2,300])
    		raw_question_vec[:,0,:] = q1_feats[:]

    		pred = model.predict([raw_question_vec[:,0,:],raw_question_vec[:,0,:]])
    		print(pred)



    		# for i in raw_question_vec[,0,:]:
    		# 	print(np.shape(i))
    		# 	for j in raw_question_vec[,0,:]:
    		#  		pred = model.predict([i,j])
    		#  		print(pred)
	else:
		print("No raw data file is found")
else:
	print('No model is found')

