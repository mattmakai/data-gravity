from flask import request, render_template, jsonify, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required, \
                            current_user
from requests_oauthlib import OAuth2Session

from . import app, db, login_manager, redis_db, socketio
from .forms import LoginForm
from .models import User, Developer, Follower, Service
from .tasks import github_follower_count
from .config import GOOGLE_CLIENT_SID, GOOGLE_CLIENT_SECRET, \
                    GOOGLE_REDIRECT_URL


@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/', methods=['GET'])
def public_view():
    return redirect(url_for('sign_in'))


@app.route('/sign-in/', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main'))
    return render_template('public/sign_in.html', form=form)


@app.route('/app/', methods=['GET'])
def main():
    gh = Service.query.filter_by(name='GitHub').first()
    gh_followers = Follower.query.filter_by(service=gh.id).order_by( \
        Follower.timestamped.desc()).first()
    return render_template('app/main.html', github_followers=gh_followers)


authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

google = OAuth2Session(GOOGLE_CLIENT_SID, scope=scope,
    redirect_uri=GOOGLE_REDIRECT_URL)
authorization_url, state = google.authorization_url(authorization_base_url,
    access_type="offline", approval_prompt="force")

@app.route('/app/authorize-apis/', methods=['GET'])
def authorize_apis():
    return render_template('app/authorize.html', google_url=authorization_url)

@app.route('/oauth2callback', methods=['GET'])
def oauth2callback_google():
    google.fetch_token(token_url, client_secret=GOOGLE_CLIENT_SECRET,
        authorization_response=request.url)
    r = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
    return str(r.content)


@app.route('/refresh/github/', methods=['GET'])
def refresh_github():
    # github_follower_count.apply_async(args=['makaimc'])
    github_follower_count('makaimc')
    return redirect(url_for('main'))


