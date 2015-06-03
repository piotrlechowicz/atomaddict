#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, json, session, g
from database.session import Get, set_user_tags, get_user_unreaded_articles_as_dict,\
    mark_articles_as_readed, Add, Put
from flask.globals import request
from flask_login import LoginManager, login_user
from database.model.models import User
from forms.forms import SignupForm
from matplotlib.backends.qt_editor import formsubplottool

app = Flask(__name__)
app.secret_key = 'temporarly secret key'
login_manager = LoginManager()


@app.route('/save_tags', methods=['GET', 'POST'])
def save_tags():

    if 'email' not in session:
        return redirect(url_for('sign_in'))
    # get user
    get = Get()
    user = get.user(email=session['email'])
    if not user:
        get.close_session()
        return redirect(url_for('sign_in'))

    tags = []
    for req in request.form:
        tags.append(req)

    # refresh user tags
    set_user_tags(email=user.email, tags=tags)

    get.close_session()
    return redirect(url_for('index'))


@app.route('/article_readed', methods=['GET', 'POST'])
def article_readed():
    article_id = request.form['article_id']

    # delete article from user
    get = Get()
    email = get.all_users()[0].email
    get.close_session()
    mark_articles_as_readed(user_email=email, article_id=article_id)
    return redirect(url_for('index'))


@app.route('/')
def index():
    # TODO If user is logged in render index.html. Ladning page otherwise.

    if 'email' not in session:
        return redirect(url_for('sign_in'))

    # get user
    get = Get()
    user = get.user(email=session['email'])
    if not user:
        get.close_session()
        return redirect(url_for('sign_in'))

    tags_and_articles = get_user_unreaded_articles_as_dict(email=user.email)
    tags = get.user_tags_as_dictionary(email=user.email)
    get.close_session()

    return render_template('index.html',
                           user=user,
                           tags=tags,
                           tags_and_articles=tags_and_articles)


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    # TODO Acutall signing up
    form = SignupForm()

    if request.method == 'POST':
        if form.validate() is False:
            return render_template('signup.html', form=form)
        else:
            put = Put()
            user = put.user(email=form.email.data, password=form.password.data,
                            nickname=form.nickname.data)
            put.close_session()
            session['email'] = user
            return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('signup.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    # TODO Acutall signing in
#     form = LoginForm()
#     if form.validate_on_submit():
#         # login and validate the user
#         login_user
    return render_template('signin.html')


@app.route('/signout')
def sign_out():
    # TODO Acutall signing out
    return redirect(url_for('index'))


@app.route('/settings')
def settings():
    # TODO Save user's settings
    return 'Settings updated'


@app.route('/base')
def base():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(debug=True)
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_email):
    get = Get()
    user = get.user(email=user_email)
    get.close_session()
    return user
    