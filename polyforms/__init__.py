from flask import Flask, render_template, request, session, redirect, url_for, flash

polyforms = Flask(__name__)

@polyforms.route('/')


@polyforms.route('/login')
    return render_template('login.html')

@polyforms.route('/form')
    return render_template('form.html')

@polyforms.route('/ajax')
    return redirect(url_for('/form', ))

@polyforms.route('/my/forms')


@polyforms.route('/my/settings')
    

