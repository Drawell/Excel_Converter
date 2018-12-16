import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
from ExсelConverter.db_creator import DBCreator
from ExсelConverter.sql_enums import TypeEnum as TE, ConstraintEnum as CE

EXCEL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ExcelFiles')
DB_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DBs')

app = Flask(__name__)
app.config['DB_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DBs')
app.config['EXCEL_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ExcelFiles')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.urandom(24)

DEBUG = True

CREATORS = {}

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            if filename[-4:] == 'xlsx':
                file.save(os.path.join(EXCEL_FOLDER, filename))
                session['file_name'] = filename
                session['file_path'] = os.path.join(EXCEL_FOLDER, filename)
                return redirect(url_for('set_db'))

    return render_template('index.html')

@app.route('/set_db/', methods=['GET', 'POST'])
def set_db():
    creator = DBCreator(session['file_path'])
    filename = session['file_name']
    CREATORS[filename] = creator
    tables = creator.tables
    return render_template('TablesSettings.html', filename=filename, tables=tables)

@app.route('/show_table/', methods=['GET', 'POST'])
def show_table():
    if request.method == 'POST':
        table_index = request.form.get('index')
        if table_index == 'None':
            return 'Таблицы нет'
        else:
            table_index = int(table_index)
        session['table_index'] = table_index
    else:
        table_index = session['table_index']

    attributes = CREATORS[session['file_name']].tables[table_index].attributes
    all_types_list = TE.all_types_list()
    all_constraints_list = CE.all_constraints_list()
    table_dict = CREATORS[session['file_name']].tables
    return render_template('Table.html', attributes=attributes, all_types_list=all_types_list,
                           all_constraints_list=all_constraints_list, CE=CE, table_dict=table_dict)

@app.route('/change_name/', methods=['POST'])
def change_name():
    index = int(request.form.get('index'))
    val = request.form.get('val')
    CREATORS[session['file_name']].change_atr_name(session['table_index'], index, val)
    return redirect(url_for('show_table'))

@app.route('/change_index/', methods=['POST'])
def change_index():
    index = int(request.form.get('index'))
    val = int(request.form.get('val'))
    CREATORS[session['file_name']].change_atr_index(session['table_index'], index, val)
    print(index, val)
    return redirect(url_for('show_table'))

@app.route('/change_type/', methods=['POST'])
def change_type():
    index = int(request.form.get('index'))
    val = request.form.get('val')
    varchar_num = int(request.form.get('varchar'))
    CREATORS[session['file_name']].change_atr_type(session['table_index'], index, val, varchar_num)
    print(index, val)
    return redirect(url_for('show_table'))

@app.route('/change_constraint/', methods=['POST'])
def change_constraint():
    index = int(request.form.get('index'))
    val = request.form.get('val')
    CREATORS[session['file_name']].change_atr_constraint(session['table_index'], index, val)
    print(index, val)
    return redirect(url_for('show_table'))

@app.route('/change_fk_table/', methods=['POST'])
def change_fk_table():
    index = int(request.form.get('index'))
    table_index = request.form.get('table_index')
    if table_index is None:
        return ''
    table_index = int(table_index)

    value = CREATORS[session['file_name']].tables[table_index].name
    CREATORS[session['file_name']].change_atr_foreign_key(session['table_index'], index, value, None)

    dict = CREATORS[session['file_name']].tables[table_index].attributes
    dis = request.form.get('dis')
    atr = CREATORS[session['file_name']].tables[session['table_index']].attributes[index]
    return render_template('Selector.html', index=index, atr=atr, dict=dict, disabled=dis)
    #return redirect(url_for('show_table'))

@app.route('/change_fk_atr/', methods=['POST'])
def change_fk_atr():
    index = request.form.get('index')
    if index is None:
        redirect(url_for('show_table'))
    index = int(index)
    value = request.form.get('val')
    CREATORS[session['file_name']].change_atr_foreign_key(session['table_index'], index, None, value)

    return redirect(url_for('show_table'))

@app.route('/create_SQLite/', methods=['GET', 'POST'])
def create_SQLite():
    filename = request.form.get('value')
    if os.path.exists(os.path.join(DB_FOLDER, (filename + '.db'))):  # удаляем, если такая имеется
        os.remove(os.path.join(DB_FOLDER, (filename + '.db')))

    errors = CREATORS[session['file_name']].create_SQLite_db(DB_FOLDER, filename)
    res = 'Errors: <br>'
    for error in errors:
        res += '%s<br>' %(error)

    return res

@app.route('/create_SQLite_TXT/', methods=['GET', 'POST'])
def create_SQLite_TXT():
    filename = request.form.get('value')
    if os.path.exists(os.path.join(DB_FOLDER, (filename + '.txt'))):  # удаляем, если такая имеется
        os.remove(os.path.join(DB_FOLDER, (filename + '.txt')))

    CREATORS[session['file_name']].create_SQLite_txt(DB_FOLDER, filename)
    return ''

@app.route('/create_MySQL_TXT/', methods=['GET', 'POST'])
def create_MySQL_TXT():
    filename = request.form.get('value')
    if os.path.exists(os.path.join(DB_FOLDER, (filename + '.txt'))):  # удаляем, если такая имеется
        os.remove(os.path.join(DB_FOLDER, (filename + '.txt')))

    CREATORS[session['file_name']].create_MySQL_txt(DB_FOLDER, filename)
    return ''

@app.route('/download/<file>', methods=['GET'])
def download(file):
    return send_from_directory(DB_FOLDER, file)


if __name__ == '__main__':
    app.run()