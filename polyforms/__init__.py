from flask import Flask, render_template, request, session, redirect, url_for, flash
import os

polyforms = Flask(__name__)
polyforms.secret_key = os.urandom(32)
DIR = os.path.dirname(__file__) + "/"

@polyforms.route('/')
def root():
    print "=====================================\nConsole Message\n"
    print DIR + "\n====================================="
    body = "<h2> Deployment Test </h2>"
    body+= "DIR: " + DIR + "<br>"
    body+= '<img src="' + url_for('static', filename='img/cat_cage.jpg') + '" width="500"</img>'
    return body

#This will become the root "/" page but not right now because of the deploytest stuff
@polyforms.route('/home')
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
    if pword == "123" and uname != "": #replace with database check
        session["user"] = uname
    else:
        flash("Wrong")
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
    elif uname == "taken": #check its not already existing
        flash("This username already exists")
    else:
        #insert into database, then...
        flash("Success! Your account has been made. Please login.")
        return redirect(url_for("login_page"))
    return redirect(url_for("signup_page"))

@polyforms.route('/form/respond', methods=["GET"])
def display_form():
    q = {'type':"short", 'index':"0", 'question':"Name"}
    return render_template('form.html', title="test", questions=[q])

@polyforms.route('/ajax')
def ajax():
    return redirect(url_for('/form'))

@polyforms.route('/my/forms')
def my_forms():
    return ""

@polyforms.route('/my/settings')
def settings_page():
    return ""

@polyforms.route('/logout')
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("home_page"))

#Will not be executed if this is imported by WSGI
if __name__ == "__main__":
    polyforms.debug = True
    polyforms.run()

