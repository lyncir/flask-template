# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, g, abort
from flask.ext.login import login_user, logout_user, current_user

from app import app, permision, User, bcrypt
from app.forms.users import LoginForm, AddUserForm, ChangedPasswordForm


#@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.get_user()
        login_user(User(user))
        return form.redirect('index')
    return render_template('login.html', form=form)


#@app.route('/logout')
@permision
def logout():
    logout_user()
    return redirect(url_for('login'))


#@app.route('/user/add')
@permision
def adduser():
    form = AddUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        g.mysql_db.execute('INSERT INTO users(username, password) \
                VALUE(%s, %s)', username, bcrypt.generate_password_hash(password))
        return redirect(url_for('index'))
    return render_template('adduser.html', form=form)


#@app.route('/user/<username>/profile')
@permision
def profile(username):
    form = ChangedPasswordForm()
    if form.validate_on_submit():
        user_name = form.username.data
        if username != user_name:
            abort(404)
        new_password = form.new_password.data
        g.mysql_db.execute('UPDATE users SET password=%s WHERE username=%s',
                bcrypt.generate_password_hash(new_password), user_name)
        return redirect(url_for('index'))
    return render_template('profile.html', form=form, current_user=current_user)
