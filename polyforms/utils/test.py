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
    if thing == None:
        return False
    thing = str(thing)
    chars_are_digits = [(c in "0123456789") for c in thing]
    return (not (False in chars_are_digits)) and (len(thing) > 0)

#returns True if the given form_id represents an actual form in the database
def form_exists(form_id):
    if not is_valid_id(form_id):
        return False
    db, c = open_db()
    c.execute("SELECT form_id FROM forms WHERE form_id = %d;" % int(form_id))
    result = c.fetchone()
    close_db(db)
    return result != None

#Returns a list of errors in processing this form. If everything goes right, the error list is empty. DOES NOT store responses
#data should be an array of size equal to the number of questions in the form. Elements can be None or "". Choice questions must be inner lists.
def validate_form_submission(form_id, data):
    errors = []
    form = main.get_form_questions(form_id)
    responses = []
    index = 1
    if form["open"] == False:
        errors.append("This form is no longer accepting responses")
    for q in form["questions"]:
        if q["type"] == "section":
            continue
        if data[index] == None or len(data[index]) == 0:
            if (q["required"] == 1 or q["required"] == True):
                if q["type"] == "username":
                    errors.append("You must be logged in")
                else:
                    errors.append("You must answer, \"" + q["question"] + '"')
            index += 1
            responses.append(None)
            continue
        elif q["type"] == "int":
            try:
                responses.append(int(data[index]))
                if q["min"] != None and q["min"] != "" and responses[-1] < q["min"]:
                    errors.append("Your answer must be greater than or equal to %d for \"%s\"" % (q["min"], q["question"]))
                if q["max"] != None and q["max"] != "" and responses[-1] > q["max"]:
                    errors.append("Your answer must be less than or equal to %d for \"%s\"" % (q["max"], q["question"]))
            except:
                errors.append("You didn't enter an integer for, \"" + q["question"] + '"')
                responses.append(data[index])
        elif q["type"] == "number":
            try:
                responses.append(float(data[index]))
                if q["min"] != None and q["min"] != "" and responses[-1] < q["min"]:
                    errors.append("Your answer must be greater than or equal to %d for \"%s\"" % (q["min"], q["question"]))
                if q["max"] != None and q["max"] != "" and responses[-1] > q["max"]:
                    errors.append("Your answer must be less than or equal to %d for \"%s\"" % (q["max"], q["question"]))
            except:
                errors.append("You didn't enter a valid number for, \"" + q["question"] + '"')
                responses.append(data[index])
        elif q["type"] == "choice":
            responses.append(data[index])
            if q["min"] != None and len(responses[-1]) < q["min"]:
                errors.append("Select at least %d choices for \"%s\"" % (q["min"], q["question"]))
            if q["max"] != None and len(responses[-1]) > q["max"]:
                errors.append("Select no more than %d choices for \"%s\"" % (q["max"], q["question"]))
        elif q["type"] == "short" or q["type"] == "long":
            responses.append(data[index])
            try:
                if q["min"] != None and len(responses[-1]) < q["min"]:
                    errors.append("Your response must be at least %d characters long for \"%s\"" % (q["min"], q["question"]))
                if q["max"] != None and len(responses[-1]) > q["max"]:
                    errors.append("Your response must be no longer than %d characters for \"%s\"" % (q["max"], q["question"]))
            except:
                pass
        elif q["type"] == "username":
            responses.append(data[index])
        index += 1
    return errors

#returns true if this person can change form settings
def can_edit(user_id, form_id):
    if form_exists(form_id):
        db, c = open_db()
        owner = c.execute("SELECT owner_id FROM forms WHERE form_id = ? AND owner_id = ?;", (form_id, user_id)).fetchone()
        close_db(db)
        return owner != None
    else:
        return False

#returns true if this person can submit a response (if logged in)
def can_respond(user_id, form_id, login_required):
    db, c = open_db()
    result = c.execute("SELECT * FROM responses WHERE form_id = ? AND user_id = ?;", (form_id, user_id)).fetchone()
    close_db(db)
    return ((result == None or len(result) == 0) and login_required) or (login_required == False)


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

