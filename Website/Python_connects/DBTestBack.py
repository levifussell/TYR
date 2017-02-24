#!/usr/bin/python
import MySQLdb

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
for row in cur.fetchall():
    print "{}".format(row[0])


db.close()
