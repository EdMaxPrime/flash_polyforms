import sqlite3   # enable control of an sqlite database
import hashlib   # allows for passwords and emails to be encrypted and decrypted
import os

#this will be the one we use when routes work
#f = "data/database.db"

#temp
local_db_location =  os.path.abspath(os.path.dirname(__file__))
global db_file
db_file = local_db_location + "/../data/database.db"
path_to_db = db_file

def use_database(path):
    if len(path) > 0 and path[-1] != "/":
        path += "/"
    path_to_db = path + local_db_location

def open_db():
    db = sqlite3.connect(path_to_db) # open if f exists, otherwise create
    c = db.cursor()                  # facilitate db ops
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

#Given a tuple/list and a list of strings, will create a dictionary where the first key in the list corresponds to the first element in the tuple
def tuple_to_dictionary(tuuple, list_of_keys):
    d = {} #the dictionary
    index = 0 #the column index
    while index < len(tuuple):
        d[ list_of_keys[index] ] = tuuple[index]
        index += 1
    return d
    
def add_form(user_id, formTitle, loginReq, publicReq, theme, open, message):
    db, c = open_db()
    c.execute("INSERT INTO forms (title, owner_id, login_required, public_results, theme, created, open, message) VALUES (?,?,?,?,?, datetime('now'), ?, ?)", (formTitle, user_id, loginReq, publicReq, theme, open, message))
    form_id = c.execute("SELECT max(form_id) FROM forms;").fetchone()
    close_db(db)
    return form_id[0]

#Add a response to a question, returns its id
def add_response(form_id, user_id, question_id, response, response_id=None):
    db, c = open_db()
    if response_id == None:
        response_id = c.execute("SELECT max(response_id) FROM responses WHERE form_id = ? AND response_id >= 0;", (form_id,)).fetchone()[0] or 0
        response_id += 1
    if isinstance(response, list):
        response = "\n".join(response)
    c.execute("INSERT INTO responses (user_id, form_id, question_id, response_id, response, timestamp) VALUES (?,?,?,?,?, datetime('now'));", (user_id,form_id, question_id, response_id, response))
    close_db(db)
    return response_id

#Add a response to a question, but give it a negative id going backwards, returns its id
def add_response_negative(form_id, user_id, question_id, response, response_id=None):
    db, c = open_db()
    if response_id == None:
        response_id = c.execute("SELECT min(response_id) FROM responses WHERE form_id = ? AND response_id < 0;", (form_id,)).fetchone()[0] or 0
        response_id -= 1
    if isinstance(response, list):
        response = "\n".join(response)
    c.execute("INSERT INTO responses (user_id, form_id, question_id, response_id, response, timestamp) VALUES (?,?,?,?,?, datetime('now'));", (user_id,form_id, question_id, response_id, response))
    close_db(db)
    return response_id
    
def add_question(formID, question, type, required, min, max):
    db, c = open_db()
    question_id = c.execute("SELECT max(question_id) FROM questions WHERE form_id = ?;", (formID,)).fetchone()
    question_id = (question_id[0] + 1) if question_id[0] != None else 1
    c.execute("INSERT INTO questions (question, question_id, form_id, type, required, min, max) VALUES (?,?,?,?,?,?,?);", (question, int(question_id),int(formID), type, required, min, max))
    close_db(db)
    return question_id

def add_option(formID, questionID, text_user_sees, value):
    db, c = open_db()
    c.execute("INSERT INTO options (form_id, question_id, text_user_sees, value) VALUES (?,?,?,?)", (formID, questionID, text_user_sees, value))
    close_db(db)
    
def add_style(formID, row, column, property, value):
    db, c = open_db()
    c.execute("INSERT INTO styles (form_id, row, column, property, value) VALUES (?,?,?,?,?)", (formID, row, column, property, value))
    db.commit()
    db.close()

