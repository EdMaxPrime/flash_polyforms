import sqlite3   # enable control of an sqlite database
import hashlib   # allows for passwords and emails to be encrypted and decrypted
import db as main

#this will be the one we use when routes work
def open_db():
    db = sqlite3.connect(main.path_to_db) # open if f exists, otherwise create
    c = db.cursor()                       # facilitate db ops
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
    questions = c.execute("SELECT question_id, question, type, required, min, max FROM questions WHERE form_id = ? ORDER BY question_id ASC;", (form_id,)).fetchall()
    for q in questions:
        #convert the query result into a dictionary
        questionAsDict = tuple_to_dictionary(q, ["index", "question", "type", "required", "min", "max"])
        #If this question lists options, then add them as a list under the key "choices"
        if questionAsDict["type"] == "choice":
            c.execute("SELECT text_user_sees, value FROM options WHERE form_id = ? AND question_id = ? ORDER BY option_index ASC;", (form_id, questionAsDict["index"]))
            result = c.fetchall()
            questionAsDict["choices"] = [tuple_to_dictionary(choice, ["text", "value"]) for choice in result]
        #add this to the list of questions
        form["questions"].append(questionAsDict)
    close_db(db)
    return form

#Add a question, return its id
def add_question(form_id, question, _type, required=False, _min=None, _max=None):
    db, c = open_db()
    question_id = c.execute("SELECT max(question_id) FROM questions WHERE form_id = ?;", (form_id,)).fetchone()
    question_id = (question_id[0] + 1) if question_id[0] != None else 1
    c.execute("INSERT INTO questions VALUES (?,?,?,?,?,?,?);", (question_id, question, _type, form_id, required, _min, _max))
    close_db(db)
    return question_id


#Add a response to a question, returns its id
def add_response(form_id, question_id, response, new_row=False):
    db, c = open_db()
    response_id = c.execute("SELECT max(response_id) FROM responses WHERE form_id = ?;", (form_id,)).fetchone()[0] or 0
    if new_row:
        response_id += 1
    c.execute("INSERT INTO responses (form_id, question_id, response_id, response, timestamp) VALUES (?,?,?,?, datetime('now'));", (form_id, question_id, response_id, response))
    close_db(db)
    return response_id

#This will clear the database, keeps tables
def reset():
    db, c = open_db()
    c.execute("DELETE FROM forms;")
    c.execute("DELETE FROM responses;")
    c.execute("DELETE FROM questions;")
    c.execute("DELETE FROM options;")
    c.execute("DELETE FROM accounts;")
    c.execute("DELETE FROM styles;")
    close_db(db)

