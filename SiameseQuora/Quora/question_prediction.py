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
nlp = spacy.load('en')
if os.path.exists('final_tf_idf_vec.h5'):
	model = load_model('final_tf_idf_vec.h5',custom_objects={'contrastive_loss': contrastive_loss})
	if os.path.exists("raw_question.tsv"):
		raw_question = pd.read_csv("raw_question.tsv",delimiter = '\t')

		if os.path.exists('current_question.tsv'):
			current_question = pd.read_csv("current_question.tsv",delimiter = ',')

			combine_question = pd.concat([current_question,raw_question])

			print(raw_question)
			print(current_question)

			print(combine_question)

			combine_question['question'] = combine_question['question'].apply(lambda x: unicode(str(x),"utf-8"))

			questions = list(current_question['question']) + list(raw_question['question'])

			tfidf = TfidfVectorizer(lowercase=False,)
			tfidf.fit_transform(questions)

			word2tfidf = dict(zip(tfidf.get_feature_names(),tfidf.idf_))


			vecs3 = []
			for qu in tqdm(list(combine_question['question'])):
				doc = nlp(qu)
				mean_vec = np.zeros([len(doc),300])
				for word in doc:
					vec = word.vector
					try:
						idf = word2tfidf[str(word)]
					except:
						idf = 0
					mean_vec += vec * idf
				mean_vec = mean_vec.mean(axis=0)
				vecs3.append(mean_vec)
			combine_question['q1_feats'] = list(vecs3)

			b = [a[None,:] for a in list(combine_question['q1_feats'].values)]
			q3_feats = np.concatenate(b, axis=0)
			combine_question_vec = np.zeros([combine_question.shape[0],2,300])
			combine_question_vec[:,0,:] = q3_feats


			question_route = []
			question_list = []
			score_list = []
			index_i = 0
			index_j = 0
			score = 0
			for i in combine_question_vec[:,0,:]:
				i = np.reshape(i,(1,300))
				route_list = []
				for j in combine_question_vec[:,0,:]:
					j = np.reshape(j,(1,300))
					pred = model.predict([i,j])
					if pred >= 0.5:
						route_list.append(index_j)
					else:
						route_list.append(index_i)
					index_j +=1
				question_route.append(route_list)
				index_i +=1
			for i in question_route:
				n = question_route.index(i)
				for j in i:
					if j != n:
						question_route[j] = []
						score +=1
					else:
						continue
				if not i :
					continue
				else:
					score_list.append(score)
					question_list.append(combine_question['question'].values[n])
				score = 0
			df = pd.DataFrame({'question':question_list,'score':score_list})
			df.to_csv('current_question.tsv')
			sys.exit(0)


		else:
			raw_question['question'] = raw_question['question'].apply(lambda x: unicode(str(x),"utf-8"))


			# merge texts
			questions = list(raw_question['question'])

			tfidf = TfidfVectorizer(lowercase=False, )
			tfidf.fit_transform(questions)

			# dict key:word and value:tf-idf score
			word2tfidf = dict(zip(tfidf.get_feature_names(), tfidf.idf_))
			del questions


    
    		vecs1 = []
    		for qu in tqdm(list(raw_question['question'])):
    			doc = nlp(qu) 
    			mean_vec = np.zeros([len(doc), 300])
    			for word in doc:
    				# word2vec
    				vec = word.vector
    				# fetch df score
    				try:
    					idf = word2tfidf[str(word)]
    				except:
    					idf = 0
    				# compute final vec
    				mean_vec += vec * idf
        		mean_vec = mean_vec.mean(axis=0)
        		vecs1.append(mean_vec)
    		raw_question['q1_feats'] = list(vecs1)

    

    		b = [a[None,:] for a in list(raw_question['q1_feats'].values)]
    		q1_feats = np.concatenate(b, axis=0)
    		raw_question_vec = np.zeros([raw_question.shape[0],2,300])
    		raw_question_vec[:,0,:] = q1_feats


    		question_route = [] 
    		question_list = []
    		score_list = []
    		index_i = 0
    		index_j = 0
    		score = 0
    		for i in raw_question_vec[:,0,:]:
    		 	i = np.reshape(i,(1,300))
    		 	route_list = []
    		 	for j in raw_question_vec[:,0,:]:
    		 		j = np.reshape(j,(1,300))
    		 		pred = model.predict([i,j])
    		 		print(pred)
    		 		if pred >= 0.5:
    		 			route_list.append(index_j)
    		 		else:
    		 			route_list.append(index_i)
    		 		index_j +=1
    		 	question_route.append(route_list)
    		 	index_i +=1
    		for i in question_route:
    			n = question_route.index(i)
    			for j in i:
    				if j != n:
    					question_route[j] = []
    					score +=1
    				else:
    					continue
    			if not i:
    				continue
    			else:
    				score_list.append(score)
    				question_list.append(raw_question['question'][n])
    			score = 0
    		df = pd.DataFrame({'question':question_list,'score':score_list})
    		df.to_csv('current_question.tsv')
    		sys.exit(0)

	else:
		print("No raw data file is found")
else:
	print('No model is found')

