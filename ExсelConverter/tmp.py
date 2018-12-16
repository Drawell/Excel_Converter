'''import MySQLdb
con = MySQLdb.connect(host="localhost", user="root", passwd="pass", db="test")

#Удалить и создать базу данных
con.query('DROP DATABASE test')
con.query('CREATE DATABASE test')

#Предоставить полномочия на базу данных
con.query("GRANT ALL ON test.* to 'root'@'localhost'")

cur = con.cursor()

cur.execute("SET NAMES 'utf8'")

cur.execute("CREATE TABLE test(id INT, name VARCHAR(20))")

cur.execute("INSERT INTO test VALUES(1, 'Anna')")
cur.execute("INSERT INTO test VALUES(2, 'Boris')")

cur.execute("SELECT * FROM test")
for s in cur.fetchall():
    print(s)

cur.execute("UPDATE test SET name = 'Inna' WHERE id = 1")
cur.execute("DELETE FROM test WHERE id = 1")

cur.execute("DROP TABLE test")
cur.close()
con.commit()
con.close()
'''

import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
from ExсelConverter.db_creator import DBCreator
from ExсelConverter.sql_enums import TypeEnum as TE, ConstraintEnum as CE

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.urandom(24)

DEBUG = True

CREATORS = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    atr = 'a'
    dict = {1: 'a', 2: 'b'}
    return render_template('tmp.html', dict=dict, atr=atr)


if __name__ == '__main__':
    app.run()