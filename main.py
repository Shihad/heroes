#библиотеки
import random

from flask import Flask, render_template, request, redirect
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from threading import Event, Thread

from models import db, Personage, User


app = Flask(__name__)

cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'this_is_my_secret_key_It_is_only_mine'
db.init_app(app)

login_manager = LoginManager(app)

idle_messages=["Ничего не происходит.",
          "Тишина...",
          "Нет новостей - хорошая новость"]
battle_messages=["{} сражается за свою жизнь!",
          "Сеча лютая, {} бьется отчаянно!",
          "{} рубится без остановки!"]
dead_messages=["{} разлагается физически",
          "Червяк ползет по ребру {} уже второй час",
          "{} переворачивается в гробу"]

heal_messages=["{} пьет зеленку",
          "Ядреный заячий помет лечит {} уже второй час",
          "{} съел горсть таблеток"]

# функция - загрузчик пользователей
# без нее не работает функция login_user
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

@app.before_first_request
def create_table():
    db.drop_all()
    db.create_all()
    hero1=Personage('Вирджил')
    hero2 = Personage('Джахейра')
    hero3 = Personage('Рейстлин Маджере')
    user1=User('Vvasya','vasya.pupkin@mail.ru','qwerty')
    user2=User('Petya','petya.pyatochkin@mail.ru','12345')
    user3=User('admin','i.m.root@mail.ru','nimda')
    db.session.add(hero1)
    db.session.add(hero2)
    db.session.add(hero3)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    print(dir(user1))
    db.session.commit()

@app.route("/personages")
def personages_list():
    personages=Personage.query.all()
    return render_template("personages_list.html",personages=personages)

@app.route("/personages/<p_id>")
def personage_page(p_id):
    personage=Personage.query.filter_by(id=p_id).first()
    return render_template("personage_page.html",personage=personage)

@app.route("/personages/create", methods=["POST","GET"])
def personage_create():
    if request.method=="GET":
        return render_template("personages_create.html")
    if request.method=="POST":
        name=request.form['name']
        hero = Personage(name)
        db.session.add(hero)
        db.session.commit()
        return redirect("/personages")

@app.route("/signup",methods = ['post','get'])
def user_create():
    if request.method=="GET":
        return render_template("signup.html")
    if request.method=="POST":
        login = request.form['login']
        mail = request.form['mail']
        password = request.form['password']
        pass_confirm = request.form['pass_confirm']
        if password==pass_confirm:
            user = User(login,mail,password)
            db.session.add(user)
            db.session.commit()
            return redirect("/login")
        else:
            print('Пароли не совпадают')
            return render_template("signup.html",message='Пароли не совпадают')

@app.route("/login",methods=['post','get'])
def user_login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        if user:
            if user.check_password(password):
                # авторизация
                login_user(user, remember=False)
                return redirect("/userpage")
            else:
                print("Неправильный пароль")
                return render_template('login.html', message='Неверный пароль')

@app.route("/userpage")
@login_required
def user_page():
    return render_template('userpage.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/api/personages")
def user_personage_page():
    p_id=1
    personage = Personage.query.filter_by(id=p_id).first_or_404()
    if personage.state == 'idle':
        return {"status": 200, "message": random.choice(idle_messages), "hero": personage.json()}
    if personage.state == 'battle':
        return {"status": 200, "message": random.choice(battle_messages).format(personage.name) ,
                "hero": personage.json()}
    if personage.state == 'dead':
        return {"status": 200, "message": random.choice(dead_messages).format(personage.name),
                "hero": personage.json()}
    if personage.state == 'heal':
        return {"status": 200, "message": random.choice(heal_messages).format(personage.name),
                "hero": personage.json()}


def call_repeatedly(interval, func, *args):
    stopped = Event()
    counter = 1

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)

    Thread(target=loop).start()
    return stopped.set


def game_loop():
    with app.app_context():
        personages = Personage.query.all()
        for personage in personages:
            if personage.state == 'idle':
                if personage.hp <= personage.max_hp // 5:
                    personage.state = 'heal'
                if random.randint(1, 100) < 25:
                    personage.state = 'battle'
            elif personage.state == 'battle':
                personage.hp -= random.randint(5, 10)
                if personage.hp<=0:
                    personage.state = 'dead'
                if random.randint(1, 100) < 30:
                    personage.state = 'idle'
            elif personage.state == 'dead':
                if random.randint(1, 1000) < 5:
                    personage.state = 'idle'
            db.session.add(personage)
        db.session.commit()

cancel_future_calls = call_repeatedly(10, game_loop) #вызов функции game_loop с периодом 10 с

app.run()
