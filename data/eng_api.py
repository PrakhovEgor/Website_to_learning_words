import sqlite3

import flask
from flask import jsonify

blueprint = flask.Blueprint(
    'eng_api',
    __name__,
    template_folder='templates'
)

words_all = []
connection = sqlite3.connect('db/engdata.db')
cur = connection.cursor()
cur.execute('SELECT * FROM dict')
res = cur.fetchall()
connection.close()
for i in res:
    words_all.append(i)


@blueprint.route('/api/eng')
def get_words():
    return jsonify(
        {
            'words': [item for item in words_all]
        }
    )


@blueprint.route('/api/eng/<word>', methods=['GET'])
def get_one_word(word):
    cor = []
    for i in words_all:
        if word.lower() in i[1] or word.lower() in i[3]:
            cor.append(i[1:])
    if cor:
        return jsonify(
            {
                'words': cor
            }
        )

    return jsonify({'error': 'Not found'})
