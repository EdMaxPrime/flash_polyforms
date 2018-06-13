import sqlite3   # enable control of an sqlite database
import hashlib   # allows for passwords and emails to be encrypted and decrypted
import db as main
from flask import session

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
    return (not (False in chars_are_digits)) and (len(thing) > 0)

#Returns a list of forms with responses in the given amount. These are the most recently created ones
def get_recent_forms(amount):
    db, c = open_db()
    c.execute("SELECT form_id FROM forms WHERE open = 1 ORDER BY created DESC LIMIT %s;" % str(amount))
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

#Returns form info with more question data. Top level keys are: id, title, owner, login_required, public_results, theme, created, open
#The questions array has items with these keys: index, question, type, required, min, max
#Choices in the choices key of a question have these keys: text and value
def get_form(form_id):
    db, c = open_db()
    c.execute("SELECT form_id, title, owner_id, login_required, public_results, theme, created, open, message FROM forms WHERE form_id = ?;", (str(form_id),))
    result = c.fetchone()
    form = tuple_to_dictionary(result, ["id", "title", "owner", "login_required", "public_results", "theme", "created", "open", "message"])
    form["login_required"] = (form["login_required"] == 1)
    form["public_results"] = (form["public_results"] == 1)
    form["open"] = (form["open"] == 1)
    c.execute("SELECT max(response_id) FROM responses WHERE form_id = " + str(form_id) + ";")
    tempCounter = c.fetchone()[0]
    if tempCounter == None:
        tempCounter = 0
    form["data"] = tempCounter

    try:
        form["owner"] = c.execute("SELECT username FROM accounts WHERE user_id=?;", (form["owner"],)).fetchone()[0]
    except:
        form["owner"] = ""
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

#Returns the number of answerable questions in the form
def number_of_questions(form_id):
    questions = get_form(form_id)["questions"]
    if len(questions) == 0:
        return 0
    else:
        return reduce(lambda num, q: (num+1 if q["type"] != "section" else num), questions, 0)

#Returns a list of forms that are owned by the given user
def get_forms_by(user_id):
    db, c = open_db()
    result = c.execute("SELECT form_id FROM forms WHERE owner_id=?;", (user_id,)).fetchall()
    close_db(db)
    list_of_forms = [get_form(r[0]) for r in result]
    return list_of_forms

#Add a question, return its id
def add_question(form_id, question, _type, required=False, _min=None, _max=None):
    db, c = open_db()
    question_id = c.execute("SELECT max(question_id) FROM questions WHERE form_id = ?;", (form_id,)).fetchone()
    question_id = (question_id[0] + 1) if question_id[0] != None else 1
    if _type == "section": #these <h1> tags dont count as questions, they just need to be in the right order
        question_id -= 1
    c.execute("INSERT INTO questions VALUES (?,?,?,?,?,?,?);", (question_id, question, _type, form_id, required, _min, _max))
    close_db(db)
    return question_id


#Add a response to a question, returns its id
def add_response(form_id, question_id, response, new_row=False):
    db, c = open_db()
    response_id = c.execute("SELECT max(response_id) FROM responses WHERE form_id = ?;", (form_id,)).fetchone()[0] or 0
    if new_row:
        response_id += 1
    if isinstance(response, list):
        response = ",".join(response)
    try:
        c.execute("INSERT INTO responses (user_id, form_id, question_id, response_id, response, timestamp) VALUES (?,?,?,?,?, datetime('now'));", (session["user_id"],form_id, question_id, response_id, response))
    except KeyError:
        c.execute("INSERT INTO responses (user_id, form_id, question_id, response_id, response, timestamp) VALUES (?,?,?,?,?, datetime('now'));", (None,form_id, question_id, response_id, response))
    close_db(db)
    return response_id

#Returns a list of errors in processing this form. If everything goes right, the error list is empty. DOES NOT store responses
#data should be an array of size equal to the number of questions in the form. Elements can be None or "". Choice questions must be inner lists.
def validate_form_submission(form_id, data):
    errors = []
    form = get_form(form_id)
    responses = []
    index = 1
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
        owner = c.execute("SELECT owner_id FROM forms WHERE form_id = " + str(form_id) + " AND owner_id = " + str(user_id) + ";").fetchone()
        close_db(db)
        return owner != None
    else:
        return False

#Change form settings
def toggle_form(form_id, what):
    db, c = open_db()
    c.execute("UPDATE forms SET %s = 1 - %s WHERE form_id = %s" % (what, what, str(form_id)))
    value = c.execute("SELECT %s FROM forms WHERE form_id = %s;" % (what, str(form_id))).fetchone()
    close_db(db)
    return (value[0] == 1) if value != None else False

#change theme
def set_theme(form_id, theme):
    db, c = open_db()
    c.execute("UPDATE forms SET theme = " + "'" + theme + "' WHERE form_id = " + form_id + ";")
    close_db(db)
    return theme


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

