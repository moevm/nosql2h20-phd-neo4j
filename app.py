from flask import Flask
from flask import render_template
from flask import request, abort, redirect

from backend import MyApp

app = MyApp()

app_server = Flask(__name__, static_folder='static')


@app_server.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['UrlInput']
        tiny_url = app.add_url(url)
        return render_template('home.html', tiny_url=request.base_url + str(tiny_url))

    return render_template('home.html')


@app_server.route('/about')
def about():
    return render_template('about.html')


@app_server.route('/<url>')
def show_post(url):
    url = int(url)

    if app.check_url(url):
        return redirect(app.get_url(url))
    else:
        abort(404)
