# -*- coding: utf8 -*-

import os
import urlparse
from flask import Flask, g, render_template, redirect, url_for, session, \
        request
import torndb
from flask.ext.login import LoginManager, UserMixin, login_user, current_user, \
        logout_user, login_required

from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


@app.before_request
def connect_db():
    g.mysql_db = torndb.Connection(host='localhost',
                             user='root',
                             password='',
                             database='flask_test',
                             charset='utf8'
                             )


@app.after_request
def close_connection(response):
    g.mysql_db.close()
    return response


# flask login
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, userdict):
        self.id = userdict.get('id')
        self.username = userdict.get('username')
        self.active = userdict.get('active')

    def is_authenticated(self):
        return True

    def is_active(self):
        if self.active == 1:
            return True
        else:
            return False

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


@login_manager.user_loader
def load_user(userid):
    user = g.mysql_db.get("select * from users where id=%s", userid)
    return User(user)


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    users = """select username,path from (select * from users left join (select user_id,
    user_role.role_id, route_id from user_role inner join role_route on
    user_role.role_id=role_route.role_id) A on users.id=A.user_id) B left join
    routes on B.route_id= routes.id"""
    return render_template('index.html', current_user=current_user)


def next_url(url):
    """
    @param url: http://www.baidu.com/index.html
    @rtype: string
    @return: path
    """
    if url is None:
        return None
    else:
        o = urlparse(url)
        if o.path in ['/login', '/logout']:
            return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.get_user()
        login_user(User(user))
        return form.redirect('index')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/page1')
@login_required
def page1():
    return render_template('page1.html')
