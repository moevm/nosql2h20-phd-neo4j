from collections import deque
from functools import lru_cache

from flask import Flask
from flask import render_template
from flask import request

CACHE_SIZE = 100


class MyApp:
    length_of_a_hash = 6
    divider = 10 ** length_of_a_hash
    max_capacity = 8192

    def __init__(self):
        self._urls = deque()
        self.urls_mapping = {}

    @lru_cache(maxsize=CACHE_SIZE)
    def add_url(self, url):
        tiny_url = int(hash(url) % self.divider)
        self._urls.append(tiny_url)
        self.urls_mapping[tiny_url] = url

        if len(self._urls) > self.max_capacity:
            self.delete_url()

        return tiny_url

    def delete_url(self):
        url_to_delete = self._urls.popleft()
        self.urls_mapping.pop(url_to_delete)

    @lru_cache(maxsize=CACHE_SIZE)
    def check_url(self, url):
        return url in self._urls

    @lru_cache(maxsize=CACHE_SIZE)
    def get_url(self, url):
        return self.urls_mapping[url]


app = MyApp()

app_server = Flask(__name__, static_folder='static')


# @app_server.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         url = request.form['UrlInput']
#         tiny_url = app.add_url(url)
#         return render_template('home.html', tiny_url=request.base_url + str(tiny_url))
#
#     return render_template('home.html')


@app_server.route('/')
def about():
    return render_template('home.html')


@app_server.route('/add_asp')
def add_asp():
    return render_template('add_asp.html')


@app_server.route('/add_task')
def add_task():
    return render_template('add_task.html')


@app_server.route('/watch')
def watch():
    return render_template('watch.html')
