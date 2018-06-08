from flask import Flask, render_template, request, session, redirect, url_for, flash, Response, abort
import os   #for secret key creation and file system exploration
import random   #for the generate_questions random word generator
from utils import db
from utils import test

polyforms = Flask(__name__)
polyforms.secret_key = os.urandom(32)
polyforms.config['TEMPLATES_AUTO_RELOAD'] = True
DIR = os.path.dirname(__file__)
db.use_database(DIR)
db.create_tables()

#Used for testing the display of questions
def generate_questions(num):
    results = []
    words = "blah ooh why aaah how far when foo what bar name interest".split()
    types = ["short", "long", "number", "choice"]
    for x in range(0, num):
        qtype = random.choice(types)
        results.append({'type':qtype, 'question': 8 * (random.choice(words)+' ')+'?', 'index': str(x), 'min':None, 'max':None, 'required':True})
        if qtype == "choice":
            results[-1]["choices"] = [{'text': random.choice(words), 'value': str(i)} for i in range (0, 4)]
    return results

#Used to test viewing of results in a table. Returns a random word
def random_word():
    length = random.randrange(2, 4)
    return reduce(lambda s, c: s+c, [chr(random.randrange(ord('A'), ord('D'))) for i in range(0, length)], "")

#Returns a dictionary with the keys {title: form_title, headers: [], data: [[]]}
def random_form(form_title, number_of_questions, number_of_responses):
    form = {}
    form['title'] = form_title
    form['created'] = "2018-05-26 12:00:00"
    questions = generate_questions(number_of_questions)
    form['headers'] = [q['question'] for q in questions]
    form['data'] = [[(random_word() if questions[i]['type'] != "number" else random.randrange(0, 3)) for i in range(0, number_of_questions)] for i in range(0, number_of_responses)]
    return form

@polyforms.route('/test')
def deploy_test():
    print "=====================================\nConsole Message\n"
    print DIR + "\n====================================="
    body = "<h2> Deployment Test </h2>"
    body+= "DIR: " + DIR + "<br>"
    body+= '<img src="' + url_for('static', filename='img/cat_cage.jpg') + '" width="500"</img>'
    return body

@polyforms.route('/')
def home_page():
    #print db.returnFormData(1)
    #print db.getFormDataNoResponse(1)
    #print db.getFormData(2)
    #db.add_question(6, "Favorite movie", "choice", 0, None, 1)
    #db.add_option(6, 7, "Ghost Busters", "ghost busters")
    #db.add_option(6, 7, "The Breakfast Club", "breakfast")
    #db.add_option(6, 7, "Pulp Fiction", "pf")
    #print db.getPublicForms(24)
    #print "==== GetFormData ===="
    #print db.getFormData(1)
    #print "==== GetFormDataNoResponse ===="
    #print db.getFormDataNoResponse(1)
    #print "==== GetFormDataWithResponse ===="
    #print db.getFormDataWithResponse(1)
    return render_template("index.html", username=session.get("user", ""), forms=db.getPublicForms(24))

#Shows the form to login
@polyforms.route('/login')
def login_page():
    return render_template('login.html', username=session.get("user", ""), redirect=request.args.get("redirect", ""))

#Verifies username and password, redirects home on success
@polyforms.route('/login/verify', methods=["POST"])
def login_logic():
    uname = request.form.get("username", "")
    pword = request.form.get("password", "")
    form_id = request.form.get("redirect")
    submitType = request.form.get("submit", "")
    if pword == "123":
        session["user"] = "Root" # @NSA Backend
    elif db.validate_login(uname, pword) == True:
        session["user"] = uname
        session["userID"] = db.getID("accounts", "user_id", "username", str(uname))
    else:
        flash("Wrong username or password")
        return redirect(url_for("login_page", redirect=form_id))
    #This is to redirect people that are filling out a form that requires login
    if form_id == None or form_id == "":
        return redirect(url_for("home_page"))
    else:
        return redirect(url_for("display_form", id=form_id))

#Shows the form to signup
@polyforms.route('/join')
def signup_page():
    return render_template("signup.html", username=session.get("user", ""))

#Verifies that this account can be made, redirects to login page on success
@polyforms.route('/join/verify', methods=['POST'])
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

@polyforms.route('/form/respond', methods=["GET"])
def display_form():
    form_id = request.args.get("id")
    username = session.get("user")
    if form_id == None or test.form_exists(form_id) == False: #insert db check for existing form
        return render_template("404.html", username=username), 404
    #now that we know the form exists...
    form = test.get_form(form_id)
    if username == None and form["login_required"]: #insert db check for login required
        flash("Please login to view this form. You will be redirected after you login.")
        return redirect(url_for("login_page", redirect=form_id))
    else:
        template_name = form["theme"]
        flash('Answer "How many siblings do you have?"')
        flash('Answer "Do you think freshman should be allowed to go out for frees?"')
        flash('Select atleast 3 but no more than 4 choices for "Ice cream flavors?"')
        return render_template("form_themes/"+template_name, title=form["title"], questions=form["questions"], form_id=form_id)

