import sqlite3   # enable control of an sqlite database
import hashlib   # allows for passwords and emails to be encrypted and decrypted
from flask import session   # interact with cookie

#this will be the one we use when routes work
#f = "data/database.db"

#temp
f = "data/database.db"

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
    
def add_form(user_id, formTitle, loginReq, publicReq, theme):
    db=sqlite3.connect("../data/database.db")
    c=db.cursor()
    c.execute("INSERT INTO forms (title, owner_id, login_required, public_results, theme, created) VALUES (?,?,?,?,?, datetime('now'))", (formTitle, user_id, loginReq, publicReq, theme))
    db.commit()
    db.close()

def add_response(userID, formID, question_id, response, timestamp):
    db=sqlite3.connect("../data/database.db")
    c=db.cursor()
    c.execute("INSERT INTO responses (form_id, question_id, user_id, response, timestamp) VALUES (?,?,?,?,?)", (formID, question_id, userID, response, timestamp))
    db.commit()
    db.close()
    
def add_question(formID, question, type, required, min, max):
    db=sqlite3.connect("../data/database.db")
    c=db.cursor()
    #access cookie
    #print formID
    c.execute("INSERT INTO questions (question, form_id, type, required, min, max) VALUES (?,?,?,?,?,?)", (question, formID, type, required, min, max))
    db.commit()
    db.close()

def add_option(formID, questionID, text_user_sees, value):
    db=sqlite3.connect("../data/database.db")
    c=db.cursor()
    c.execute("INSERT INTO options (form_id, question_id, text_user_sees, value) VALUES (?,?,?,?)", (formID, questionID, text_user_sees, value))
    db.commit()
    db.close()
    
def add_style(formID, row, column, property, value):
    db=sqlite3.connect("../data/database.db")
    c=db.cursor()
    c.execute("INSERT INTO styles (form_id, row, column, property, value) VALUES (?,?,?,?,?)", (formID, row, column, property, value))
    db.commit()
    db.close()

# add security questions later
# sqlite automatically increments all integer primary keys (user_id)
def add_account(username, password):
    db, c = open_db()
    c.execute("INSERT INTO accounts (username, password) VALUES ('%s', '%s')" % (username, hashed(password)))
    close_db(db)

#Returns true if this username+password pair matches, false if it does not
def validate_login(username, password):
    db, c = open_db()
    #print  "SELECT username FROM accounts WHERE username" + " = '" + str(username) + "' AND password = '" + str(hashed(password)) + "';"
    c.execute("SELECT username FROM accounts WHERE username" + " = '" + str(username) + "' AND password = '" + str(hashed(password)) + "';")
    results = c.fetchone()
    close_db(db)
    if results == None:
        return False
    else:
        return len(results) > 0

def checkExist(table, colName, query):
    db, c = open_db()
    #print "SELECT " + str(colName) + " FROM " + table + " WHERE " + colName + "=" + query +";"
    c.execute("SELECT " + str(colName) + " FROM " + str(table) + " WHERE " + str(colName) + " = '" + str(query) +"';")
    results = c.fetchone()
    close_db(db)
    if results == None:
        return False
    else:
        return len(results) > 0

#Returns true if this username is already taken, false otherwise
def user_exists(username):
    db, c = open_db()
    c.execute("SELECT username FROM accounts WHERE username = '%s';" % (username,)) #comma needed for this
    whos_there = c.fetchone()
    close_db(db)
    return len(whos_there) > 0

"""#Given a form's ID number, returns a dictionary representing this form
{
  title: "My Form",
  owner: "XD",
  id: "100",
  created: "2018-05-26 12:00:00",
  headers: ["Name?", "Age?", <question>],
  types: ["short", "number", <short|long|number|choice>],
  data: [
    ["gir", 40, <answer to a question>],
    ["zim", 12]
  ]
}"""
def get_form_responses(form_id):
    return {}

def create_tables():
    db, c = open_db()
    c.execute("CREATE TABLE IF NOT EXISTS forms(form_id INTEGER PRIMARY KEY, title TEXT, owner_id INTEGER, login_required INTEGER, public_results INTEGER, theme TEXT, created TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS responses(form_id INTEGER, question_id INTEGER, user_id INTEGER, response_id INTEGER PRIMARY KEY, response BLOB, timestamp TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS questions(question_id INTEGER PRIMARY KEY, question integer, type TEXT, form_id INTEGER, required INTEGER, min INTEGER, max INTEGER);")
    c.execute("CREATE TABLE IF NOT EXISTS options(form_id INTEGER, question_id INTEGER, option_index INTEGER PRIMARY KEY, text_user_sees TEXT, value TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS accounts(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS styles(form_id INTEGER, row INTEGER, column INTEGER, property TEXT, value TEXT);")
    close_db(db)
    
