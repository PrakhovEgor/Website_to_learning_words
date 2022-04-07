import sqlite3
import random

from flask import Flask, render_template, request
from werkzeug.utils import redirect
from text_to_speech import speech

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

words = []
id_words = []

flag = 1
eng_words = []
rus_words = []
progress = 0
count_r = 0
a = 0
dict_tr = {}


@app.route("/generator", methods=['GET', 'POST'])
def generator():
    global eng_words, rus_words, flag, count_r, words, a, id_words, words, dict_tr
    is_sound = False
    if request.method == 'POST':
        if "btn1" in request.form:
            dig = [i for i in range(7617)]
            try:
                id_words = random.sample(dig, int(request.form['count']))
            except:
                id_words = []
            if id_words:
                connection = sqlite3.connect('db/engdata.db')
                cur = connection.cursor()
                words.clear()
                for i in id_words:
                    cur.execute('SELECT * FROM dict WHERE id =\'' + str(i) + "\'")
                    res = cur.fetchall()
                    words.append(res[0])
        elif "test" in request.form:
            flag = 1
            eng_words = []
            rus_words = []
            count_r = 0
            a = 0
            dict_tr = {}
            return redirect('/test')

        else:
            for i in id_words:
                if str(i) in request.form:
                    k = 0
                    for j in words:
                        if j[0] == i:
                            speech(words[k][1])
                            is_sound = True
                            break
                        else:
                            k += 1
                    break

    return render_template('generator.html', title='Название приложения', words=words, check=is_sound)


@app.route("/test", methods=['GET', 'POST'])
def test():
    global eng_words, rus_words, flag, count_r, words, a, progress, dict_tr
    try:
        if flag == 1:
            eng_words = []
            for i in words:
                dict_tr[i[1]] = i[3]
                eng_words.append(i[1])
                rus_words.append(i[3])
            random.shuffle(eng_words)
            random.shuffle(rus_words)

        progress = round(count_r / len(eng_words) * 100, 0)
        print(len(eng_words), a)
        word = eng_words[a]
        word_tr = dict_tr[word]
        sound = False
        if flag == 1:
            speech(word)
            sound = True
            flag = 0
        btn_next = False
        correct = False
        ready = False
        wrong_word = ''
        rus = rus_words[:7]
        if not word_tr in rus:
            rus.append(word_tr)
            random.shuffle(rus)

        if request.method == 'POST':
            if word_tr in request.form:
                count_r += 1
                btn_next = True
                correct = True
                if len(eng_words) - 1 > a:
                    a += 1
                else:
                    progress = round(count_r / len(eng_words) * 100, 0)
                    ready = True

            elif 'btn_next' in request.form:

                random.shuffle(rus_words)
                speech(word)
                sound = True
            elif 'main_page' in request.form:
                return redirect('/generator')
            else:
                if len(eng_words) < a:
                    a += 1
                btn_next = True
                eng_words.append(word)
                for i in request.form:
                    wrong_word = i
        return render_template('test2.html', ready=ready, correct=correct,
                               progress=progress, word=word, rus=rus, btn_next=btn_next, word_tr=word_tr,
                               sound=sound, wrong_word=wrong_word)
    except:
        return redirect('/generator')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