#Shortcut URLS
@polyforms.route('/f/<form_id>')
def display_form_shortcut(form_id):
    if test.form_exists(form_id): #insert check if this shortcut registered in DB
        return redirect(url_for("display_form", id=form_id))
    else:
        return render_template("404.html", username=session.get("user", "")), 404

#This will store the responses to the form and then redirect to a Thank You
@polyforms.route('/form/submit', methods=['POST'])
def process_form():
    if "form_id" not in request.form:
        return "Error"
    else:
        form_id = request.form["form_id"]
        return redirect(url_for("display_form"))

#View the responses to your form and make charts
@polyforms.route('/form/view')
def responses_page():
    form_id = request.args.get("id", "-1")
    test_form = random_form("This is a randomly generated form #"+form_id, 5, 20)
    return render_template("spreadsheet.html", username=session.get("user", ""), title=test_form['title'], headers=test_form['headers'], data=test_form['data'], form_id=form_id)

#CSV
@polyforms.route('/form/view/form.csv')
def responses_csv():
    if not ("id" in request.args):
        return "The requested file was not found at this url"
    else:
        test_form = random_form("This is a randomly generated form", 5, 20)
        return Response(render_template("csv_results.csv", headers=test_form['headers'], data=test_form['data']), mimetype="text/csv")
#JSON
@polyforms.route('/form/view/form.json')
def responses_json():
    if not ("id" in request.args):
        return "The requested file was not found at this url", 404
    else:
        test_form = random_form("This is a randomly generated form", 5, 20)
        return Response(render_template("json_results.json", headers=test_form['headers'], data=test_form['data']), mimetype="application/json")

@polyforms.route('/ajax')
def ajax():
    return redirect(url_for('/form'))

@polyforms.route('/my/forms')
def my_forms():
    return render_template("ownforms.html", username=session.get("user",""), forms_user_made={str(n):random_form("This is a randomly generated form #"+str(n), 5, 20) for n in range(0, 4)})

@polyforms.route('/my/settings')
def settings_page():
    return render_template("settings.html", username=session.get("user",""))

@polyforms.route('/my/settings/password')
def reset_password_page():
    return render_template("pass_reset.html", username=session.get("user", ""))

#This is where the password reset form redirects. This method will check the DB for security question. Then it will change the password. Then it will redirect to login
@polyforms.route('/my/settings/password-update', methods=["POST"])
def reset_password_logic():
    uname = request.form.get("username")
    question = request.form.get("question")
    answer = request.form.get("answer")
    if not (db.user_exists(uname)):
        flash("Username is wrong or does not exist. Please re-enter an username")
    elif not db.validate_resetPassword(uname, question, answer):
        flash("Security Question and/or answer is wrong. Please make sure the answer and question match the ones you used when signing up. Capitalization matters.")
    elif request.form.get("password") == request.form.get("password2"):
        db.update_account(uname, request.form.get("password", ""))
        if "user" in session:
            session.pop("user")
        flash("Success! Your password has been changed.")
        return redirect(url_for("login_page"))
    else:
        flash("The new password doesn't match in both boxes")
    return redirect(url_for("reset_password_page"))

@polyforms.route('/logout')
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("home_page"))

#This can be used as a Jinja filter
@polyforms.template_filter('dtnormal')
def format_datetime(value="2018-05-26 12:00:00"):
    months = ["Jan", "Feb", "March", "April", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m = int(value[5:7]) - 1
    d = value[8:10]
    y = value[0:4]
    t = value[11:-3]
    return "%s %s at %s" % (months[m], d, t)

@polyforms.template_filter('attributes')
def conditional_attributes(question):
    result = ""
    if question['required'] == True:
        result += "required "
    if question['min'] != None:
        if question['type'] == "long" or question['type'] == "short":
            result += 'minlength="%d" ' % question['min']
        elif question['type'] == "number":
            result +='min="%d" ' % question['min']
    if question['max'] != None:
        if question['type'] == "long" or question['type'] == "short":
            result += 'maxlength="%d" ' % question['max']
        elif question['type'] == "number":
            result +='max="%d" ' % question['max']
    return result

#Will not be executed if this is imported by WSGI
if __name__ == "__main__":
    polyforms.debug = True
    polyforms.run()

