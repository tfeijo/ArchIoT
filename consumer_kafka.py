import json
from typing import List, Dict, Any
from flask_paginate import Pagination, get_page_parameter
from models import User, Group
from kafka import KafkaConsumer
from flask import Flask, render_template, request, redirect, session, flash, url_for

app = Flask(__name__)
app.secret_key = '123'

KAFKA_TOPIC = 'Siafu-Office'

groups: Dict[str, Group] = {}

group = Group('dev1', ['entityID', 'time', 'Activity'], [])
groups[group.name] = group
group = Group('dev2', ['entityID', 'time', 'position'], [])
groups[group.name] = group

users: Dict[str, User] = {}
user = User('Thiago Feijó', 'tfeijo', '123', 'dev1')
users[user.login] = user

groups['dev1'].list_user.append(user.name)

user = User('Nedson', 'nedson', '123', 'dev2')
users[user.login] = user
groups['dev2'].list_user.append(user.name)


def kafka_consult(parsed_topic_name):
    consumer = KafkaConsumer(parsed_topic_name,
                             auto_offset_reset='earliest',
                             bootstrap_servers=['localhost:9092'],
                             api_version=(0, 10),
                             consumer_timeout_ms=1000,
                             fetch_max_bytes=1
                             )
    list_user = []
    for msg in consumer:
        records = json.loads(msg.value.decode('utf8'))
        list_user.append(records)

    if consumer is not None:
        consumer.close()

    return list_user


def kafka_consult_key(parsed_topic_name):

    consumer = KafkaConsumer(parsed_topic_name,
                             auto_offset_reset='earliest',
                             bootstrap_servers=['localhost:9092'],
                             api_version=(0, 10),
                             consumer_timeout_ms=1000
                             )


    for msg in consumer:
        records = json.loads(msg.value.decode('utf8'))
        break

    list_key = []

    for key in records:
        list_key.append(key)

    return list_key


@app.route('/')
def index():
    if not is_logged():
        return back_to_login(f'Usuário não autenticado.')
    else:
        global list_agent

        list_agent = kafka_consult(KAFKA_TOPIC)

        search: bool = False
        q = request.args.get('q')
        if q:
            search: bool = True

        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 20

        pagination = Pagination(page=page,
                                total=len(list_agent),
                                search=search, record_name='agents',
                                css_framework='bootstrap4',
                                per_page=per_page
                                )
        begin = pagination.skip
        end = begin + per_page - 1

        login_logged_user = session['usuario_logado']
        group = users[login_logged_user].group

        list_key = groups[group].list_key

        return render_template('kafka.html', titulo='Agent List',
                               list_agent=list_agent[begin:end],
                               group=group,
                               pagination=pagination,
                               list_key=list_key)


@app.route('/new-user')
def new_user():
    if not is_logged():
        return back_to_login()
    else:
        return render_template('new_user.html', titulo='New user', groups=groups)


@app.route('/list-user')
def list_user():
    if not is_logged():
        return back_to_login()
    else:

        user_list = []
        for user in users:
            user_list.append(users[user])

        return render_template('list_users.html', titulo='Users', users=user_list)


@app.route('/new-group')
def new_group():
    if not is_logged():
        return back_to_login()
    else:
        list_key = kafka_consult_key(KAFKA_TOPIC)

        return render_template('new_group.html',
                               titulo='New group',
                               groups=groups,
                               list_key=list_key)


@app.route('/list-group')
def list_group():
    if not is_logged():
        return back_to_login()
    else:

        group_list = []
        for group in groups:
            group_list.append(groups[group])

        return render_template('list_groups.html', titulo='Groups', groups=group_list)


@app.route('/create-user', methods=['POST', ])
def create_user():
    if not is_logged():
        return back_to_login()
    else:
        nome = request.form['fullname']
        login = request.form['login']
        password = request.form['password']
        group = request.form['group']
        new_user = User(nome, login, password, group)

        if new_user.login in users:
            flash('User already exist!')
        else:
            users[new_user.login] = new_user
            groups[group].list_user.append(new_user.name)
            if new_user.login in users:
                flash('Usuário criado com sucesso!')
            else:
                flash('Erro ao criar usuário!')

        return redirect(url_for('new_user'))


@app.route('/create-group', methods=['POST', ])
def create_group():
    if not is_logged():
        return back_to_login()
    else:
        nome = request.form['groupname']
        list_key = request.form.getlist('fields')

        new_group = Group(nome, list_key, [])

        if new_group.name in groups:
            flash('Group already exist!')
        else:
            groups[new_group.name] = new_group
            if new_group.name in groups:
                flash('Grupo criado com sucesso!')
            else:
                flash('Erro ao criar grupo!')

        return redirect(url_for('list_group'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    if is_logged():
        flash('Sessão encerrada.')
    else:
        flash('Usuário não autenticado')

    session.clear()
    list_agent = None
    return redirect(url_for('login'))


@app.route('/autenticar', methods=['POST', ])
def autenticar():
    login = request.form['login']
    name = users[login].name
    password = request.form['password']

    if login in users and users[login].password == password:
        session['usuario_logado'] = login
        flash(f'{name} autenticado com sucesso!')
        return redirect(url_for('index'))
    else:
        return back_to_login('Erro de login. Tente novamente.')


def is_logged():
    return 'usuario_logado' in session.keys()


def back_to_login(msg='Você deve se autenticar.'):
    list_agent = None
    flash(msg)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
