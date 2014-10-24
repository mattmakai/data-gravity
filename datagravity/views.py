from flask import request, render_template, jsonify, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required, \
                            current_user

from . import app, db, login_manager, redis_db, socketio
from .forms import LoginForm
from .models import User, Developer, Follower, Service
from .tasks import github_follower_count


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


@app.route('/refresh/github/', methods=['GET'])
def refresh_github():
    # github_follower_count.apply_async(args=['makaimc'])
    github_follower_count('makaimc')
    return redirect(url_for('main'))


