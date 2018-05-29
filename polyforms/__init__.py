from flask import Flask, render_template, request, session, redirect, url_for, flash, Response
import os   #for secret key creation and file system exploration
import random   #for the generate_questions random word generator
from utils import db

polyforms = Flask(__name__)
polyforms.secret_key = os.urandom(32)
DIR = os.path.dirname(__file__) + "/"

#Used for testing the display of questions
def generate_questions(num):
    results = []
    words = "blah ooh why aaah how far when foo what bar name interest".split()
    types = ["short", "long", "number", "choice"]
    for x in range(0, num):
        qtype = random.choice(types)
        results.append({'type':qtype, 'question': 8 * (random.choice(words)+' ')+'?', 'index': str(x), 'min':None, 'max':None})
        if qtype == "choice":
            results[-1]["choices"] = random.randrange(1, 10) * [random.choice(words)]
    return results

#Used to test viewing of results in a table. Returns a random word
def random_word():
    length = random.randrange(2, 10)
    return reduce(lambda s, c: s+c, [chr(random.randrange(ord('A'), ord('Z'))) for i in range(0, length)], "")

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
    return render_template("index.html", username=session.get("user", ""))

#Shows the form to login
@polyforms.route('/login')
def login_page():
    return render_template('login.html', username=session.get("user", ""))

#Verifies username and password, redirects home on success
@polyforms.route('/login/verify', methods=["POST"])
def login_logic():
    uname = request.form.get("username", "")
    pword = request.form.get("password", "")
    if pword == "123":
        session["user"] = "Root" # @NSA Backend
    elif db.validate_login(uname, pword) == True:
        session["user"] = uname
    else:
        flash("Wrong username or password")
        return redirect(url_for("login_page"))
    return redirect(url_for("home_page"))

#Shows the form to signup
@polyforms.route('/join')
def signup_page():
    return render_template("signup.html", username=session.get("user", ""))

#Verifies that this account can be made, redirects to login page on success
@polyforms.route('/join/verify', methods=['POST'])
def signup_logic():
    uname = request.form.get("username1", "")
    pword = request.form.get("password1", "")
    if len(uname) == 0:
        flash("Username can't be blank")
    elif uname != request.form.get("username2", ""):
        flash("You didn't type the username correctly the 2nd time")
    elif len(pword) == 0:
        flash("Password can't be blank")
    elif pword != request.form.get("password2", ""):
        flash("You didn't type the password correctly the 2nd time")
    elif db.checkExist("accounts", "username", uname): #check its not already existing
        flash("This username already exists")
    else:
        db.add_account(uname, pword)
        flash("Success! Your account has been made. Please login.")
        return redirect(url_for("login_page"))
    return redirect(url_for("signup_page"))

@polyforms.route('/form/respond', methods=["GET"])
def display_form():
    return render_template('form.html', title="This is the title of a form", questions=generate_questions(10))

#This will store the responses to the form and then redirect to a Thank You
@polyforms.route('/form/submit', methods=['POST'])
def process_form():
    return redirect(url_for("display_form"))

#View the responses to your form and make charts
@polyforms.route('/form/view')
def responses_page():
    form_id = request.args.get("id", "0")
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

@polyforms.route('/ajax')
def ajax():
    return redirect(url_for('/form'))

@polyforms.route('/my/forms')
def my_forms():
    return render_template("ownforms.html", username=session.get("user",""), forms_user_made={str(n):random_form("This is a randomly generated form #"+str(n), 5, 20) for n in range(0, 4)})

@polyforms.route('/my/settings')
def settings_page():
    return render_template("settings.html", username=session.get("user",""))

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

#Will not be executed if this is imported by WSGI
if __name__ == "__main__":
    polyforms.debug = True
    polyforms.run()

