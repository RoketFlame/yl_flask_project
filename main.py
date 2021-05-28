import json
import os
import copy

import waitress
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from data import db_session
from flask import Flask, render_template, redirect, request, url_for, flash, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource

from data.news import News
from data.users import User
from data.communities import Community
from data.comments import Comment

from forms.community import CommunityForm
from forms.news import NewsForm, Commenting
from forms.user import RegisterForm, LoginForm, EditForm

import api_news
from resources import news_resources
from functions import get_fps

db_session.global_init("db/blogs.db")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    params = {}
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    params['news'] = news
    params['title'] = 'Записи в блоге'
    return render_template("index.html", **params)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('my_profile'))
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(request.args.get("next") or url_for("my_profile"))
        flash("Неправильный логин или пароль")
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data == form.password_again.data:
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                flash("Такой пользователь уже есть")
            else:
                user = User(
                    name=form.name.data,
                    email=form.email.data,
                    about=form.about.data
                )
                user.avatar = open('static/images/default_avatar.png', 'rb').read()
                user.set_password(form.password.data)
                db_sess.add(user)
                db_sess.commit()
                return redirect('/login')
        else:
            flash('Пароли не совпадают')

    return render_template('register.html', title='Регистрация', form=form)


@app.route("/news")
def news():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("news.html", news=news, title='Записи в блоге')


