import sqlite3   # enable control of an sqlite database
import hashlib   # allows for passwords and emails to be encrypted and decrypted
from flask import session   # interact with cookie

f = "database.db"

def open_db():
    db = sqlite3.connect(f) # open if f exists, otherwise create
    c = db.cursor()         # facilitate db ops
    return db, c

def close_db(db):
    db.commit()
    db.close()

# helper function for incrementing id numbers
# returns next id number to be used
def increment_id(table):
    db, c = open_db()
    command = "SELECT * FROM %s" % (table)
    id = 0
    for entry in c.execute(command):
        id+=1
    close_db(db)
    return id

def hashed(foo):
    return hashlib.md5(str(foo)).hexdigest()
    
def add_form(formTitle, loginReq, publicReq, theme):
    db=sqlite3.connect("data/database.db")
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

def add_response(question_id, response, timestamp):
    db=sqlite3.connect("data/database.db")
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
    
def add_question(question, type, required, min, max):
    db=sqlite3.connect("data/database.db")
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
        c.execute("INSERT INTO questions VALUES (?,?,?,?,?,?)", (counter, question, formID, type, required, min, max))
    db.commit()
    db.close()

def add_option(questionID, text_user_sees, value):
    db=sqlite3.connect("data/database.db")
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
    
def add_style(row, column, property, value):
    db=sqlite3.connect("data/database.db")
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

# add security questions later
# sqlite automatically increments all integer primary keys (user_id)
def add_account(username, password):
    db, c = open_db()
    c.execute("INSERT INTO accounts (username, password) VALUES ('%s', '%s')" % (username, hashed(password)))
    close_db(db)

def create_tables():
    db, c = open_db()
    c.execute("CREATE TABLE forms(form_id INTEGER PRIMARY KEY, title TEXT, owner_id INTEGER, login_required INTEGER, public_results INTEGER, theme TEXT);")
    c.execute("CREATE TABLE responses(form_id INTEGER PRIMARY KEY, question_id INTEGER, user_id INTEGER, response_id INTEGER, response BLOB, timestamp TEXT);")
    c.execute("CREATE TABLE questions(question_id INTEGER PRIMARY KEY, question integer, type TEXT, form_id INTEGER, required INTEGER, min INTEGER, max INTEGER);")
    c.execute("CREATE TABLE options(form_id INTEGER PRIMARY KEY, question_id INTEGER, option_index INTEGER, text_user_sees TEXT, value TEXT);")
    c.execute("CREATE TABLE accounts(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT);")
    c.execute("CREATE TABLE styles(form_id INTEGER, row INTEGER, column INTEGER, property TEXT, value TEXT);")
    close_db(db)
    
create_tables()