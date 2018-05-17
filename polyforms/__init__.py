from flask import Flask, render_template, request, session, redirect, url_for, flash
import os

polyforms = Flask(__name__)
DIR = os.path.dirname(__file__) + "/"

@polyforms.route('/')
def root():
    return ""

@polyforms.route('/login')
def login_page():
    return render_template('login.html')

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

