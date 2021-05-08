import json
import sqlite3

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/<int:post_id>/detail', methods=('GET', 'POST'))
@login_required
def detail(post_id):
    # 작가명,글 제목, 본문, 좋아요 수 -> 좋아요 클릭여부 -> 태그들 -> 댓글들
    post = get_db().execute(
        'SELECT p.id, p.author_id, username, title, body, likes'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (post_id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    liked = get_db().execute(
        'SELECT COUNT(*) '
        '  FROM like WHERE post_id = ? AND user_id = ?',
        (post_id, g.user['id'])
    ).fetchone()

    tags = get_db().execute(
        'SELECT body'
        ' FROM tag WHERE post_id = ?',
        (post_id,)
    ).fetchall()

    comments = get_db().execute(
        'SELECT c.id, u.username, c.body'
        ' FROM comment c JOIN user u ON c.user_id = u.id'
        ' WHERE c.post_id = ?',
        (post_id,)
    ).fetchall()

    return render_template('blog/detail.html', post=post, liked=liked, tags=tags, comments=comments)


@bp.route('/like', methods=('GET', 'POST'))
@login_required
def like():
    post_id = request.form['post_id']

    liked = get_db().execute(
        'SELECT COUNT(*) '
        '  FROM like WHERE post_id = ? AND user_id = ?',
        (post_id, g.user['id'])
    ).fetchone()

    if liked[0] == 0:
        get_db().execute(
            'INSERT INTO like (post_id, user_id) VALUES(?, ?)',
            (post_id, g.user['id'])
        )
        get_db().commit()

    else:
        get_db().execute(
            'DELETE FROM like WHERE post_id = ? AND user_id = ?',
            (post_id, g.user['id'])
        )
        get_db().commit()

    likes = get_db().execute(
        'SELECT likes FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (post_id,)
    ).fetchone()
    return str(likes[0])


@bp.route('/create_comment', methods=('GET', 'POST'))
@login_required
def create_comment():
    post_id = request.form['post_id']
    body = request.form['body']

    # 댓글 입력
    get_db().execute(
        'INSERT INTO comment (post_id, user_id, body) VALUES(?, ?, ?)',
        (post_id, g.user['id'], body)
    )
    get_db().commit()

    # 댓글 불러오기
    comments = get_db().execute(
        'SELECT c.id, u.username, c.body'
        ' FROM comment c JOIN user u ON c.user_id = u.id'
        ' WHERE c.post_id = ?',
        (post_id,)
    ).fetchall()

    commentDict = {"comment": []}
    for i in range(len(comments)):
        commentDict["comment"].append(
            {
                "number": comments[i]["id"],
                "username": comments[i]["username"],
                "body": comments[i]["body"]
            })

    return commentDict


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """
    로그인한 사용자가 글을 작성할 때 사용되는 함수입니다.
    1. 로그인을 검증하기 위해 login_required 데코레이터를 사용했습니다.(auth.py)
    2. 글을 제출할 때 제목(title)을 달지 않았으면, flash로 오류를 알립니다.
      - 글 작성하기 페이지로 다시 이동합니다.
    3. 정상적으로 글이 작성됐다면, 메인 페이지로 이동합니다.
    """

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
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

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
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
