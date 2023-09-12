from os import getenv
from uuid import uuid4

from flask import Flask, redirect, request
from requests import get, post

gh_client_id = getenv('GH_CLIENT_ID')
gh_client_secret = getenv('GH_CLIENT_SECRET')
ya_client_id = getenv('YA_CLIENT_ID')
ya_client_secret = getenv('YA_CLIENT_SECRET')
csrf_token = str(uuid4())

app = Flask(__name__)


@app.route('/')
def index():
    return (
        '<html>'
        '<body>'
        f'<a href="https://github.com/login/oauth/authorize?client_id={gh_client_id}&state={csrf_token}&redirect_uri=http://127.0.0.1:5000/get_github_token">Github</a>'
        f'<br>'
        f'<a href="https://oauth.yandex.ru/authorize?response_type=code&client_id={ya_client_id}&state={csrf_token}&redirect_uri=http://127.0.0.1:5000/get_yandex_token">Яндекс</a>'
        f'</body>'
        f'</html>'
    )


@app.route('/get_github_token')
def get_github_token():
    if str(request.args.get('state', '') == csrf_token):
        response = post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': gh_client_id,
                'client_secret': gh_client_secret,
                'code': request.args.get('code', '')
            },
            headers={'Accept': 'application/json'}
        )
        access_token = response.json().get('access_token', '')
        return redirect(f'/github_success?access_token={access_token}')


@app.route('/get_yandex_token')
def get_yandex_token():
    if str(request.args.get('state', '') == csrf_token):
        response = post(
            'https://oauth.yandex.ru/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': ya_client_id,
                'client_secret': ya_client_secret,
                'code': request.args.get('code', '')
            },
            headers={'Content-type': 'application/x-www-form-urlencoded'}
        )
        access_token = response.json().get('access_token', '')
        return redirect(f'/yandex_success?access_token={access_token}')


@app.route('/github_success')
def github_success():
    access_token = request.args.get('access_token')
    response = get(
        'https://api.github.com/user',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    return response.content


@app.route('/yandex_success')
def yandex_success():
    access_token = request.args.get('access_token')
    response = get(
        'https://login.yandex.ru/info',
        headers={'Authorization': f'OAuth {access_token}'}
    )
    return response.content


app.run()
