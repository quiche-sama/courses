from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from courses_app.auth import login_required
from courses_app.db import get_db

bp = Blueprint('c_list', __name__)

@bp.route('/')
def index():
    db = get_db()
    listes_de_courses = db.execute(
        'SELECT c.id, title, body, created, owner_id'
        ' FROM clist c JOIN user u ON c.owner_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('c_list/index.html', listes_de_courses=listes_de_courses)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method =='POST':
        title = request.form['title']
        body = request.form['body']
        error = None
    if not title:
        error = 'Title required'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO clist (title, body, owner_id)'
            ' VALUES(?, ?, ?',
            (title, body, g.user['id'])
        )
        db.commit()
        return redirect(url_for('blog.index'))
    return render_template('c_list/create.html')