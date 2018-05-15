from flask import Flask, render_template, request, redirect, url_for, session, g
from sqlalchemy import or_

import config
from decorators import login_required
from exts import db
from models import User, Question, Answer

app = Flask(__name__)
app.config.from_object(config)

# 不要忘记初始化
db.init_app(app)


@app.route('/')
def index():
    context = {
        # 按时间由近及远的顺序查找所有数据库中发布的问题
        'questions': Question.query.order_by('-create_time').all()
    }
    return render_template('index.html', **context)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if password1 == password2:
            phone = request.form.get('phone')
            username = request.form.get('username')
            user = User.query.filter(User.phone == phone).first()
            if user:
                return '手机号已被注册'
            else:
                user = User(phone=phone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
        else:
            return '两次密码不一致！'


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


@app.route('/logout/')
def logout():
    # 设置第二个参数后，即使user_id不存在也不会出现Key_Error
    session.pop('user_id', None)
    # session.clear
    # del session['user_id']
    return redirect(url_for('login'))


# 视图函数里面的参数别忘记了
@app.route('/detail/<question_id>/')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('question_detail.html', question=question_model)


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


@app.route('/search/')
def search():
    q = request.args.get('q')
    # 查询或
    search_questions = Question.query.filter(
        or_(Question.title.contains(q), Question.content.contains(q))).order_by(
        '-create_time').all()
    # 查询与
    # Question.query.filter(Question.title.contains(q), Question.content.contains(q))

    return render_template('index.html', questions=search_questions)


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


if __name__ == '__main__':
    app.run()
