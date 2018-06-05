import sqlite3   # enable control of an sqlite database
import hashlib   # allows for passwords and emails to be encrypted and decrypted
import db as main

#this will be the one we use when routes work
f = "data/database.db"

def open_db():
    db = sqlite3.connect(f) # open if f exists, otherwise create
    c = db.cursor()         # facilitate db ops
    return db, c

def close_db(db):
    db.commit()
    db.close()

def hashed(foo):
    return hashlib.md5(str(foo)).hexdigest()

#Given a tuple/list and a list of strings, will create a dictionary where the first key in the list corresponds to the first element in the tuple
def tuple_to_dictionary(tuuple, list_of_keys):
    d = {} #the dictionary
    index = 0 #the column index
    while index < len(tuuple):
        d[ list_of_keys[index] ] = tuuple[index]
        index += 1
    return d

#Returns true if the given thing is a nonnegative integer
def is_valid_id(thing):
    thing = str(thing)
    chars_are_digits = [(c in "0123456789") for c in thing]
    return not (False in chars_are_digits)

#Returns a form
def get_recent_forms(amount):
    db, c = open_db()
    c.execute("SELECT form_id FROM forms ORDER BY created DESC LIMIT %s;" % str(amount))
    list_of_ids = c.fetchall()
    close_db(db)
    return [get_form(x[0]) for x in list_of_ids]

#returns True if the given form_id represents an actual form in the database
def form_exists(form_id):
    if not is_valid_id(form_id):
        return False
    db, c = open_db()
    c.execute("SELECT form_id FROM forms WHERE form_id = %d;" % int(form_id))
    result = c.fetchone()
    close_db(db)
    return result != None

#Returns form info with more question data
def get_form(form_id):
    db, c = open_db()
    c.execute("SELECT form_id, title, owner_id, login_required, public_results, theme, created FROM forms WHERE form_id = ?;", (str(form_id),))
    result = c.fetchone()
    print form_id
    form = tuple_to_dictionary(result, ["id", "title", "owner", "login_required", "public_results", "theme", "created"])
    form["questions"] = []
    questions = c.execute("SELECT question_id, question, type, required, min, max FROM questions WHERE form_id = ?;", (form_id,)).fetchall()
    for q in questions:
        form["questions"].append(tuple_to_dictionary(q, ["index", "question", "type", "required", "min", "max"]))
    close_db(db)
    return form

