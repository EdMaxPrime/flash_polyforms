from flask import Flask, render_template, request, session, redirect, url_for, flash, Response, abort, json
from jinja2 import escape
import os   #for secret key creation and file system exploration
import random   #for the generate_questions random word generator
from utils import db
from utils import test
from utils import security

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
DIR = os.path.dirname(__file__) or '.'
DIR += '/'
db.use_database(DIR)
db.create_tables()
THEMES = ["basic.html", "light.html", "dark.html"]
app.secret_key = security.get_secret_key(DIR + "data/secret")

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
    return render_template("index.html", username=session.get("user", ""), forms=db.get_recent_forms(24))

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
    '''
    #Dummy account to test stuff
    if pword == "123":
        session["user"] = "Root" # NSA Backend
        session["user_id"] = "1"
    '''
    if db.validate_login(uname, pword) == True:
        session["user"] = uname
        session["user_id"] = db.getID("accounts", "user_id", "username", str(uname))
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
def display_form():
    form_id = request.args.get("id")
    username = session.get("user", "")
    if test.form_exists(form_id) == False: #insert db check for existing form
        return render_template("404.html", username=username), 404
    #now that we know the form exists...
    form = db.get_form_questions(form_id)
    print form["questions"]
    if (username == None or username == "") and form["login_required"]: #insert db check for login required
        flash("Please login to view this form. You will be redirected after you login.")
        return redirect(url_for("login_page", redirect=form_id))
    else:
        template_name = form["theme"]
        return render_template("form_themes/"+template_name, title=form["title"], questions=form["questions"], form_id=form_id)

#Shortcut URLS
@app.route('/f/<form_id>')
def display_form_shortcut(form_id):
    return redirect(url_for("display_form", id=form_id))

#This will store the responses to the form and then redirect to a Thank You
@app.route('/form/submit', methods=['POST'])
def process_form():
    form_id = request.form.get("id", "")
    username = session.get("user", "")
    user_id = session.get("user_id", "")
    if not test.form_exists(form_id):
        return render_template("404.html", username=username), 404
    else:
        data = {}
        form = db.get_form_questions(form_id)
        number_of_questions = len(form["questions"])
        for qnumber in range(1, number_of_questions+1):
            if form["questions"][qnumber-1]["type"] == "choice":
                data[qnumber] = request.form.getlist(str(qnumber), None)
            else:
                data[qnumber] = request.form.get(str(qnumber), None)
        errors = test.validate_form_submission(form_id, data)
        if len(errors) > 0:
            for e in errors:
                flash(e)
                return redirect(url_for("display_form", id=form_id))
        else:
            qnumber = 1
            while qnumber <= number_of_questions:
                db.add_response(form_id, user_id, qnumber, data[qnumber], qnumber == 1)
                qnumber += 1
            return redirect(url_for("thankyou", id=form_id))

#Thank you message once form is filled out
@app.route('/form/end')
def thankyou():
    id = request.args.get("id", "-1")
    if test.form_exists(id):
        form = db.get_form_meta(id)
        return render_template("form_themes/end_"+form["theme"], owner=form["owner"], title=form["title"], message=form["message"])
    else:
        return render_template("unauthorized.html", username=session.get("user", ""))

#View the responses to your form and make charts
@app.route('/form/view')
def responses_page():
    form_id = request.args.get("id", "-1")
    user_id = session.get("user_id", "")
    username = session.get("user", "")
    if test.form_exists(form_id) == False:
        return render_template("404.html", username=username)
    else:
        #form = db.getFormData(form_id)
        form = db.get_form_responses(form_id)
        if form["owner"] == username or form["public_results"] == True: #you have permission to view this
            return render_template("spreadsheet.html", username=username, title=form['title'], headers=form['headers'], data=form['data'], jsonData=json.dumps(form['data']), form_id=form_id, types=form["types"])
        else: #you dont have permission to view this
            return render_template("unauthorized.html", username=username)

#CSV
@app.route('/form/view/form.csv')
def responses_csv():
    if not ("id" in request.args):
        return render_template("404.html", username=session.get("user", "")), 404
    else:
        form_id = request.args.get("id", "-1")
        form = db.get_form_responses(form_id)
        print form["data"]
        if session.get("user", "") != form["owner"] and form["public_results"] == False: #dont have permission to download
            return render_template("unauthorized.html", username=session.get("user", ""))
        else: #you do have permission to download
            return Response(render_template("results_csv", headers=form['headers'], data=form['data']), mimetype="text/csv")

#JSON
@app.route('/form/view/form.json')
def responses_json():
    if not ("id" in request.args):
        return render_template("404.html", username=session.get("user", "")), 404
    else:
        form_id = request.args.get("id", "-1")
        form = db.get_form_responses(form_id)
        if session.get("user", "") != form["owner"] and form["public_results"] == False: #dont have permission to download
            return render_template("unauthorized.html", username=session.get("user", ""))
        else: #you do have permission to download
            return Response(render_template("results_json", headers=form['headers'], data=form['data']), mimetype="application/json")
