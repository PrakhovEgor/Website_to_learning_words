import datetime
import random
import sqlite3
from itertools import groupby
import os
from flask import (Flask, g, render_template, request, session)
from flask_login import LoginManager, login_required, login_user, logout_user

from werkzeug.utils import redirect

from data import db_session, eng_api
from data.users import User
from forms.user import LoginForm, RegisterForm
from text_to_speech import speech

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def get_port():
  return int(os.environ.get("PORT", 33507))


def words_g():
    connection = sqlite3.connect('db/engdata.db')
    cur = connection.cursor()
    cur.execute('SELECT * FROM dict')
    res = cur.fetchall()
    connection.close()
    words_all = []
    for i in res:
        words_all.append(i)
    return words_all


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    session['words'] = []
    words_all = words_g()
    g.data = words_all
    from flask_login import current_user
    if current_user.is_authenticated:
        connection = sqlite3.connect('db/engdata.db')
        cur = connection.cursor()
        session['words'] = []
        cur.execute('SELECT * FROM learn WHERE name=\'' + current_user.email + "\'")
        res = cur.fetchall()
        connection.close()
        for i in res:
            session.get('words').append(i[1:])
        idc = str(current_user.id) + '.mp3'
    else:
        idc = 0
    is_sound = False
    if request.method == 'POST':
        if 'go_to_learn' in request.form:
            session['words'] = []
            return redirect('/generator')
        elif 'test' in request.form:
            session['part'] = 1
            session['flag'] = 1
            session['eng_words'] = []
            session['rus_words'] = []
            session['count_r'] = 0
            session['a'] = 0
            session['dict_tr'] = {}
            session['part'] = 1
            session['lg'] = 0
            return redirect('/test')
        else:
            id = 0
            for i in request.form:
                id = i
            connection = sqlite3.connect('db/engdata.db')
            cur = connection.cursor()
            cur.execute('SELECT eng FROM learn WHERE id=\'' + str(id) + "\'")
            res = cur.fetchall()
            connection.close()
            speech(res[0][0], 0, current_user.id)
            is_sound = True
    return render_template("index.html", current_user=current_user, words=session.get('words'), sound=is_sound,
                           id = idc)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
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
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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


@app.route("/generator", methods=['GET', 'POST'])
def generator():
    from flask_login import current_user
    try:
        os.remove('static/' + str(current_user.id) + '.mp3')
    except:
        pass
    words_all = words_g()
    is_sound = False
    session['flag'] = 1
    session['eng_words'] = []
    session['rus_words'] = []
    session['count_r'] = 0
    session['a'] = 0
    session['dict_tr'] = {}
    session['part'] = 1
    session['lg'] = 0
    if request.method == 'POST':
        if "btn1" in request.form:
            try:
                count = int(request.form['count'])
            except:
                count = 7
            dig = [i for i in range(len(words_all))]
            id_words = random.sample(dig, count)
            session['id_words'] = id_words
            if id_words:
                connection = sqlite3.connect('db/engdata.db')
                cur = connection.cursor()
                words = []
                for i in id_words:
                    cur.execute('SELECT * FROM dict WHERE id =\'' + str(i) + "\'")
                    res = cur.fetchall()
                    words.append(res[0])
                connection.close()
                session['words'] = words
        elif "test" in request.form:
            """session['flag'] = 1
            session['eng_words'] = []
            session['rus_words'] = []
            session['count_r'] = 0
            session['a'] = 0
            session['dict_tr'] = {}
            session['words'] = words"""
            return redirect('/test')
        else:
            for i in session.get('id_words', None):
                if str(i) in request.form:
                    k = 0
                    for j in session.get('words', None):
                        if j[0] == i:
                            speech(session.get('words', None)[k][1], 0, current_user.id)
                            is_sound = True
                            break
                        else:
                            k += 1
                    break

    return render_template('generator.html', title='Название приложения', words=session.get('words', 0),
                           check=is_sound, id=str(current_user.id) + '.mp3')


@app.route("/test", methods=['GET', 'POST'])
def test():
    from flask_login import current_user
    try:
        os.remove('static/' + str(current_user.id) + '.mp3')
    except:
        pass
    session['rus_words'] = [el for el, _ in groupby(session.get('rus_words', None))]
    if session.get('flag', None) == 1:
        session['eng_words'] = []
        for i in session['words']:
            session['dict_tr'][i[1]] = i[3]
            session['eng_words'].append(i[1])
            session['rus_words'].append(i[3])
        random.shuffle(session['eng_words'])
        random.shuffle(session['rus_words'])
    session['progress'] = round(session['count_r'] / (len(session['eng_words']) * 2) * 100, 0)
    if session['part'] == 1:
        word = session['eng_words'][session['a']]
        word_tr = session['dict_tr'][word]
        rus = session['rus_words'][:7]
        if not word_tr in rus:
            rus.append(word_tr)
            random.shuffle(rus)
    else:
        word = session['eng_words'][session['a']]
        word_tr = get_key(session['dict_tr'], word)
        rus = session['rus_words'][:7]
        if not word_tr in rus:
            rus.append(word_tr)
            random.shuffle(rus)
    sound = False
    if session.get('flag', None) == 1:
        speech(word, session['lg'], current_user.id)
        sound = True
        session['flag'] = 0
    btn_next = False
    correct = False
    ready = False
    wrong_word = ''
    if request.method == 'POST':
        if word_tr in request.form:
            session['count_r'] += 1
            btn_next = True
            correct = True
            if len(session['eng_words']) - 1 > session['a']:
                session['a'] += 1
            else:
                if session['part'] == 1:
                    session['a'] = 0
                    session['eng_words'], session['rus_words'] = session['rus_words'], session['eng_words']
                    session['part'] = 2
                    session['lg'] = 1
                else:
                    try:
                        session['progress'] = round(session['count_r'] / len(session['eng_words']) * 100, 0)
                        connection = sqlite3.connect('db/engdata.db')
                        cur = connection.cursor()
                        for i in session['id_words']:
                            cur.execute('SELECT * FROM dict WHERE id =\'' + str(i) + "\'")
                            res = cur.fetchall()
                            cur.execute("INSERT INTO learn VALUES(\"%s\", \"%s\", \"%s\" , \"%s\" , \"%s\")" % (
                                current_user.email, res[0][0], res[0][1], res[0][2], res[0][3]))
                            connection.commit()
                        connection.close()
                        ready = True
                    except:
                        ready = True

        elif 'btn_next' in request.form:
            random.shuffle(session['rus_words'])
            speech(word, session['lg'], current_user.id)
            sound = True
        elif 'main_page' in request.form:
            session['flag'] = 1
            session['eng_words'] = []
            session['rus_words'] = []
            session['count_r'] = 0
            session['a'] = 0
            session['dict_tr'] = {}
            return redirect('/')
        else:
            if len(session['eng_words']) < session['a']:
                session['a'] += 1
            btn_next = True
            session['eng_words'].append(word)
            for i in request.form:
                wrong_word = i
                if not wrong_word in rus:
                    rus.append(wrong_word)
                    random.shuffle(rus)
    return render_template('test.html', ready=ready, correct=correct,
                           progress=session['progress'], word=word, rus=rus, btn_next=btn_next, word_tr=word_tr,
                           sound=sound, wrong_word=wrong_word, id=str(current_user.id) + '.mp3')



@app.route("/api", methods=['GET', 'POST'])
def api():
    return render_template('api.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session['words'] = []
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(eng_api.blueprint)
    app.run(host='0.0.0.0', port=get_port())



if __name__ == '__main__':
    main()
