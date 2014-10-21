from flask import request, render_template, jsonify
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
    dev = Developer()
    if Developer.query.count() > 0:
        dev = Developer.query.get(1)
    return render_template('public/public.html', dev=dev)

@app.route('/sign-in/', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    return render_template('public/sign_in.html', form=form)

@app.route('/app/', methods=['GET'])
def dashboard():
    follower_counts = Follower.query.order_by( \
        Follower.timestamped.desc()).all()
    return render_template('app/dashboard.html')


@app.route('/refresh/github/', methods=['GET'])
def refresh_github():
    github_follower_count.apply_async(args=['makaimc'])
    return 'ok'


