import json

from werkzeug.exceptions import abort

from data import db_session
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.news import News
from data.users import User
from data.communities import Community

from forms.community import CommunityForm
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm, EditForm

db_session.global_init("db/blogs.db")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, title='Записи в блоге')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
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
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('create_news.html', title='Добавление новости',
                           form=form)


@app.route('/news/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('create_news.html', title='Редактирование новости', form=form)


@app.route('/news/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if news.is_published_by_community:
        author = db_sess.query(News).filter(News.id == id).first().community.creator
    else:
        author = None
    news = db_sess.query(News).filter((News.user == current_user) |
                                      (author == current_user)).filter(News.id == id).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/communities')
def communities():
    db_sess = db_session.create_session()
    coms = db_sess.query(Community)
    return render_template('communities.html', coms=coms, title='Сообщества')


@app.route('/community/<int:id>')
def community_(id):
    db_sess = db_session.create_session()
    com = db_sess.query(Community).filter(Community.id == id).first()
    news = db_sess.query(News).filter(News.community_id == com.id)
    return render_template('community.html', com=com, title=com.name, news=news)


@app.route('/community/<int:id>/news/create', methods=['GET', 'POST'])
def create_news_by_community(id):
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        com = db_sess.query(Community).filter(Community.id == id).first()
        com.news.append(news)
        db_sess.merge(com)
        db_sess.commit()
        return redirect(f'/../../community/{id}')
    return render_template('create_news.html', title='Добавление новости',
                           form=form)


@app.route('/community/create', methods=['GET', 'POST'])
@login_required
def create_community():
    form = CommunityForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        com = Community()
        com.name = form.name.data
        com.description = form.description.data
        com.creator = current_user
        current_user.communities.append(com)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('create_community.html', title='Добавление сообщества',
                           form=form)


@app.route('/community/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_community(id):
    form = CommunityForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        coms = db_sess.query(Community).filter(Community.id == id,
                                               Community.creator == current_user
                                               ).first()
        if coms:
            form.name.data = coms.name
            form.description.data = coms.description
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        coms = db_sess.query(Community).filter(Community.id == id,
                                               Community.creator == current_user
                                               ).first()
        if news:
            coms.name = form.name.data
            coms.description = form.description.data
            db_sess.commit()
            return redirect('/communities')
        else:
            abort(404)
    return render_template('create_community.html', title='Редактирование сообщества', form=form)


@app.route('/community/delete/<int:id>', methods=['GET', 'POST'])
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
    return redirect('/communities')


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
            current_user.name = form.name.data
            current_user.email = form.email.data
            current_user.about = form.about.data
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template('edit_profile.html', title='Редактирование профиля', form=form,
                               message="Неправильный пароль")
    return render_template('edit_profile.html', title='Редактирование профиля', form=form)


if __name__ == '__main__':
    db_sess = db_session.create_session()
    db_sess.commit()
    app.run(port=8080, host='127.0.0.1')
