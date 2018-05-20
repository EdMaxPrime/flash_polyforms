import sqlite3   # enable control of an sqlite database
import hashlib   # allows for passwords and emails to be encrypted and decrypted

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
    for user in c.execute(command):
        id+=1
    close_db(db)
    return id

def hashed(foo):
    return hashlib.md5(str(foo)).hexdigest()
    
def add_form():
    db, c = open_db()
    
    close_db(db)

def add_response():
    db, c = open_db()
    
    close_db(db)
    
def add_question():
    db, c = open_db()
    
    close_db(db)

def add_account():
    db, c = open_db()
    
    close_db(db)
    
def add_style():
    db, c = open_db()
    
    close_db(db)

def create_tables():
    db, c = open_db()
    c.execute("CREATE TABLE forms(form_id INTEGER PRIMARY KEY, title TEXT, owner_id INTEGER, login_required INTEGER, public_results INTEGER, theme TEXT)")
    c.execute("CREATE TABLE responses(form_id integer PRIMARY KEY, question_id INTEGER, user_id INTEGER, response_id INTEGER, response BLOB, timestamp TEXT)")
    c.execute("CREATE TABLE questions(question_id PRIMARY KEY, question integer, type TEXT, form_id INTEGER, min INTEGER, max INTEGER)")
    c.execute("CREATE TABLE options(form_id PRIMARY KEY, question_id INTEGER, option_index INTEGER, text_user_sees TEXT, value TEXT)")
    c.execute("CREATE TABLE accounts(user_id INTEGER PRIMARY KEY, username integer TEXT, password TEXT)")
    c.execute("CREATE TABLE styles(form_id INTEGER, row INTEGER, column INTEGER, property TEXT, value TEXT)")
    close_db(db)
    
create_tables()