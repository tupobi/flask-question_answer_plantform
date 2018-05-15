# flask问答平台小案例笔记

## 配置文件

### config.py

(配置项目基本信息)

```python
import os
from datetime import timedelta

# debug模式
DEBUG = True

# 配置数据库
DIALECT = 'mysql'
DRIVER = 'mysqldb'
USERNAME = 'root'
PASSWORD = '1234'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'questionplantform'
# SQLALCHEMY标志URI
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8" \
    .format(DIALECT, DRIVER, USERNAME,
            PASSWORD, HOST, PORT,
            DATABASE)
# 忽略SQLALCHEMY警告
SQLALCHEMY_TRACK_MODIFICATIONS = False

# session
# 设置session'盐'：SECRET_KEY
SECRET_KEY = os.urandom(24)
# 设置session过期时间，25天，设置permanent默认一个月，没设置关闭浏览器就销毁
PERMANENT_SESSION_LIFETIME = timedelta(days=25)
```

### exts.py

(扩展文件，防止循环引用)

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

### models.py

(数据库模型文件)

```python
from exts import db
```

### manage.py

(终端脚本控制文件)

```python
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app
from exts import db

manager = Manager(app)

# 使用migrate绑定app和db
migrate = Migrate(app, db)

# 添加迁移脚本的命令到manager中去
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
```
## 父模板的抽离

新建base.html和base.css文件

### base.html

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{% block title %}{% endblock %}-问答平台</title>
        {% block head %}{% endblock %}

        <!-- 最新版本的 Bootstrap 核心 CSS 文件 -->
        <link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css"
            integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u"
            crossorigin="anonymous">

        <script src="https://cdn.bootcss.com/jquery/3.3.1/jquery.min.js"></script>

        <!-- 最新的 Bootstrap 核心 JavaScript 文件 -->
        <script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"
            integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa"
            crossorigin="anonymous"></script>

        <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
    </head>
    <body>
        <nav class="navbar navbar-default">
            <div class="container">
                <!-- Brand and toggle get grouped for better mobile display -->
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse"
                        data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="#">
                        <img class="logo"
                            src="{{ url_for('static', filename = 'images/logo.jpg') }}" alt="问答平台">
                    </a>
                </div>

                <!-- Collect the nav links, forms, and other content for toggling -->
                <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                    <ul class="nav navbar-nav">
                        <li class="active">
                            <a href="#">首页
                                <span class="sr-only">(current)</span>
                            </a>
                        </li>
                        <li>
                            <a href="#">发布问答</a>
                        </li>
                    </ul>
                    <form class="navbar-form navbar-left">
                        <div class="form-group">
                            <input type="text" class="form-control" placeholder="输入搜索内容">
                        </div>
                        <button type="submit" class="btn btn-default">搜索</button>
                    </form>
                    <ul class="nav navbar-nav navbar-right">
                        <li>
                            <a href="#">登录</a>
                        </li>
                        <li>
                            <a href="#">注册</a>
                        </li>
                    </ul>
                </div><!-- /.navbar-collapse -->
            </div><!-- /.container-fluid -->
        </nav>
        {% block body %}{% endblock %}
    </body>
</html>
```

### base.css

```css
.logo {
    width: 80px;
}
```

### index.html继承base.html

```html
{% extends 'base.html' %}

{% block  title%}
    首页
{% endblock %}

{% block body %}
    我是首页
{% endblock %}
```

## 创建数据库

### models.py

创建模型

```python
from exts import db


class User(db.Model):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(11), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
```

### manage.py

数据库迁移

```python
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app
from exts import db
from models import User

manager = Manager(app)

# 使用migrate绑定app和db
migrate = Migrate(app, db)

