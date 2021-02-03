from flask import Flask
from flask import render_template
from flask import request

from backend import MyApp

app = MyApp()

app_server = Flask(__name__, static_folder='static')
print("Flask app is running...")

student_id = 0
work_id = 0


@app_server.route('/', methods=['GET', 'POST'])
def home():
    print(request.method)
    if request.method == 'POST':
        if request.form.get('Export') == 'Export':
            print("Export")
            app.export_db()
        elif request.form.get('Import') == 'Import':
            print("Import")
            app.import_db()
        elif request.form.get('Clear') == 'Clear':
            print("Clear db")
            app.clear_db()
        return render_template('home.html', done=True)
    return render_template('home.html', done=None)


@app_server.route('/add_asp', methods=['GET', 'POST'])
def add_asp():
    if request.method == 'POST':
        print("Запрос на добавление аспиранта")
        global student_id
        student = {
            'id': student_id,
            'name': request.form['Name'],
            'surname': request.form['Surname'],
            'patronymic': request.form['Patronymic'],
            'group_number': request.form['GroupNumber'],
            'year_of_admission': request.form['Year'],
            'email': request.form['Email'],
            'login': request.form['Login'],
            'password': request.form['Pass'],
        }

        app.add_graduate(student)
        student_id += 1

        return render_template('add_asp.html', done=True)

    return render_template('add_asp.html', done=None)


@app_server.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        print("Запрос на добавление работы")
        student = {
            'login': request.form['Login'],
            'password': request.form['Pass'],
        }

        global work_id
        work = {
            'id': work_id,
            'semester': request.form['Semester'],
            'index': request.form['Index'],
            'link': request.form['Link'],
        }

        if app.new_work(student, work):
            work_id += 1
            return render_template('add_task.html', done=True)

    return render_template('add_task.html', done=None)


@app_server.route('/watch', methods=['GET', 'POST'])
def watch():
    if request.method == 'POST':
        print("Запрос на просмотр статистики")

        student = {
            'name': request.form['Name'],
            'surname': request.form['Surname'],
            'patronymic': request.form['Patronymic'],
        }
        list, mark = app.find_student_works_by_name(student)

        pattern = ""
        for work in list:
            pattern += f"<li>{work}</li>"
        html_list = "<ol>" + pattern + "</ol>"

        html_list += f"<p> Оценка на данный момент: {mark} </p>"

        return html_list

    return render_template('watch.html')
