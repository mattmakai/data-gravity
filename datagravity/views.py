from flask import request, render_template, jsonify

from . import app, db, redis_db, socketio
from .tasks import github_follower_count
from .models import Follower, Service


@app.route('/', methods=['GET'])
def dashboard():
    follower_counts = Follower.query.order_by( \
        Follower.timestamped.desc()).all()
    return render_template('dashboard.html', follower_counts=follower_counts)


@app.route('/refresh/github/', methods=['GET'])
def refresh_github():
    github_follower_count.apply_async(args=['makaimc'])
    return 'ok'


