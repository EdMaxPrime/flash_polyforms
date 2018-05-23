import sqlite3, os, base64, requests, json, hashlib
from flask import session

'''
db=sqlite3.connect("data/formData.db")
    c=db.cursor()

    db.commit()
    db.close()
'''

def createTables():
    db=sqlite3.connect("data/formData.db")
    c=db.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS forms (form_id INTEGER PRIMARY KEY, title TEXT, owner_id INTEGER, login_required INTEGER, public_results INTEGER, theme TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS responses (form_id INTEGER PRIMARY KEY, question_id INTEGER, user_id INTEGER, response_id INTEGER, response TEXT, timestamp TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS questions (question_id INTEGER PRIMARY KEY, type TEXT, form_id INTEGER, min INTEGER, max INTEGER);")
    c.execute("CREATE TABLE IF NOT EXISTS options (form_id INTEGER PRIMARY KEY, question_id INTEGER, option_index INTEGER, text_user_sees INTEGER, value TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS styles (form_id INTEGER PRIMARY KEY, row INTEGER, column INTEGER, property TEXT, value TEXT);")

    db.commit()
    db.close()

def addForm(formTitle, loginReq, publicReq, theme):
    db=sqlite3.connect("data/formData.db")
    c=db.cursor()

    #check if <forms> table exists
    c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='forms';")
    #bol holds if the table exists (0 = does not exist) and (1 = does exist)
    bol = c.fetchone()[0]
    #temp variable to hold # of users
    counter = 0
    if bol == 0:
        counter = 1
    if bol == 1:
        c.execute("SELECT COUNT(form_id) FROM forms;")
        counter = c.fetchone()
        counter = int(counter[0]) + 1
        #access cookie
        userID = session["user"]
        c.execute("INSERT INTO forms VALUES (?,?,?,?,?,?)", (counter,formTitle, userID, loginReq, publicReq, theme))
    db.commit()
    db.close()

def addResponse(question_id, response, timestamp):
    db=sqlite3.connect("data/formData.db")
    c=db.cursor()

    #check if <responses> table exists
    c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='responses';")
    #bol holds if the table exists (0 = does not exist) and (1 = does exist)
    bol = c.fetchone()[0]
    #temp variable to hold # of users
    counter = 0
    if bol == 0:
        counter = 1
    if bol == 1:
        c.execute("SELECT COUNT(response_id) FROM forms;")
        counter = c.fetchone()
        counter = int(counter[0]) + 1
        #access cookie
        userID = session["user"]
        formID = session["form_id"]
        c.execute("INSERT INTO responses VALUES (?,?,?,?,?,?)", (formID, question_id, userID, counter, response, timestamp))

    db.commit()
    db.close()

def addQuestions(question, type, min, max):
    db=sqlite3.connect("data/formData.db")
    c=db.cursor()

    #check if <questions> table exists
    c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='questions';")
    #bol holds if the table exists (0 = does not exist) and (1 = does exist)
    bol = c.fetchone()[0]
    #temp variable to hold # of users
    counter = 0
    if bol == 0:
        counter = 1
    if bol == 1:
        c.execute("SELECT COUNT(question_id) FROM questions;")
        counter = c.fetchone()
        counter = int(counter[0]) + 1
        #access cookie
        userID = session["user"]
        formID = session["form_id"]
        c.execute("INSERT INTO questions VALUES (?,?,?,?,?,?)", (counter, question, formID, type, min, max))
    db.commit()
    db.close()



def addOptions(questionID, text_user_sees, value):
    db=sqlite3.connect("data/formData.db")
    c=db.cursor()

    #check if <options> table exists
    c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='options';")
    #bol holds if the table exists (0 = does not exist) and (1 = does exist)
    bol = c.fetchone()[0]
    #temp variable to hold # of users
    counter = 0
    if bol == 0:
        counter = 1
    if bol == 1:
        c.execute("SELECT COUNT(option_index) FROM questions WHERE question_id = " + str(questionID) + ";")
        counter = c.fetchone()
        counter = int(counter[0]) + 1
        #access cookie
        userID = session["user"]
        formID = session["form_id"]
        c.execute("INSERT INTO options VALUES (?,?,?,?,?,?)", (formID, questionID, counter, text_user_sees, value))
    db.commit()
    db.close()

def addStyles(row, column, property, value):
    db=sqlite3.connect("data/formData.db")
    c=db.cursor()

    #check if <styles> table exists
    c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='styles';")
    #bol holds if the table exists (0 = does not exist) and (1 = does exist)
    bol = c.fetchone()[0]
    #temp variable to hold # of users
    if bol == 0:
        pass
    if bol == 1:
        formID = session["form_id"]
        c.execute("INSERT INTO options VALUES (?,?,?,?,?)", (formID, row, column, property, value))
    db.commit()
    db.close()

def getForm():
    pass

def getResponse

createTables()