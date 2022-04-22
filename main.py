import random
import sqlite3
import datetime

from flask import Flask, render_template, request, session, make_response
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_session import Session
from werkzeug.utils import redirect
from data.users import User
from data import db_session, eng_api
from forms.user import RegisterForm, LoginForm
from text_to_speech import speech
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
#run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=2
)

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
    connection = sqlite3.connect('db/engdata.db')
    cur = connection.cursor()
    cur.execute('SELECT * FROM dict')
    res = cur.fetchall()
    connection.close()
    words_all = []
    for i in res:
        words_all.append(i)
    session['words_all'] = words_all

    from flask_login import current_user
    if request.method == 'POST':
        if 'go_to_learn' in request.form:
            return redirect('/generator')
        elif 'go_to_remember' in request.form:
            return redirect('/remember')
    return render_template("index.html", current_user=current_user, words=session.get('words_all'))


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

    is_sound = False
    session['flag'] = 1
    session['eng_words'] = []
    session['rus_words'] = []
    session['count_r'] = 0
    session['a'] = 0
    session['dict_tr'] = {}
    words_all = session.get('words_all', None)
    id_words = session.get('id_words', None)

    if request.method == 'POST':
        if "btn1" in request.form:
            dig = [i for i in range(7600)]
            id_words = random.sample(dig, int(request.form['count']))
            if id_words:
                connection = sqlite3.connect('db/engdata.db')
                cur = connection.cursor()
                words = []
                for i in id_words:
                    cur.execute('SELECT * FROM dict WHERE id =\'' + str(i) + "\'")
                    res = cur.fetchall()
                    print(res)
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
            for i in id_words:
                if str(i) in request.form:
                    k = 0
                    for j in session.get('words', None):
                        if j[0] == i:
                            speech(session.get('words', None)[k][1], 0)
                            is_sound = True
                            break
                        else:
                            k += 1
                    break

    return render_template('generator.html', title='Название приложения', words=session.get('words', None), check=is_sound)


@app.route("/test", methods=['GET', 'POST'])
def test():
    """eng_words = session.get('eng_words', None)
    rus_words = session.get('rus_words', None)
    flag = session.get('flag', None)
    count_r = session.get('count_r', None)
    words = session.get('words', None)
    a = session.get('a', None)
    progress = session.get('progress', None)
    dict_tr = session.get('dict_tr', None)
    part = session.get('part', None)
    lg = session.get('lg', None)
    id_words = session.get('id_words', None)"""

    from flask_login import current_user
    if flag == 1:
        eng_words = []
        for i in words:
            dict_tr[i[1]] = i[3]
            eng_words.append(i[1])
            rus_words.append(i[3])
        random.shuffle(eng_words)
        random.shuffle(rus_words)
    progress = round(count_r / len(eng_words) * 100, 0) // 2
    if part == 1:
        word = eng_words[a]
        word_tr = dict_tr[word]
        rus = rus_words[:7]
        if not word_tr in rus:
            rus.append(word_tr)
            random.shuffle(rus)
    else:
        word = eng_words[a]
        word_tr = get_key(dict_tr, word)
        rus = rus_words[:7]
        if not word_tr in rus:
            rus.append(word_tr)
            random.shuffle(rus)
    sound = False
    if flag == 1:
        speech(word, lg)
        sound = True
        flag = 0
    btn_next = False
    correct = False
    ready = False
    wrong_word = ''
    if request.method == 'POST':
        if word_tr in request.form:
            count_r += 1
            btn_next = True
            correct = True
            if len(eng_words) - 1 > a:
                a += 1
            else:
                if part == 1:
                    a = 0
                    eng_words, rus_words = rus_words, eng_words
                    part = 2
                    lg = 1
                else:
                    try:
                        progress = round(count_r / len(eng_words) * 100, 0)
                        connection = sqlite3.connect('db/engdata.db')
                        cur = connection.cursor()
                        for i in id_words:
                            cur.execute('SELECT * FROM dict WHERE id =\'' + str(i) + "\'")
                            res = cur.fetchall()
                            print(res[0])
                            cur.execute("INSERT INTO learn VALUES(\"%s\", \"%s\", \"%s\" , \"%s\" , \"%s\")" % (
                                current_user.email, res[0][0], res[0][1], res[0][2], res[0][3]))
                            connection.commit()
                        connection.close()
                        ready = True
                    except:
                        ready = True

        elif 'btn_next' in request.form:
            random.shuffle(rus_words)
            speech(word, lg)
            sound = True
        elif 'main_page' in request.form:
            session['flag'] = 1
            session['eng_words'] = []
            session['rus_words'] = []
            session['count_r'] = 0
            session['a'] = 0
            session['dict_tr'] = {}
            session['words'] = words
            return redirect('/')
        else:
            if len(eng_words) < a:
                a += 1
            btn_next = True
            eng_words.append(word)
            for i in request.form:
                wrong_word = i
                if not wrong_word in rus:
                    rus.append(wrong_word)
                    random.shuffle(rus)
    return render_template('test.html', ready=ready, correct=correct,
                           progress=progress, word=word, rus=rus, btn_next=btn_next, word_tr=word_tr,
                           sound=sound, wrong_word=wrong_word)


@app.route("/remember", methods=['GET', 'POST'])
def remember():
    print(session.get('words_all'))
    from flask_login import current_user
    connection = sqlite3.connect('db/engdata.db')
    cur = connection.cursor()
    words.clear()
    cur.execute('SELECT * FROM learn WHERE name=\'' + current_user.email + "\'")
    res = cur.fetchall()
    connection.close()
    for i in res:
        words.append(i[1:])
    is_sound = False
    if request.method == 'POST':
        if 'test' in request.form:
            return redirect('/test')
        elif 'generator' in request.form:
            return redirect('/generator')
        else:
            id = 0
            for i in request.form:
                id = i
            connection = sqlite3.connect('db/engdata.db')
            cur = connection.cursor()
            cur.execute('SELECT eng FROM learn WHERE id=\'' + str(id) + "\'")
            res = cur.fetchall()
            connection.close()
            print(res[0][0])
            speech(res[0][0], 0)
            is_sound = True
    return render_template('remember.html', title='Название приложения', words=words, sound=is_sound)


@app.route("/api", methods=['GET', 'POST'])
def api():
    return render_template('api.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(eng_api.blueprint)
    app.run(debug=True)


if __name__ == '__main__':
    main()