#XML
@app.route('/form/view/form.xml')
def responses_xml():
    if not ("id" in request.args):
        return render_template("404.html", username=session.get("user", "")), 404
    else:
        form_id = request.args.get("id", "-1")
        form = db.get_form_responses(form_id)
        if session.get("user", "") != form["owner"] and form["public_results"] == False: #dont have permission to download
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
        elif setting == "basic":
            result = "Your form has the basic theme"
            db.update_form(form_id, "theme", "basic.html")
        elif setting == "light":
            result = "Your form has the light theme"
            db.update_form(form_id, "theme", "light.html")
        elif setting == "dark":
            result = "Your form has the dark theme"
            db.update_form(form_id, "theme", "dark.html")
        elif setting == "delete":
            return render_template("delete.html", username=username, form_id=form_id)
        #determine response content-type
        if "response" in request.args:
            status = "success" if result != False else "error"
            return Response('{"status": "%s", "message": "%s"}' % (status, str(result)), mimetype="application/json")
        else:
            return render_template("update.html", message=result, form_id=form_id, username=username)
    else:
        return render_template("unauthorized.html", username=username)

#Delete a form
@app.route('/form/delete')
def delete_form():
    username = session.get("username", "")
    user_id = session.get("user_id", "")
    form_id = request.args.get("id", "-1")
    if test.can_edit(user_id, form_id):
        db.delete_form(form_id)
        return redirect(url_for("my_forms"))
    else:
        return render_template("unauthorized.html", username=username)

#Make a new form
@app.route('/form/new')
def create():
    if "user" in session:
        return render_template("create.html", username=session.get("user", ""))
    else:
        flash("You need an account to make a form")
        return redirect(url_for("login_page"))

@app.route('/addQuestions', methods = ["POST", "GET"])
def addQuestions():
    if "loginReq" not in request.args.keys():
        loginReq = 0
    else:
        loginReq = 1
    if "publicReq" not in request.args.keys():
        publicReq = 1
    else:
        publicReq = 0
    if "message" not in request.args.keys() or len(request.args["message"]) == 0:
        message = "Your response has been recorded"
    else:
        message = request.args["message"]
    formID = db.add_form(session.get("user_id", ""), request.args.get("title", ""), loginReq, publicReq, request.args.get("theme", "basic.html"), 1, message)
    i=0
    while (str(i) + ".question" in request.args.keys()):
        if (str(i) + ".required" not in request.args.keys()):
            required = 0
        else:
            required = 1
        if (is_positive_number(request.args.get(str(i) + ".min"))):
            min = request.args[str(i) + ".min"]
        else:
            min = None
        if (is_positive_number(request.args.get(str(i) + ".max"))):
            max = request.args[str(i) + ".max"]
        else:
            max = None
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
        question_id = db.add_question(formID, request.args[str(i) + ".question"], type, required, min, max)
        if type == "choice":
            for o in request.args.get(str(i) + ".answers", "").splitlines():
                ovalue = o.split(")", 1)[0]
                otext = o.split(")", 1)[-1]
                db.add_option(formID, question_id, otext, ovalue)
        i+=1
    return redirect(url_for("my_forms"))

@app.route('/form/edit', methods=["GET", "POST"])
def edit_form():
    username = session.get("user", "")
    user_id = session.get("user_id", "")
    #Get form id
    if request.method == "GET":
        form_id = request.args.get("id")
    else:
        form_id = request.form.get("form_id")
    #Make sure this person has permission and the form exists
    if not test.form_exists(form_id):
        return render_template("404.html", username=username), 404
    elif not test.can_edit(user_id, form_id):
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
            if "theme" in request.form and request.form["theme"] in THEMES:
                db.update_form(form_id, "theme", request.form["theme"])
            if "message" in request.form:
                db.update_form(form_id, "message", request.form["message"])
            #Now do the questions
            question_id = 1
            while str(question_id) + ".question" in request.form:
                i = str(question_id)
                db.update_question(form_id, question_id, "question", request.form[i+".question"])
                if i+".required" in request.form:
                    db.update_question(form_id, question_id, "required", 1)
                else:
                    db.update_question(form_id, question_id, "required", 0)
                if i+".min" in request.form and is_positive_number(request.form[i+".min"]):
                    db.update_question(form_id, question_id, "min", request.form[i+".min"])
                else:
                    db.update_question(form_id, question_id, "min", None)
                if i+".max" in request.form and is_positive_number(request.form[i+".max"]):
                    db.update_question(form_id, question_id, "max", request.form[i+".max"])
                else:
                    db.update_question(form_id, question_id, "max", None)
                if i+".answers" in request.form:
                    print "choices here"
                question_id += 1
        return render_template("edit.html", username=username, form=db.get_form_questions(form_id))

#This lists all the forms in your account. Clicking on a form will bring you to /form/view
@app.route('/my/forms')
def my_forms():
    if "user" not in session:
        flash("You must be logged in to view this page")
        return redirect(url_for("login_page"))
    user_id = session.get("user_id", "")
    return render_template("ownforms.html", username=session.get("user",""), forms_user_made=db.get_forms_by(user_id))

#View settings for your account
@app.route('/my/settings')
def settings_page():
    if "user" not in session:
        flash("You must be logged in to view this page")
        return redirect(url_for("login_page"))
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
        session.pop("user")
        session.pop("user_id")
        # Do nothing if there is no form_id
        try:
            session.pop("form_id")
        except KeyError:
            pass
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

def is_positive_number(thing):
    try:
        thing = int(thing)
        return thing > 0
    except:
        return False

#Will not be executed if this is imported by WSGI
if __name__ == "__main__":
    app.debug = True
    app.run()

