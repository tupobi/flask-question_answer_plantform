from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from exts import db


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


class Answer(db.Model):
    __table_name__ = 'answer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # db.Text db.Integer首字母大写，否则报错！！
    content = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_time = db.Column(db.DateTime, default=datetime.now)

    question = db.relationship('Question',
                               backref=db.backref('answers', order_by=create_time.desc()))
    author = db.relationship('User', backref=db.backref('answers'))