# add security questions later
# sqlite automatically increments all integer primary keys (user_id)
def add_account(username, password, security_question, security_question_answer):
    db, c = open_db()
    c.execute("INSERT INTO accounts (username, password, security_question, security_question_answer) VALUES ('%s', '%s', '%s', '%s')" % (username, hashed(password), str(security_question), hashed(str(username) + str(security_question_answer))))
    close_db(db)

#Returns true if this username+password pair matches, false if it does not
def validate_login(username, password):
    db, c = open_db()
    c.execute("SELECT username FROM accounts WHERE username" + " = '" + str(username) + "' AND password = '" + str(hashed(password)) + "';")
    results = c.fetchone()
    close_db(db)
    if results == None:
        return False
    else:
        return len(results) > 0

#Returns true if this username+password pair matches, false if it does not
def validate_resetPassword(username, security_question, security_question_answer):
    db, c = open_db()
    c.execute("SELECT username FROM accounts WHERE username" + " = '" + str(username) + "' AND security_question = '" + str(security_question) +"' AND security_question_answer = '" + str(hashed(str(username) + str(security_question_answer))) + "';")
    results = c.fetchone()
    close_db(db)
    if results == None:
        return False
    else:
        return len(results) > 0

#Checks if something exists in a specific Column within a table. Returns true if it is found
def checkExist(table, colName, query):
    db, c = open_db()
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
    results = c.fetchone()
    close_db(db)
    if results == None:
        return False
    else:
        return len(results) > 0

#returns the ID # for a specific form / question / user based off 1 thing you know about a column in the Table + the colName of the ID
def getID(tableName, idCol, queryCol, query):
    db, c = open_db()
    c.execute("SELECT " + str(idCol) + " FROM " + str(tableName) + " WHERE " + str(queryCol) + " = '%s';" % (query,)) #comma needed for this
    ID = c.fetchone()
    close_db(db)
    return ID[0]

#Useful for retrieving sqlite query results
def defaultVal(v, d):
    return d if (v == None or v[0] == None) else v[0]

def get_form_meta(form_id):
    db, c = open_db()
    c.execute("SELECT form_id, title, owner_id, login_required, public_results, theme, created, open, message FROM forms WHERE form_id = ?;", (str(form_id),))
    result = c.fetchone()
    form = tuple_to_dictionary(result, ["id", "title", "owner", "login_required", "public_results", "theme", "created", "open", "message"])
    form["login_required"] = (form["login_required"] == 1)
    form["public_results"] = (form["public_results"] == 1)
    form["open"] = (form["open"] == 1)
    form["num_responses"] = defaultVal(c.execute("SELECT max(response_id) FROM responses WHERE form_id = " + str(form_id) + ";").fetchone(), 0)
    form["owner_id"] = form["owner"]
    form["owner"] = defaultVal(c.execute("SELECT username FROM accounts WHERE user_id=?;", (form["owner"],)).fetchone(), "")
    close_db(db)
    return form

#Returns form info with more question data. Top level keys are: id, title, owner, login_required, public_results, theme, created, open
#The questions array has items with these keys: index, question, type, required, min, max
#Choices in the choices key of a question have these keys: text and value
def get_form_questions(form_id):
    form = get_form_meta(form_id) #get basic info into the dictionary
    db, c = open_db()
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

#form_id, question_id, user_id, response_id, response, timestamp
def get_form_responses(form_id):
    form = get_form_meta(form_id)
    db, c = open_db()
    questions = c.execute("SELECT question, type FROM questions WHERE form_id = ? ORDER BY question_id;", (form_id,)).fetchall()
    form["headers"] = ["Response Index", "When"] + [query[0] for query in questions]
    form["types"] = ["int", "short"] + [query[1] for query in questions]
    responseArray = c.execute("SELECT * FROM responses WHERE form_id = ? AND response_id >= 0 ORDER BY response_id, question_id;", (form_id,)).fetchall()    
    form["data"] = []
    response_id = 1
    tempArray = [None for i in range(0, len(form["headers"]))]
    for r in responseArray:
        #when the response index goes up, put the previous row in the 2d data array and then fill the tempArray with None values to signify a new row
        if r[3] > response_id:
            form["data"].append(tempArray)
            tempArray = [None for i in range(0, len(form["headers"]))]
            response_id += 1
        #make sure response index and timestamp are recorded
        if tempArray[0] == None:
            tempArray[0] = response_id  #response index/id
            tempArray[1] = r[5]         #timestamp
        #now put the actual answer for this question into its right spot, accounting for the extra response index and timestamp columns
        tempArray[ r[1] + 1 ] = r[4]
        #if its a choice question, turn the answer into a list
        if form["types"][ r[1] + 1 ] == "choice":
            tempArray[ r[1] + 1 ] = tempArray[ r[1] + 1 ].splitlines()
    #put the last row in
    if len(form["data"]) < len(responseArray):
        form["data"].append(tempArray)
    close_db(db)
    return form

#Returns a list of forms that are owned by the given user
def get_forms_by(user_id):
    db, c = open_db()
    result = c.execute("SELECT form_id FROM forms WHERE owner_id=?;", (user_id,)).fetchall()
    close_db(db)
    list_of_forms = [get_form_questions(r[0]) for r in result]
    return list_of_forms

#Returns the same structure as get_form_questions, but it also includes one answer to all the questions with the provided response_id
def get_form_questions_1response(form_id, response_id):
    form = get_form_questions(form_id)
    db, c = open_db()
    c.execute("SELECT response, question_id FROM responses WHERE form_id = ? AND response_id = ? ORDER BY question_id;", (form_id, response_id))
    responses = c.fetchall()
    i = 0
    while i < len(form["questions"]) and i < len(responses):
        if form["questions"][i]["type"] == "choice":
            selected_choices = responses[i][0].splitlines()
            for c in form["questions"][i]["choices"]:
                c["selected"] = c["value"] in selected_choices
        else:
            form["questions"][i]["value"] = responses[i][0]
        i += 1
    close_db(db)
    return form

# This returns a dictionary that represents a form.
# Keys are title, id, created, headers, types, data.
# Header is an array of questions.
# Types is an array of what types of question each question is
# Data is a 2d Array that holds the arrays of responses per question
def getFormData(formID):
    #=================
    # "Global" Holder variables
    formData = {}
    headerArray = []
    typeArray = []
    dataArray = []
    #==================
    # Top parts of Dictionary
    db, c = open_db()
    c.execute("SELECT * FROM forms WHERE form_id = " + str(formID))
    tempResult = c.fetchone()
    #Basic form stuff
    formData["title"] = str(tempResult[1])
    formData["id"] = str(tempResult[0])
    formData["created"] = str(tempResult[6])
    formData["login_required"] = str(tempResult[3])
    formData["public_results"] = str(tempResult[4])
    formData["open"] = tempResult[7]
    #Add creator ID
    ownerID = tempResult[2]
    c.execute("SELECT username FROM accounts where user_id = " + str(ownerID) + ";")
    tempResult = c.fetchone()
    formData["owner"] = (str(tempResult[0]))
    #========================
    # headers + types
    c.execute("SELECT * FROM questions WHERE form_id = " + str(formID) + " AND type != 'section';")
    tempResult = c.fetchall()
    if tempResult is not None:
        for each in tempResult:
            #question_id_array.append(each[0])
            headerArray.append(str(each[1]))
            typeArray.append(str(each[2]))
        formData["headers"] = headerArray
        formData["types"] = typeArray
    if tempResult == None:
        question_id_array = None
        formData["headers"] = None
        formData["types"] = None
    #========================
    # DATA 
    responseArray = c.execute("SELECT * FROM responses WHERE form_id = ? ORDER BY response_id, question_id;", (formID,)).fetchall()    
    if len(responseArray) > 0:
        currentResponseID = responseArray[0][3]
        tempArray = []
        dataArray.append([])
        for each in responseArray:
            if each[3] == currentResponseID:
                dataArray[-1].append(each[4])
            else:
                dataArray.append([])
                currentResponseID = each[3]
                dataArray[-1].append(each[4])
        formData["data"] = dataArray
    else:
        formData["data"] = []
    close_db(db)
    return formData

#This returns a dictionary with the same syntax of returnFormDataNoResponse(formID) but with responses

def getFormDataWithResponse(formID):
    #=================
    # "Global" Holder variables
    formData = {}
    questionArray = []
    #==================
    # Top parts of Dictionary
    db, c = open_db()
    c.execute("SELECT * FROM forms WHERE form_id = " + str(formID))
    tempResult = c.fetchone()
    #Basic form stuff
    formData["title"] = str(tempResult[1])
    formData["id"] = str(tempResult[0])
    formData["theme"] = str(tempResult[5])
    formData["open"] = tempResult[7]
    #Add creator ID
    ownerID = tempResult[2]
    c.execute("SELECT username FROM accounts where user_id = " + str(ownerID) + ";")
    tempResult = c.fetchone()
    formData["owner"] = (str(tempResult[0]))
    #========================
    # questions
    c.execute("SELECT * FROM questions WHERE form_id = " + str(formID) + ";")
    tempResult = c.fetchall()
    for each in tempResult:
        tempDict = {}
        optionArray = []
        responseArray = []
        tempDict["question_id"] = each[0]
        tempDict["question"] = str(each[1])
        tempDict["type"] = str(each[2])
        tempDict["min"] = each[4]
        tempDict["max"] = each[5]

        c.execute("SELECT * from options WHERE question_id = " + str(each[0]) + ";")
        optionDump = c.fetchall()
        if optionDump is not None:
            for eachOption in optionDump:
                tempOptionDict = {}
                tempOptionDict["text"] = str(eachOption[3])
                tempOptionDict["value"] = str(eachOption[4])
                optionArray.append(tempOptionDict)
            tempDict["option"] = optionArray
        if optionDump == None:
            tempDict["option"] = None

        #===
        c.execute("SELECT * from responses WHERE question_id = " + str(each[0]) + ";")
        responseDump = c.fetchall()
        if responseDump is not None:
            for eachResponse in responseDump:
                responseArray.append(str(eachResponse[4]))
            tempDict["response"] = responseArray
        if responseDump == None:
            tempDict["response"] = None
        #===
        questionArray.append(tempDict)
    formData["questions"] = questionArray
    close_db(db)
    return formData

# Returns a dictionary for the from
# First layer of keys are title, id, theme, owner, and questions
# The "Question" key is an array of dictionaries with each dictionary being a question
#   Each dictionary has the keys: question_id, question, type max, and options
#   Options is an array of dictionaries, each dictionary representing an option for the question
#       These dictionaries have keys, text and values. 
def getFormDataNoResponse(formID):
    #=================
    # "Global" Holder variables
    formData = {}
    questionArray = []
    #==================
    # Top parts of Dictionary
    db, c = open_db()
    c.execute("SELECT * FROM forms WHERE form_id = " + str(formID))
    tempResult = c.fetchone()
    #Basic form stuff
    formData["id"] = str(tempResult[0])
    formData["title"] = str(tempResult[1])
    formData["login_required"] = str(tempResult[3])
    formData["public_results"] = str(tempResult[4])
    formData["theme"] = str(tempResult[5])
    formData["open"] = tempResult[7]
    #Add creator ID
    ownerID = tempResult[2]
    c.execute("SELECT username FROM accounts where user_id = " + str(ownerID) + ";")
    tempResult = c.fetchone()
    formData["owner"] = (str(tempResult[0]))
    #========================
    # questions
    c.execute("SELECT * FROM questions WHERE form_id = " + str(formID) + ";")
    tempResult = c.fetchall()
    for each in tempResult:
        tempDict = {}
        optionArray = []
        tempDict["question_id"] = each[0]
        tempDict["question"] = each[1]
        tempDict["type"] = each[2]
        tempDict["min"] = each[4]
        tempDict["max"] = each[5]

        c.execute("SELECT * from options WHERE question_id = " + str(each[0]) + ";")
        optionDump = c.fetchall()
        if optionDump is not None:
            for eachOption in optionDump:
                tempOptionDict = {}
                tempOptionDict["text"] = eachOption[3]
                tempOptionDict["value"] = eachOption[4]
                optionArray.append(tempOptionDict)
            tempDict["option"] = optionArray
        else:
            tempDict["option"] = None
        questionArray.append(tempDict)
    formData["questions"] = questionArray
    close_db(db)
    return formData

