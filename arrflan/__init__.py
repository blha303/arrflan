#!/usr/bin/env python3
from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_openid import OpenID
from requests import get, post
import re

flask_app = Flask(__name__)
flask_app.config.from_pyfile('../settings.cfg')
flask_app.secret_key = flask_app.config["SECRET_KEY"]
oid = OpenID(flask_app)

from arrflan.models import User
from arrflan.database import db_session, init_db

init_db()

# Steam
def get_steam_userinfo(steam_id):
    options = {
        'key': flask_app.config['STEAM_API_KEY'],
        'steamids': steam_id
    }
    rv = get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0001/', params=options).json()
    return rv['response']['players']['player'][0] or {}


# Flask routes
@flask_app.route("/")
def index():
    return render_template("index.html", user=g.user)

@flask_app.route("/login")
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    return oid.try_login('http://steamcommunity.com/openid')

@flask_app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(oid.get_next_url())


# Pre/post functions
@oid.after_login
def create_or_login(resp):
    _steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')
    match = _steam_id_re.search(resp.identity_url)
    g.user = User.query.filter_by(steam_id=match.group(1)).first()
    if not g.user:
        steamdata = get_steam_userinfo(match.group(1))
        g.user = User(match.group(1))
        g.user.nickname = steamdata['personaname']
        g.user.country = steamdata['loccountrycode']
        g.user.state = steamdata['locstatecode']
        g.user.url = shorten_url(steamdata['profileurl'])
        g.user.realname = steamdata['realname']
        g.user.avatar = shorten_url(steamdata['avatarmedium'])
    db_session.commit()
    session['user_id'] = g.user.id
    flash('You are logged in as %s' % g.user.nickname)
    return redirect(oid.get_next_url())

@flask_app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@flask_app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


# Utility functions
def shorten_url(url):
    response = post("http://rf.ln/create", data={"url": url}).json()
    return "http://rf.ln/" + str(response["result"]["id"])
