import sqlite3
import random

from flask import Flask, render_template, request, make_response, jsonify
from flask_wtf import Form
from werkzeug.utils import redirect
from text_to_speech import speech

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

words = []
id_words = []


@app.route("/generator", methods=['GET', 'POST'])
def generator():
    global words
    global id_words

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
    return render_template('test.html', title='Название приложения')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
