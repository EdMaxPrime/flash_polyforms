from flask import Flask, render_template, request, session, redirect, url_for, flash
import os

polyforms = Flask(__name__)
DIR = os.path.dirname(__file__) + "/"

@polyforms.route('/')
def root():
    print "=====================================\nConsole Message\n"
    print DIR + "\n====================================="
    body = "<h2> Deployment Test </h2>"
    body+= "DIR: " + DIR + "<br>"
    body+= '<img src="' + url_for('static', filename='img/cat_cage.jpg') + '" width="500"</img>'
    return body

@polyforms.route('/login')
def login_page():
    return render_template('login.html')

@polyforms.route('/login/verify', methods=["POST"])
def login_logic():
    uname = request.form.get("username", "")
    pword = request.form.get("password", "")
    if pword == "123": #replace with database check
        session["user"] = uname
    else:
        flash("Wrong")
    return redirect(url_for("/"))

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

#Will not be executed if this is imported by WSGI
if __name__ == "__main__":
    app.debug = True
    app.run()

