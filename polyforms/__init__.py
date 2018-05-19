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
    if pword == "123": #replace with database check
        session["user"] = uname
    else:
        flash("Wrong")
    return redirect(url_for("home_page"))

#Shows the form to signup
@polyforms.route('/join')
def signup_page():
    return "Go back this page doesnt exist yet"

#Verifies that this account can be made, redirects to login page on success
@polyforms.route('/join/verify', methods=['POST'])
def signup_logic():
    #insert logic to check that this account is valid
    return redirect(url_for("home_page"))

@polyforms.route('/form/respond', methods=["GET"])
def display_form():
    return render_template('form.html')

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

