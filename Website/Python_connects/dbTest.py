# !/usr/bin/python
import MySQLdb
import questionProcessing as qp

def computeScoredQuestions(questions):
    scoredQuestions = {}
    tfidfQuestions = {}
    tfidfQ = qp.TFIDF(questions)
    for q in questions:
        if scoredQuestions.has_key(q):
            scoredQuestions[q] += 1
        else:
            scoredQuestions[q] = 1
            tfidfQuestions[q] = tfidfQ[questions.index(q)]
    # print("h:{}".format(scoredQuestions))
    deletes = True
    while deletes:
        deletes = False
        for q1 in scoredQuestions:
            for q2 in scoredQuestions:
                if q1 != q2:
                    # print(q1)
                    # print(q2)
                    # isSame = qp.classify(q1, q2)
                    isSame = qp.cosSim(tfidfQuestions[q1], tfidfQuestions[q2])
                    # print(isSame)
                    if isSame:
                        # deletedQs.append(q2)
                        scoredQuestions[q2] += scoredQuestions[q1]
                        print(scoredQuestions[q2])
                        scoredQuestions[q1] += scoredQuestions[q2]
                        del scoredQuestions[q1]
                        deletes = True
                if deletes:
                    break
            if deletes:
                break

        # for d in deletedQs:
            # del scoredQuestions[d]

    # print(scoredQuestions)

    return scoredQuestions

db = MySQLdb.connect(host="tyr.czavorwfa0ij.eu-west-2.rds.amazonaws.com",    # your host, usually localhost
                     user="admin",         # your username
                     passwd="Edin40214986",  # your password
                     db="messages")        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# Use all the SQL you like
cur.execute("SELECT text_message FROM texts")

# print all the first cell of all the rows
allRecentQuestions = []
for row in cur.fetchall():
    # print "{}".format(row[0])
    allRecentQuestions.append(row[0])

db.close()
print(allRecentQuestions)
db = MySQLdb.connect(host="tyr.czavorwfa0ij.eu-west-2.rds.amazonaws.com",    # your host, usually localhost
                     user="admin",         # your username
                     passwd="Edin40214986",  # your password
                     db="messages")        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

scoredQuestions = computeScoredQuestions(allRecentQuestions)
print(scoredQuestions)
for k in scoredQuestions:
    print type(scoredQuestions[k])
    sql = ("""INSERT INTO sorted_texts(text_message, score) VALUES (%s,%s)""")
    args = (k,scoredQuestions[k])
    print sql
    cur.execute(sql,args)
#cur.execute("INSERT INTO sorted_texts(text_message, score) VALUES ('Test 123', 23)")
    db.commit()
# NOW WE HAVE THE QUESTIONS SCORED, WE WANT TO PUSH THEM TO THE DATABASE
#for k in scoredQuestions:
