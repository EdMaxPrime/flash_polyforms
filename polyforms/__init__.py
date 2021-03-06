from flask import Flask, render_template, request, session, redirect, url_for, flash, Response, abort, json
from jinja2 import escape
from functools import wraps
import os   #for secret key creation and file system exploration
import random   #for the generate_questions random word generator
import json
from utils import db
from utils import test
from utils import config

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
DIR = os.path.dirname(__file__) or '.'
DIR += '/'
db.use_database(DIR)
db.create_tables()
config.load_themes(DIR + "data/themes.json")
app.secret_key = config.get_secret_key(DIR + "data/secret")

#Usage: @valid_session (below the route decorator)
#This will redirect to login page if the session expired, or if user is not logged in
def valid_session(message="You need to login again", strict=False, redirectForm=""):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session or "user_id" not in session:
                flash(message)
                return redirect(url_for("login_page", redirect=redirectForm))
            elif strict and db.getID("accounts", "user_id", "username", str(session["user"])) != session["user_id"]:
                session.pop("user")
                session.pop("user_id")
                flash(message)
                return redirect(url_for("login_page", redirect=redirectForm))
            if db.did_session_expire(session.get("user", ""), session.get("token", "")):
                session.pop("user")
                session.pop("user_id")
                flash("You need to login again")
                return redirect(url_for("login_page", redirect=redirectForm))
            else:
                return f(*args, **kwargs)
        return decorated_function
    return decorator

#This decorator will display the 404 page if the form in the url is not found
def form_must_exist(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "POST":
            form_id = request.form.get("id", "")
        else:
            form_id = request.args.get("id", "")
        if test.form_exists(form_id) == False and form_id != "feedback": #db check for existing form
            return render_template("404.html", username=session.get("user", "")), 404
        return f(*args, **kwargs)
    return decorated_function


@app.route('/test')
def deploy_test():
    print "=====================================\nConsole Message\n"
    print DIR + "\n====================================="
    body = "<h2> Deployment Test </h2>"
    body+= "DIR: " + DIR + "<br>"
    body+= '<img src="' + url_for('static', filename='img/cat_cage.jpg') + '" width="500"</img>'
    return body

@app.route('/')
def home_page():
    return render_template("index.html", username=session.get("user", ""), forms=db.get_recent_forms(24), totalForms=db.get_number_of("forms"), totalQ=db.get_number_of("questions"), totalAns=db.get_number_of("responses"))

#Shows the form to login
@app.route('/login')
def login_page():
    return render_template('login.html', username=session.get("user", ""), redirect=request.args.get("redirect", ""))

#Verifies username and password, redirects home on success
@app.route('/login/verify', methods=["POST"])
def login_logic():
    uname = request.form.get("username", "")
    pword = request.form.get("password", "")
    form_id = request.form.get("redirect")
    submitType = request.form.get("submit", "")
    if db.validate_login(uname, pword) == True:
        session["user"] = uname
        session["user_id"] = db.getID("accounts", "user_id", "username", str(uname))
        session["token"] = db.add_session(uname)
    else:
        flash("Wrong username or password")
        return redirect(url_for("login_page", redirect=form_id))
    #This is to redirect people that are filling out a form that requires login
    if form_id == None or form_id == "":
        return redirect(url_for("home_page"))
    else:
        return redirect(url_for("display_form", id=form_id))

#Shows the form to signup
@app.route('/join')
def signup_page():
    return render_template("signup.html", username=session.get("user", ""))

#Verifies that this account can be made, redirects to login page on success
@app.route('/join/verify', methods=['POST'])
def signup_logic():
    uname = request.form.get("username1", "")
    pword = request.form.get("password1", "")
    sq = request.form.get("question", "")
    sqAns = request.form.get("answer", "")
    if len(uname) == 0:
        flash("Username can't be blank")
    elif uname != request.form.get("username2", ""):
        flash("You didn't type the username correctly the 2nd time")
    elif len(pword) == 0:
        flash("Password can't be blank")
    elif pword != request.form.get("password2", ""):
        flash("You didn't type the password correctly the 2nd time")
    elif db.user_exists(uname): #check its not already existing
        flash("This username already exists")
    else:
        db.add_account(uname, pword, sq, sqAns)
        flash("Success! Your account has been made. Please login.")
        return redirect(url_for("login_page"))
    return redirect(url_for("signup_page"))

@app.route('/form/respond', methods=["GET"])
@form_must_exist
def display_form():
    form_id = request.args.get("id")
    username = session.get("user", "")
    session_token = session.get("token", "")
    if form_id == "feedback":
        form = config.FEEDBACK
    elif "bad" in request.args and is_integer(request.args["bad"]):
        form = db.get_form_questions_1response(form_id, request.args["bad"])
        db.delete_response(form_id, response_id=int(request.args["bad"]))
    else:
        form = db.get_form_questions(form_id)
    if (username == None or username == "" or db.did_session_expire(username, session_token)) and form["login_required"]: #insert db check for login required
        flash("Please login to view this form. You will be redirected after you login.")
        return redirect(url_for("login_page", redirect=form_id))
    else:
        theme = config.get_theme(form["theme"])
        return render_template("form_themes/"+theme["template_form"], title=form["title"], description=form["description"], questions=form["questions"], form_id=form_id, theme=theme, form=form)

#Shortcut URLS
@app.route('/f/<form_id>')
def display_form_shortcut(form_id):
    return redirect(url_for("display_form", id=form_id))

#This will store the responses to the form and then redirect to a Thank You
@app.route('/form/submit', methods=['POST'])
@form_must_exist
def process_form():
    form_id = request.form.get("id", "")
    username = session.get("user", "")
    user_id = session.get("user_id")
    data = {}
    form = db.get_form_questions(form_id) if form_id != "feedback" else config.FEEDBACK
    number_of_questions = len(form["questions"])
    for qnumber in range(1, number_of_questions+1):
        if form["questions"][qnumber-1]["type"] == "choice":
            data[qnumber] = request.form.getlist(str(qnumber), None) or []
        else:
            data[qnumber] = request.form.get(str(qnumber), None)
    errors = test.validate_form_submission(form, data)
    if not test.can_respond(user_id, form_id, form["login_required"]):
        errors.append(("You can't respond to this form more than once", "general"))
    if len(errors) > 0: #invalid submission
        if request.form.get("response") == "json":
            return Response(json.dumps({"status": "bad", "errors": errors, "answers": data, "form_id": form_id}), mimetype="application/json")
        else: 
            qnumber = 1
            response_id = None
            while qnumber <= number_of_questions:
                response_id = db.add_response_negative(form_id, user_id, qnumber, data[qnumber], response_id)
                qnumber += 1
            for e in errors:
                flash(e[0], e[1])
            return redirect(url_for("display_form", id=form_id, bad=response_id))
    else: #valid submission
        qnumber = 1
        response_id = None
        while qnumber <= number_of_questions:
            response_id = db.add_response(form_id, user_id, qnumber, data[qnumber], response_id)
            qnumber += 1
        if request.form.get("response") == "json":
            return Response(json.dumps({"status": "ok", "message": codes_to_html(form["message"], form), "form_id": form_id}), mimetype="application/json")
        else:
            return redirect(url_for("thankyou", id=form_id))

#Thank you message once form is filled out
@app.route('/form/end')
@form_must_exist
def thankyou():
    id = request.args["id"]
    form = db.get_form_meta(id) if id != "feedback" else config.FEEDBACK
    theme = config.get_theme(form["theme"])
    return render_template("form_themes/"+theme["template_end"], form=form, theme=theme)

#View the responses to your form and make charts
@app.route('/form/view')
@form_must_exist
def responses_page():
    form_id = request.args.get("id", "-1")
    user_id = session.get("user_id", "")
    username = session.get("user", "")
    #form = db.getFormData(form_id)
    form = db.get_form_responses(form_id)
    isowner = form["owner_id"] == user_id
    if isowner or form["public_results"] == True: #you have permission to view this
        return render_template("spreadsheet.html", username=username, title=form['title'], headers=form['headers'], data=form['data'], jsonData=json.dumps(form['data']), form_id=form_id, types=form["types"], isowner=isowner, form=form)
    else: #you dont have permission to view this
        return render_template("unauthorized.html", username=username)

#CSV
@app.route('/form/view/form.csv')
@form_must_exist
def responses_csv():
    form_id = request.args.get("id", "-1")
    form = db.get_form_responses(form_id)
    if session.get("user_id", "") != form["owner_id"] and form["public_results"] == False: #dont have permission to download
        return render_template("unauthorized.html", username=session.get("user", ""))
    else: #you do have permission to download
        return Response(render_template("results_csv", headers=form['headers'], data=form['data']), mimetype="text/csv")

#JSON
@app.route('/form/view/form.json')
@form_must_exist
def responses_json():
    form_id = request.args.get("id", "-1")
    form = db.get_form_responses(form_id)
    if session.get("user_id", "") != form["owner_id"] and form["public_results"] == False: #dont have permission to download
        return render_template("unauthorized.html", username=session.get("user", ""))
    else: #you do have permission to download
        return Response(render_template("results_json", headers=form['headers'], data=form['data']), mimetype="application/json")
#XML
@app.route('/form/view/form.xml')
@form_must_exist
def responses_xml():
    form_id = request.args.get("id", "-1")
    form = db.get_form_responses(form_id)
    if session.get("user_id", "") != form["owner_id"] and form["public_results"] == False: #dont have permission to download
        return render_template("unauthorized.html", username=session.get("user", ""))
    else: #you do have permission to download
        return Response(render_template("results_xml", headers=form['headers'], data=form['data'], owner=form["owner"], created=form["created"], title=form["title"]), mimetype="application/xml")

#change form settings
@app.route('/form/toggle')
def change_form():
    username = session.get("user", "")
    user_id = session.get("user_id", "")
    form_id = request.args.get("id", "-1")
    setting = request.args.get("setting", "")
    result = False
    if test.can_edit(user_id, form_id):
        if setting == "open":
            result = db.toggle_form(form_id, "open")
            if result == True:
                result = "Your form is now accepting responses"
            else:
                result = "Your form is no longer accepting responses"
        elif setting == "public":
            result = db.toggle_form(form_id, "public_results")
            if result == True:
                result = "Your form's results are now public. Anyone with the link can view them. Press the button below and then copy the link in the address bar."
            else:
                result = "Your form's results are now private"
        elif setting == "delete_response":
            result = "You deleted response #" + request.args.get("rid", "") + "."
            db.delete_response(form_id, response_id=request.args.get("rid"))
        elif setting == "delete":
            return render_template("delete.html", username=username, form_id=form_id)
        elif "theme" in request.args and config.theme_exists(request.args["theme"]):
            result = 'Your form has the "%s" theme' % config.get_theme(request.args["theme"])["display_name"]
            db.update_form(form_id, "theme", request.args["theme"])
        #update form's edit time
        if result != False:
            db.update_edited_time(form_id)
        #determine response content-type
        if "response" in request.args:
            status = "ok" if result != False else "bad"
            return Response('{"status": "%s", "message": "%s"}' % (status, str(result)), mimetype="application/json")
        elif "redirect" in request.args:
            return redirect(request.args["redirect"] + "?id=" + form_id)
        else:
            return render_template("update.html", message=result, form_id=form_id, username=username)
    else:
        if "response" in request.args:
            return Response('{"status": "bad", "message": "You do not have permission to edit this form"}', mimetype="application/json")
        else:
            return render_template("unauthorized.html", username=username)

#Delete a form
@app.route('/form/delete')
@valid_session("You must be logged in to delete your form")
def delete_form():
    username = session.get("user", "")
    user_id = session.get("user_id", "")
    form_id = request.args.get("id", "-1")
    if test.can_edit(user_id, form_id):
        db.delete_form(form_id)
        return redirect(url_for("my_forms"))
    else:
        return render_template("unauthorized.html", username=username)

#Shows information about a form
@app.route('/form/info')
def info_form():
    username = session.get("user", "")
    form_id = request.args.get("id", "-1")
    if test.form_exists(form_id) == False:
        return render_template("404.html", username=username), 404
    else:
        form = db.get_form_meta(form_id)
        return render_template("info.html", username=username, form=form, isowner=(form["owner"] == username))

#Make a new form
@app.route('/form/new')
@valid_session("You need an account to make a form")
def create():
    if "user" in session:
        form = config.EMPTY_FORM
        return render_template("create.html", username=session.get("user", ""), form=form, themes=config.THEMES)
    else:
        flash("You need an account to make a form")
        return redirect(url_for("login_page"))

@app.route('/addQuestions', methods = ["POST", "GET"])
@valid_session("You must be logged in to make a form", True)
def addQuestions():
    if "login_required" not in request.args.keys():
        loginReq = 0
    else:
        loginReq = 1
    if "public_results" not in request.args.keys():
        publicReq = 0
    else:
        publicReq = 1
    if "message" not in request.args.keys() or len(request.args["message"]) == 0:
        message = "Your response has been recorded"
    else:
        message = request.args["message"]
    if config.theme_exists(request.args.get("theme")):
        theme = request.args.get("theme")
    else:
        theme = "basic"
    formID = db.add_form(session.get("user_id", ""), request.args.get("title", ""), loginReq, publicReq, theme, 1, message, request.args.get("description", ""))
    i=0
    while (str(i) + ".question" in request.args.keys()):
        if request.args[str(i) + ".type"] == "0":
            type = "short"
        elif request.args[str(i) + ".type"] == "1":
            type = "long"
        elif request.args[str(i) + ".type"] == "2":
            type = "int"
        elif request.args[str(i) + ".type"] == "3":
            type = "number"
        elif request.args[str(i) + ".type"] == "4":
            type = "choice"
        else:
            type = request.args[str(i) + ".type"]
        if (str(i) + ".required" not in request.args.keys()):
            required = 0
        else:
            required = 1
        if (is_positive_number(request.args.get(str(i) + ".min")) and type != "number" and type != "int"):
            min = request.args[str(i) + ".min"]
        elif (is_integer(request.args.get(str(i) + ".min")) and (type == "number" or type == "int")):
            min = request.args[str(i) + ".min"]
        else:
            min = None
        if (is_positive_number(request.args.get(str(i) + ".max")) and type != "number" and type != "int"):
            max = request.args[str(i) + ".max"]
        elif (is_integer(request.args.get(str(i) + ".max")) and (type == "number" or type == "int")):
            max = request.args[str(i) + ".max"]
        else:
            max = None
        question_id = db.add_question(formID, request.args[str(i) + ".question"], type, required, min, max)
        if type == "choice":
            for o in request.args.get(str(i) + ".answers", "").splitlines():
                if len(o) == 0:
                    continue
                ovalue = o.split(")", 1)[0]
                otext = o.split(")", 1)[-1]
                db.add_option(formID, question_id, otext, ovalue)
        i+=1
    return redirect(url_for("my_forms"))

@app.route('/form/edit', methods=["GET", "POST"])
@valid_session("You need to be logged in to edit this form")
@form_must_exist
def edit_form():
    username = session.get("user", "")
    user_id = session.get("user_id", "")
    #Get form id
    if request.method == "GET":
        form_id = request.args.get("id")
    else:
        form_id = request.form.get("id")
    #Make sure this person has permission and the form exists
    if not test.can_edit(user_id, form_id):
        return render_template("unauthorized.html", username=username)
    else:
        #Either display the form or process the results
        if request.method == "POST":
            if "title" in request.form:
                db.update_form(form_id, "title", request.form["title"])
            if "public_results" in request.form:
                db.update_form(form_id, "public_results", 1)
            else:
                db.update_form(form_id, "public_results", 0)
            if "login_required" in request.form:
                db.update_form(form_id, "login_required", 1)
            else:
                db.update_form(form_id, "login_required", 0)
            if "open" in request.form:
                db.update_form(form_id, "open", 1)
            else:
                db.update_form(form_id, "open", 0)
            if "theme" in request.form and config.theme_exists(request.form["theme"]):
                db.update_form(form_id, "theme", request.form["theme"])
            if "description" in request.form:
                db.update_form(form_id, "description", request.form["description"])
            if "message" in request.form:
                db.update_form(form_id, "end_message", request.form["message"])
            #Now do the questions
            new_order = []
            to_be_deleted = []
            question_id = 1
            number_of_questions = db.get_num_questions(form_id)
            while str(question_id) + ".question" in request.form:
                i = str(question_id)
                if question_id > number_of_questions: #if this is a new question, add it
                    db.add_question(form_id, request.form[i+".question"], "short", 0, None, None) #default values: one-line question that's optional with no min/max
                else: #if this is an exisiting question, update it
                    db.update_question(form_id, question_id, "question", request.form[i+".question"])
                new_order.append(request.form.get(i+".newIndex", i))
                if request.form.get(i+".delete") == "delete":
                    to_be_deleted.append(int(new_order[-1]))
                if i+".required" in request.form:
                    db.update_question(form_id, question_id, "required", 1)
                else:
                    db.update_question(form_id, question_id, "required", 0)
                if i+".min" in request.form and is_integer(request.form[i+".min"]):
                    db.update_question(form_id, question_id, "min", request.form[i+".min"])
                else:
                    db.update_question(form_id, question_id, "min", None)
                if i+".max" in request.form and is_integer(request.form[i+".max"]):
                    db.update_question(form_id, question_id, "max", request.form[i+".max"])
                else:
                    db.update_question(form_id, question_id, "max", None)
                if i+".answers" in request.form:
                    db.delete_options(form_id, question_id)
                    for o in request.form[i+".answers"].splitlines():
                        if len(o) == 0:
                            continue
                        ovalue = o.split(")", 1)[0].strip()
                        otext = o.split(")", 1)[-1].strip()
                        db.add_option(form_id, question_id, otext, ovalue)
                if i+".type" in request.form:
                    db.update_question(form_id, question_id, "type", request.form[i+".type"])
                question_id += 1
            db.update_order(form_id, new_order)
            to_be_deleted.sort()
            #delete loop here
            for i in range(0, len(to_be_deleted)):
                #print "deleting %d which is now index %d, %d left" % (to_be_deleted[i], to_be_deleted[i]-i, len(to_be_deleted) - i - 1)
                db.delete_question(form_id, to_be_deleted[i] - i)
            db.update_edited_time(form_id)
            flash("Your changes have been saved")
        return render_template("edit.html", username=username, form=db.get_form_questions(form_id), themes=config.THEMES, isowner=True)

#This lists all the forms in your account. Clicking on a form will bring you to /form/view
@app.route('/my/forms')
@valid_session("You must be logged in to view this page")
def my_forms():
    user_id = session.get("user_id", "")
    return render_template("ownforms.html", username=session.get("user",""), forms_user_made=db.get_forms_by(user_id))

#View settings for your account
@app.route('/my/settings')
@valid_session("You must be logged in to view this page")
def settings_page():
    username = session.get("user", "")
    return render_template("settings.html", username=username)

#Verify that you are able to reset your password by answering the security question
@app.route('/my/settings/password')
def reset_password_page():
    #if "user" not in session:
    #    flash("You must be logged in to view this page")
    #    return redirect(url_for("login_page"))
    try:
        username = session.get("user", "")
    except KeyError:
        username = ""
    return render_template("pass_reset.html", username=username)

#This is where the password reset form redirects. This method will check the DB for security question. Then it will change the password. Then it will redirect to login
@app.route('/my/settings/password-update', methods=["POST"])
def reset_password_logic():
    uname = request.form.get("username")
    question = request.form.get("question")
    answer = request.form.get("answer")
    if not (db.user_exists(uname)):
        flash("Username is wrong or does not exist. Please re-enter an username")
    elif not db.validate_resetPassword(uname, question, answer):
        flash("Security Question and/or answer is wrong. Please make sure the answer and question match the ones you used when signing up. Capitalization matters.")
    elif request.form.get("password") == request.form.get("password2"):
        db.update_password(uname, request.form.get("password", ""))
        if "user" in session:
            session.pop("user")
        flash("Success! Your password has been changed.")
        return redirect(url_for("login_page"))
    else:
        flash("The new password doesn't match in both boxes")
    return redirect(url_for("reset_password_page"))

#change username or delete account
@app.route('/my/settings/update', methods = ["POST"])
@valid_session("You need to be logged in to do this")
def change_account():
    username = session.get("user", "")
    user_id = session.get("user_id", "")
    setting = request.form.get("setting", "")
    if setting == "Change":
        new_username = request.form.get("new_username", "")
        if len(new_username) == 0:
            flash("You can't have an empty username")
        elif db.user_exists(new_username) and new_username != username:
            flash("This username is already in use")
        else:
            db.update_username(user_id, new_username)
            session["user"] = new_username
    elif setting == "Delete":
        myforms = db.get_forms_by(user_id)
        for form in myforms:
            db.delete_form(form["form_id"])
        db.delete_account(user_id)
        return redirect(url_for("logout"))
    return redirect(url_for("settings_page"))

@app.route('/about')
def about_page():
    return render_template("about.html", username=session.get("user", ""))

@app.route('/logout')
def logout():
    if "user" in session:
        uname = session["user"]
        session.pop("user")
        session.pop("user_id")
        # Do nothing if there is no form_id
        try:
            session.pop("form_id")
        except KeyError:
            pass
        if "token" in session:
            session_token = session.pop("token")
            if "everywhere" in request.args:
                db.delete_session(uname, session_token)
    return redirect(url_for("home_page"))

#This can be used as a Jinja filter
@app.template_filter('dtnormal')
def format_datetime(value="2018-05-26 12:00:00"):
    months = ["Jan", "Feb", "March", "April", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m = int(value[5:7]) - 1
    d = value[8:10]
    y = value[0:4]
    t = value[11:-3]
    return "%s %s at %s" % (months[m], d, t)

@app.template_filter('attributes')
def conditional_attributes(question):
    result = ""
    if question['required'] == True:
        result += "required "
    if question['min'] != None and question['min'] != "":
        if question['type'] == "long" or question['type'] == "short":
            result += 'minlength="%d" ' % question['min']
        elif question['type'] == "number" or question['type'] == "int":
            result +='min="%d" ' % question['min']
    if question['max'] != None and question['max'] != "":
        if question['type'] == "long" or question['type'] == "short":
            result += 'maxlength="%d" ' % question['max']
        elif question['type'] == "number" or question['type'] == "int":
            result +='max="%d" ' % question['max']
    return result

@app.template_filter('linebreaks')
def newline_br(value):
    if value != None and len(value) > 0:
        lines = value.split("\n")
    else:
        lines = ""
    return "<br>".join([escape(s) for s in lines])

@app.template_filter('msgCodes')
def codes_to_html(value, form):
    return value.replace("[SIGNATURE]", "<em>%s</em>"%form["owner"]).replace("[HOWMANY]", str(form["num_responses"])).replace("[AGAIN]", '<a href="/f/%s">Submit another response</a>'%str(form["id"])).replace("[RESULTS]", '<a href="/form/view?id=%s">See the responses</a>'%str(form["id"]))

@app.template_filter('formatChoice')
def formatChoice(value):
    if value["text"] == value["value"]:
        return value["text"]
    else:
        return value["value"] + ")" + value["text"]

def is_positive_number(thing):
    try:
        thing = int(thing)
        return thing > 0
    except:
        return False

def is_integer(thing):
    try:
        int(thing)
        return True
    except:
        return False

#Will not be executed if this is imported by WSGI
if __name__ == "__main__":
    app.debug = True
    app.run()