# 添加迁移脚本的命令到manager中去
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
```

### migrate命令

- 写好manage.py后，**进入虚拟环境并activate**，然后在虚拟环境中用cd..回退，进入到项目目录中命令：

  **python manage.py db init**

  初始化migrate

- 然后命令：

  **python manage.py db migrate**

  生成一个迁移文件

- 然后实时迁移更新数据库

  **python manage.py db upgrade**

## 装饰器

### 写一个装饰器

1. 假设需求：在指定的函数执行之前先打印hell world

2. 实现方案一：

   在每个需要打印hello world的函数最前面都调用print_hello_world方法，如下（不够优雅）

   ```python
   # 需要在执行前打印hello world
   def add(a, b):
       print_hello_world()
       c = a + b
       print('结果c是：{}'.format(c))
   
   
   # 需要在执行前打印hello world
   def run():
       print_hello_world()
       print('run')
   
   
   # 不需要在执行前打印hello world
   def do_something():
       print('do something')
   
   
   add(1, 2)
   run()
   do_something()
   ```

3. 用装饰器实现

   ```python
   # 装饰器实际上就是一个函数
   # 有两个特别之处
   # 1. 参数是一个函数
   # 2. 返回值是一个函数
   
   
   def print_hello_world_decorator(func):
       def wrapper(*args, **kwargs):
           print('hello world')
           func(*args, **kwargs)
   
       # 注意，这里返回的是一个函数体，不是函数执行完后返回
       return wrapper
   
   
   # 需要在执行前打印hello world
   @print_hello_world_decorator
   def run():
       print('run')
   
   
   # 需要在执行前打印hello world
   @print_hello_world_decorator
   def add(a, b):
       c = a + b
       print("相加结果c == {}".format(c))
   
   
   # 不需要在执行前打印hello world
   def do_something():
       print('do something')
   
   
   # 这样写没有参数是OK的
   run()
   # 有两个参数报错
   # TypeError: wrapper() takes 0 positional arguments but 2 were given
   # 解决办法是在wrapper和func两个函数都加上a,b参数
   # 但是run函数又不行了，因为run函数没有参数
   # 解决办法是在wrapper和func函数里传(*args, **kwargs)可以表示任何参数
   add(1, 2)
   do_something()
   ```

   然而这样还是不行，当print(run._name__)run函数的名字时，如果加了装饰器修饰之后名称变为了wrapper。名字被偷换了，相当危险，可能连函数都找不到了，所以采用下面这种更为优雅的方式：from functools import wrapper

   ```python
   def print_hello_world_decorator(func):
   	# 只需要在这里再加个装饰器即可	
       @wraps(func)
       def wrapper(*args, **kwargs):
           print('hello world')
           func(*args, **kwargs)
   
       return wrapper
   
   print("----------")
   print(run.__name__)
   print("----------")
   ```

   总结：

   1. 装饰器实际上就是一个函数
   2. 两个特别之处：参数是一个函数，返回值也必须是一个函数
   3. 内部定义的函数和外部传来的函数，参数列表这样写表示任何参数(*args, **kwargs)，否则无法适配参数不一的各种函数
   4. 需要使用functools.wraps在装饰器中的函数上把传进来的这个函数进行一个包裹，这样就不会丢失原来的函数的_name__等属性。

### 用装饰器做登录限制

1. 先创建一个decorators.py，里面专门存放装饰器代码：

   ```python
   from functools import wraps
   from flask import session, redirect, url_for
   
   
   # 限制登陆的装饰器
   def login_required(func):
       @wraps(func)
       def wrapper(*args, **kwargs):
           if session.get('user_id'):
               return func(*args, **kwargs)
           else:
               return redirect(url_for('login'))
   
       return wrapper
   ```

2. 在需要验证登录的视图函数之前加上该装饰器即可：

   ```python
   @app.route('/question/')
   @login_required
   def question():
       return render_template('question.html')
   ```

## 创建Question模型

models.py

```python
from datetime import datetime

from exts import db