@app.route('/news/create', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        f = form.picture.data
        if f:
            news.picture = f.read()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(url_for('news'))
    return render_template('create_news.html', title='Добавление новости',
                           form=form)


@app.route('/news/id<int:id>', methods=['GET', 'POST'])
@login_required
def one_news(id):
    form = Commenting()
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    commets = news.comments
    if request.method == 'POST':
        comment = Comment()
        comment.user = db_sess.query(User).filter(User.id == current_user.id).first()
        comment.news = news
        comment.content = form.content.data
        news.comments.append(comment)
        db_sess.commit()
        return redirect(url_for('one_news', id=id))
    return render_template('one_news.html', news=news, title=news.title, form=form, comments=commets)


@app.route('/news/edit/id<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id).first()
        if news.is_published_by_community:
            author = news.community.creator
        else:
            author = news.user
        if author == current_user and news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id).first()
        if news.user == current_user or news.community.creator == current_user and news:
            f = form.picture.data
            if f:
                news.picture = f.read()
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect(url_for('news', id=id))
        else:
            abort(404)
    return render_template('create_news.html', title='Редактирование новости', form=form)


@app.route('/news/delete/id<int:id>', methods=['GET', 'POST'])
@login_required
def delete_news(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if news.is_published_by_community:
        author = news.community.creator
    else:
        author = news.user
    news = db_sess.query(News).filter(current_user == author).filter(News.id == id).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect(url_for('news'))


@app.route('/communities')
def communities():
    db_sess = db_session.create_session()
    coms = db_sess.query(Community).all()
    return render_template('communities.html', coms=coms, title='Сообщества')


@app.route('/community/id<int:id>')
@login_required
def community(id):
    db_sess = db_session.create_session()
    com = db_sess.query(Community).filter(Community.id == id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    subscribe_to_community = com.id in [c.id for c in user.subscribes_to_community]
    _len = len([user for user in com.subscribers])
    return render_template('community.html', com=com,
                           subscribe_to_community=subscribe_to_community, len=_len)


@app.route('/community/id<int:id>/news/create', methods=['GET', 'POST'])
def create_news_by_community(id):
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.is_published_by_community = True
        com = db_sess.query(Community).filter(Community.id == id).first()
        news.community_id = id
        com.news.append(news)
        db_sess.merge(com)
        db_sess.commit()
        return redirect(url_for('community', id=id))
    return render_template('create_news.html', title='Добавление новости',
                           form=form)


@app.route('/community/create', methods=['GET', 'POST'])
@login_required
def create_community():
    form = CommunityForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        com = Community()
        f = form.picture.data
        if f:
            com.avatar = f.read()
        com.name = form.name.data
        com.description = form.description.data
        com.creator = current_user
        current_user.communities.append(com)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(url_for('my_communities'))
    return render_template('create_community.html', title='Добавление сообщества',
                           form=form)


@app.route('/community/edit/id<int:id>', methods=['GET', 'POST'])
@login_required
def edit_community(id):
    form = CommunityForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        com = db_sess.query(Community).filter(Community.id == id,
                                              Community.creator == current_user
                                              ).first()
        if com:
            form.name.data = com.name
            form.description.data = com.description
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        com = db_sess.query(Community).filter(Community.id == id,
                                              Community.creator == current_user
                                              ).first()
        if com:
            f = form.picture.data
            if f:
                com.avatar = f.read()
            com.name = form.name.data
            com.description = form.description.data
            db_sess.commit()
            return redirect(url_for('community', id=id))
        else:
            abort(404)
    return render_template('create_community.html', title='Редактирование сообщества', form=form)


@app.route('/community/delete/id<int:id>', methods=['GET', 'POST'])
@login_required
def delete_community(id):
    db_sess = db_session.create_session()
    com = db_sess.query(Community).filter(Community.id == id,
                                          Community.creator == current_user
                                          ).first()
    if com:
        db_sess.delete(com)
        db_sess.commit()
    else:
        abort(404)
    return redirect(url_for('communities'))


@app.route('/news/my')
@login_required
def my_news():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.user == current_user)
    return render_template("news.html", news=news, title='Мои статьи')


@app.route('/communities/my')
@login_required
def my_communities():
    db_sess = db_session.create_session()
    coms = db_sess.query(Community).filter(Community.creator == current_user)
    return render_template("communities.html", coms=coms, title='Мои сообщества')


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditForm()
    if request.method == "GET":
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.about.data = current_user.about
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data) or form.new_password.data == '':
            db_sess = db_session.create_session()
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
            f = form.avatar.data
            if f:
                current_user.avatar = f.read()
            current_user.name = form.name.data
            current_user.email = form.email.data
            current_user.about = form.about.data
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect(url_for('my_profile'))
        flash('Неправильный пароль')
        return render_template('edit_profile.html', title='Редактирование профиля', form=form)
    return render_template('edit_profile.html', title='Редактирование профиля', form=form)


@app.route('/profile')
@login_required
def my_profile():
    user = current_user
    news = user.news
    coms = user.communities
    return render_template('profile.html', news=news, coms=coms, user=user)


@app.route('/profile/id<int:id>')
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    db_sess.commit()
    news = user.news
    coms = user.communities
    if current_user.is_authenticated:
        subscribe_yet = user in current_user.subscribes_to_user
    else:
        subscribe_yet = False
    return render_template('profile.html', news=news, coms=coms, user=user,
                           subscribe_yet=subscribe_yet)


@app.route('/user_avatar/id<int:id>')
def user_avatar(id):
    db_sess = db_session.create_session()
    img = db_sess.query(User).filter(User.id == id).first().avatar
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/news_picture/id<int:id>')
def news_picture(id):
    db_sess = db_session.create_session()
    img = db_sess.query(News).filter(News.id == id).first().picture
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/community/subscribe/id<int:id>', methods=['GET', 'POST'])
@login_required
def subscribe_to_community(id):
    db_sess = db_session.create_session()
    com = db_sess.query(Community).filter(Community.id == id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    com.subscribers.append(user)
    db_sess.commit()
    flash('Вы успешно подписались')
    return redirect(url_for('community', id=id))


@app.route('/community/unsubscribe/id<int:id>')
@login_required
def unsubscribe_to_community(id):
    db_sess = db_session.create_session()
    com = db_sess.query(Community).filter(Community.id == id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    com.subscribers.remove(user)
    db_sess.commit()
    flash('Вы успешно отписались')
    return redirect(url_for('community', id=id))


@app.route('/profile/subscribe/id<int:id>')
@login_required
def subscribe_to_user(id):
    if id not in [user.id for user in current_user.subscribes_to_user]:
        db_sess = db_session.create_session()
        user_to = db_sess.query(User).filter(User.id == id).first()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        db_sess.delete(user)
        user_to.subscribers.append(user)
        db_sess.add(user)
        db_sess.commit()
        flash('Вы успешно подписались')
    else:
        flash('Вы уже подписаны')
    return redirect(url_for('profile', id=id))


@app.route('/profile/unsubscribe/id<int:id>')
@login_required
def unsubscribe_to_user(id):
    try:
        db_sess = db_session.create_session()
        user_to = db_sess.query(User).filter(User.id == id).first()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.subscribes_to_user.remove(user_to)
        db_sess.add(user_to)
        db_sess.commit()
        flash('Вы успешно отписались')
    except:
        flash('Вы не были подписаны на этого пользователя')
    return redirect(url_for('profile', id=id))


@app.route('/community/id<int:id>/avatar')
def communities_avatar(id):
    db_sess = db_session.create_session()
    img = db_sess.query(Community).filter(Community.id == id).first().avatar
    if not img:
        img = open('static/images/default_avatar.png', 'rb').read()
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/search')
def search():
    value = request.args.get("text")
    db_sess = db_session.create_session()
    coms = db_sess.query(Community).filter(
        (Community.name.like(f"%{value}%")) | (Community.description.like(f"%{value}%"))).all()
    users = db_sess.query(User).filter(
        (User.name.like(f"%{value}%")) | (User.about.like(f"%{value}%"))).all()
    news = db_sess.query(News).filter(
        (News.title.like(f"%{value}%")) | (News.content.like(f"%{value}%"))).all()
    return render_template('search.html', coms=coms, users=users, news=news, title='Поиск',
                           value=value)


@app.route('/users')
@login_required
def users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template('users.html', users=users)


@app.route('/subscribes')
@login_required
def subscribes():
    coms = current_user.subscribes_to_community
    users = current_user.subscribes_to_user
    return render_template('subscribes.html', coms=coms, users=users)


@app.route('/computer_calculator', methods=['GET', 'POST'])
@login_required
def computer_calculator():
    fps = None
    with open('static/computer.json') as js_file:
        data = json.load(js_file)
    if request.method == 'GET':
        return render_template('calculator.html', js_f=data)
    if request.method == 'POST':
        gpu = request.form.get('gpu')
        cpu = request.form.get('cpu')
        ram = request.form.get('ram')
        game = request.form.get('game')
        fps = get_fps(gpu, cpu, ram, game)
        return render_template('calculator.html', js_f=data, fps=fps)


if __name__ == '__main__':
    api.add_resource(news_resources.NewsListResource, '/api/news')
    api.add_resource(news_resources.NewsResource, '/api/news/<int:news_id>')
    app.register_blueprint(api_news.blueprint)
    app.run(port=8000, host='127.0.0.1')
    # port = int(os.environ.get("PORT", 5000))
    # waitress.serve(app, host='0.0.0.0', port=port)
