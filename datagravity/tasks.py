import requests
from datetime import datetime, timedelta
from celery.decorators import periodic_task
import sh
from sh import cd, find, wc, cat
from sqlalchemy import and_

from .models import Follower, Service
from datagravity import app, db, celery


@celery.task
def github_follower_count(username):
    """
        Returns the number of GitHub followers for a user name or
        False if there was an issue with the request.
    """
    service = Service.query.filter(Service.name=='GitHub')[0]
    resp = requests.get('https://api.github.com/users/%s' % username)
    # real pretty code here
    td = datetime.today()
    today = datetime(year=td.year, month=td.month, day=td.day)
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    if resp.status_code == requests.codes['OK']:
        try:
            f = Follower.query.filter(and_(Follower.timestamped>yesterday,
                Follower.timestamped<tomorrow)).all()[0]
            f.count = resp.json()['followers']
            db.session.merge(f)
        except Exception as e:
            f = Follower(service, resp.json()['followers'])
            db.session.add(f)
        db.session.commit()
    return resp.status_code


@celery.task
def get_wc(content_dir):
    """
    """
    filetype = "*.markdown"
    cd(content_dir)
    files_list = find(".", "-name", "*.markdown")
    files_arr = files_list.split('\n')
    word_count = 0
    for f in files_arr:
        if f:
            try:
                file_word_count = int(wc(cat(content_dir + f), "-w"))
                word_count += file_word_count
            except:
                pass
    return word_count

