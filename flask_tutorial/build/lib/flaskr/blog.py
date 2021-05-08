from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import click
from flaskr.auth import login_required
from flaskr.db import get_db

'''
 Blueprint 함수에 prefix 인자를 넣지 않았습니다.
 따라서 prefix는 None이 됩니다.
'''
bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    """
    메인(index) 페이지를 나타냅니다.
    해당 페이지에서 DB에서 모든 사용자가 작성한 글을 보여줍니다.
    글에는 '글 번호 / 글 제목 / 글 내용 / 작성시각 / 작성자 id / 작성자 닉네임'이 포함됩니다.
    """

    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    # render_template의 두번 째 인자는 **context입니다.
    # jinja2에 전달할 변수명을 짓고, 해당 변수에 데이터를 저장합니다. (변수명: posts)
    # jinja2에서는 {{ posts }}와 같이 해당 변수명을 입력하여 읽어낼 수 있습니다.
    return render_template('blog/index.html', posts=posts)


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
    """
    글의 작성자가 글 수정 또는 삭제 버튼을 눌렀을 때, 유효성을 식별하기 위해 사용되는 코드입니다.

    이 함수에서는 두 가지를 식별합니다.
    1. 글이 존재하는지?
    2. 로그인한 유저의 id와 글의 작성자가 같은 사람인지?

    만약 유효성 식별에서 적합하지 않다면, 페이지에 오류 메시지를 전달합니다.
    """

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
    """
    1. 로그인을 검증하기 위해 login_required 데코레이터를 사용했습니다.(auth.py)

    2. get_post를 통해 수정이 가능한 글인지에 대한 유효성을 검사합니다.
      - 가능하다면, 글에 대한 정보를 post 변수에 저장합니다.
      - 가능하지 않다면, get_post 함수 내부의 abort를 통해 사용자 페이지에 오류가 전달됩니다.

    3. 글 제목이 존재하지 않으면, 글 수정 페이지로 돌아가서 에러 메시지를 나타냅니다.
      - 수정 요청 때 받은 내용이 request 객체에 남아있습니다.
      또한, request에 담긴 데이터는 ImmutableMultiDict([]) 객체를 통해 저장이 되는데,
      이는 같은 모듈(blog.py)에서라도 다른 함수에서는 초기화되는 성질이 있습니다.

      따라서 update 함수 내에서 update.html을 렌더링하면, "유저가 작성 중이던 글"을 웹 페이지로 전달받을 수 있습니다.
      반면에, 다른 함수에서 html 파일을 렌더링하면 request 객체를 초기화하여 웹 페이지로 전달할 수 있습니다.

    4. 글 제목이 존재한다면, 사용자가 작성한 내용으로 글을 수정합니다.
      - redirect 함수를 통해 index 함수에서 index.html이 렌더링 됩니다.
    """

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
    """
    1. 로그인을 검증하기 위해 login_required 데코레이터를 사용했습니다.(auth.py)
    2. get_post를 통해 삭제가 가능한 글인지에 대한 유효성을 검사합니다.
    - 가능하다면, 글에 대한 정보를 post 변수에 저장합니다.
    - 가능하지 않다면, get_post 함수 내부의 abort를 통해 사용자 페이지에 오류가 전달됩니다.
    3. 해당 글을 삭제하고 메인 페이지로 이동합니다.
    """

    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