class User(db.Model):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(11), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Question(db.Model):
    __table_name__ = 'question'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # now()表示服务器第一次运行的时间
    # now表示当前时间
    create_time = db.Column(db.DateTime, default=datetime.now)
    # 外键为user表中的id字段
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 按外键反转查找author信息，关系到User模型。然后反向引用得到该author的所有questions
    author = db.relationship('User', backref=db.backref('questions'))
```

manage.py

```python
from models import User, Question
```

命令：

迁移：python manage.py db migrate

更新：python manage.py db upgrade

## 完成首页

index视图函数

```python
@app.route('/')
def index():
    context = {
        # 按时间由近及远的顺序查找所有数据库中发布的问题
        'questions': Question.query.order_by('-create_time').all()
    }
    return render_template('index.html', **context)
```

index.html

```html
{% block main %}
    <ul class="question-ul">
        {% for question in questions %}
            <li class="question-li">
                <div class="avatar-group">
                    <img src="{{ url_for('static', filename='images/avatar.jpg') }}" alt=""
                         class="avatar">
                </div>
                <div class="question-group">
                    <p class="question-title"><a href="#">{{ question.title }}</a></p>
                    <p class="question-content">{{ question.content }}</p>
                    <div class="question-info">
                        <span class="question-author">{{ question.author.username }}</span>
                        <span class="question-date">{{ question.create_time }}</span>
                    </div>
                </div>
            </li>
        {% endfor %}
    </ul>
{% endblock %}
```

## 使用g对象以及钩子函数优化代码

优化方式是是使用g对象得到session数据，方便每个视图函数得到user。凡是需要得到session数据的视图函数都可以用到，即使是context_processor钩子函数也可以

```python
@app.route('/question/', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        if '' == title or '' == content:
            return '输入不能为空！'
        else:
            new_question = Question(title=title, content=content)
            # user_id = session.get('user_id')
            # user = User.query.filter(User.id == user_id).first()
            user = g.user
            new_question.author = user
            db.session.add(new_question)
            db.session.commit()
            return redirect(url_for('index'))


@app.route('/add_answer/', methods=['POST'])
@login_required
def add_answer():
    answer_content = request.form.get('answer_content')
    print(answer_content)
    question_id = request.form.get('question_id')

    answer = Answer(content=answer_content)
    # user_id = session['user_id']
    # user = User.query.filter(User.id == user_id).first()
    user = g.user
    answer.author = user
    question_model = Question.query.filter(Question.id == question_id).first()
    answer.question = question_model
    db.session.add(answer)
    db.session.commit()

    return redirect(url_for('detail', question_id=question_id))
    # question_model = Question.query.filter(Question.id == question_id).first()
    # return render_template('question_detail.html', question=question_model)

@app.context_processor
def my_context_processor():
    # user_id = session.get('user_id')
    # # 这是两种情况，其中一种没处理返回就报：TypeError: 'NoneType' object is not iterable
    # if user_id:
    #     user = User.query.filter(User.id == user_id).first()
    #     if user:
    #         return {'user': user}
    # return {}

    if hasattr(g, 'user'):
        return {'user': g.user}
    else:
        return {}


# 优化代码，用before_request和g对象避免重复劳动
@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user
```

## 优化密码设置加密

models.py

```python
class User(db.Model):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(11), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # 加密
    def __init__(self, *args, **kwargs):
        phone = kwargs.get('phone')
        username = kwargs.get('username')
        password = kwargs.get('password')

        self.phone = phone
        self.username = username
        # 截取密码之后加密，存入数据库
        self.password = generate_password_hash(password)

    # 解密, raw_password是用户输入的密码
    def check_password(self, raw_password):
        # self.password是数据库中存的加密的密码
        result = check_password_hash(self.password, raw_password)
        return result
```

login.py

```python
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        phone = request.form.get('phone')
        password = request.form.get('password')
        user = User.query.filter(User.phone == phone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            # 默认session一个月后过期，但是在配置文件中设置为了25天
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return '账号密码错误！'
```