#Returns a list of forms with responses in the given amount. These are the most recently created ones
def get_recent_forms(amount):
    db, c = open_db()
    c.execute("SELECT form_id FROM forms WHERE open = 1 ORDER BY created DESC LIMIT %s;" % str(amount))
    list_of_ids = c.fetchall()
    close_db(db)
    return [get_form_questions(x[0]) for x in list_of_ids]

def getSQ(username):
    db, c = open_db()
    c.execute("SELECT security_question FROM accounts WHERE username = " + "'" + str(username) + "';")
    tempResult = c.fetchone()[0]
    close_db(db)
    return str(tempResult)

def update_password(username, password):
    db, c = open_db()
    c.execute("UPDATE accounts SET password = " + "'" + str(hashed(password)) + "' WHERE username = '" + str(username) + "';")
    close_db(db)

def update_username(user_id, new_username):
    db, c = open_db()
    c.execute("UPDATE accounts SET username = ? WHERE user_id = ?;", (new_username, user_id))
    close_db(db)

#Changes a form. ColName should be one of: title, owner_id, login_required, public_results, theme, created, message, open
def update_form(formID, colName, status):
    db, c = open_db()
    c.execute("UPDATE forms SET " + colName + " = ? WHERE form_id = ?;", (status, formID))
    close_db(db)

#Changes a question. ColName should be one of: type, question, min, max, required. Its better not to change the type though.
def update_question(form_id, question_id, colName, status):
    db, c = open_db()
    c.execute("UPDATE questions SET " + colName + " = ? WHERE form_id = ? AND question_id = ?;", (status, form_id, question_id))
    close_db(db)


def get_form_questionResponses(form_id, question_id):
    formDict = getFormDataWithResponse(form_id)
    question = formDict["questions"][question_id - 1]
    if question["responses"] == "" or question["responses"] == None:
        responses = []
    else:
        responses = question["responses"]
    return responses

def get_form_questionsText(form_id):
    formDict = getFormDataNoResponse(form_id)
    tempArray = formDict["questions"]
    questionArray =[]
    for each in tempArray:
        questionArray.append(each["question"])
    return questionArray
    
def get_form_questionsOptions(form_id, question_id):
    formDict = getFormDataNoResponse(form_id)
    question = formDict["questions"][question_id - 1]
    optionArray = []
    for each in question:
        optionArray.append(each["option"])
    return optionArray

#Change form settings, where the column is a 1/0 boolean column
def toggle_form(form_id, what):
    db, c = open_db()
    c.execute("UPDATE forms SET %s = 1 - %s WHERE form_id = %s" % (what, what, str(form_id)))
    value = c.execute("SELECT %s FROM forms WHERE form_id = %s;" % (what, str(form_id))).fetchone()
    close_db(db)
    return (value[0] == 1) if value != None else False

#Deletes a form, questions and responses
def delete_form(form_id):
    db, c = open_db()
    c.execute("DELETE FROM forms WHERE form_id=?;", (form_id,))
    c.execute("DELETE FROM questions WHERE form_id=?;", (form_id,))
    c.execute("DELETE FROM responses WHERE form_id=?;", (form_id,))
    c.execute("DELETE FROM options WHERE form_id=?;", (form_id,))
    close_db(db)

