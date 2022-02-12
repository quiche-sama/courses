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
        'SELECT c.id, title, body, created, owner_id, username'
        ' FROM clist c JOIN user u ON c.owner_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('c_list/index.html', listes_de_courses=listes_de_courses)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
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
                ' VALUES(?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('c_list.index'))
    return render_template('c_list/create.html')


def get_c_list(id, check_owner=False):
    c_list = get_db().execute(
        'SELECT c.id, title, body, created, owner_id, username'
        ' FROM clist c JOIN user u ON c.owner_id = u.id'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if c_list is None:
        abort(404, f"La liste id {id} doesn't exist.")

    if check_owner and c_list['owner_id'] != g.user['id']:
        abort(403)

    return c_list


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    c_list = get_c_list(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE clist SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('c_list.index'))

    return render_template('c_list/update.html', c_list=c_list)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_c_list(id)
    db = get_db()
    db.execute('DELETE FROM clist WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('c_list.index'))