#Deletes a question, multiple-choice options (when applicable), and its responses
def delete_question(form_id, question_id):
    db, c = open_db()
    # Delete the question from th DB
    c.execute("DELETE FROM questions WHERE form_id = " + str(form_id) + " AND question_id = " + str(question_id) + ";")
    c.execute("DELETE FROM responses WHERE form_id = " + str(form_id) + " AND question_id = " + str(question_id) + ";")
    c.execute("DELETE FROM options WHERE form_id = " + str(form_id) + " AND question_id = " + str(question_id) + ";")
    c.fetchall() # do this to clear / reset the cache 
    # Re-number all the existing ones
    c.execute("SELECT question_id FROM questions where form_id = " + str(form_id) + ";")
    tempCounter = c.fetchall()
    if tempCounter == 0 or tempCounter == None:
        pass
    else:
        #tempCounter = question_id + 1
        c.execute("UPDATE questions SET question_id = question_id - 1 WHERE question_id > " + str(tempCounter) + ";")
        c.execute("UPDATE responses SET question_id = question_id - 1 WHERE question_id > " + str(tempCounter) + ";")
        c.execute("UPDATE options SET question_id = question_id - 1 WHERE question_id > " + str(tempCounter) + ";")
    close_db(db)

#Deletes the options from a multiple-choice question. The which parameter should be a list of values of the options to delete. Leave empty to delete all of them
def delete_options(form_id, question_id, which=[]):
    db, c = open_db()
    if len(which) == 0:
        c.execute("DELETE FROM options WHERE form_id = ? AND question_id = ?;", (form_id, question_id))
    else:
        for index in which:
            c.execute("DELETE FROM options WHERE form_id = ? AND question_id = ? AND value = ?;", (form_id, question_id, index))
    close_db(db)

#deletes account, but not its associated forms
def delete_account(user_id):
    db, c = open_db()
    c.execute("DELETE FROM accounts WHERE user_id = ?;", (user_id,))
    close_db(db)

#Deletes a single response givena response_id, or all responses to a form if the 2nd parameter is ommitted
def delete_response(form_id, response_id=None):
    db, c = open_db()
    if response_id != None:
        c.execute("DELETE FROM responses WHERE form_id = ? AND response_id = ?;", (form_id, response_id))
        if response_id >= 0:
            c.execute("UPDATE responses SET response_id = response_id - 1 WHERE response_id > ?;", (response_id,))
        else:
            c.execute("UPDATE responses SET response_id = response_id + 1 WHERE response_id < ?;", (response_id,))
    else:
        c.execute("DELETE FROM responses WHERE form_id = ?;", (form_id,))
    close_db(db)

def create_tables():
    db, c = open_db()
    c.execute("CREATE TABLE IF NOT EXISTS forms(form_id INTEGER PRIMARY KEY, title TEXT, owner_id INTEGER, login_required INTEGER, public_results INTEGER, theme TEXT, created TEXT, open INTEGER, message TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS responses(form_id INTEGER, question_id INTEGER, user_id INTEGER, response_id INTEGER, response BLOB, timestamp TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS questions(question_id INTEGER, question text, type TEXT, form_id INTEGER, required INTEGER, min INTEGER, max INTEGER, optional INTEGER);")
    c.execute("CREATE TABLE IF NOT EXISTS options(form_id INTEGER, question_id INTEGER, option_index INTEGER PRIMARY KEY, text_user_sees TEXT, value TEXT);")
    c.execute("CREATE TABLE IF NOT EXISTS accounts(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT, security_question TEXT, security_question_answer TEXT);")
    #c.execute("CREATE TABLE IF NOT EXISTS styles(form_id INTEGER, row INTEGER, column INTEGER, property TEXT, value TEXT);")
    close_db(db)
    
