from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

from .configs import MysqlConfig
from .sql.sql_tools import MysqlUtils

# 初始化用户管理
login_manager = LoginManager()
login_manager.login_view = '/login'


@login_manager.unauthorized_handler
def unauthorized_callback():
    # return JSON 401 rather than redirect to a login page
    from flask import jsonify
    return jsonify({'error': 'authentication required'}), 401


class User(UserMixin):
    def __init__(self, id_, username, password_hash):
        self.id = id_
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# helper functions

def init_user_table():
    db = MysqlUtils(host=MysqlConfig.host, port=MysqlConfig.port,
                    user=MysqlConfig.user, password=MysqlConfig.password,
                    database=MysqlConfig.database, charset=MysqlConfig.charset)
    # create default admin if none exists
    if db.count('users') == 0:
        pwd = generate_password_hash('admin')
        db.insert('users', {'username': 'admin', 'password': pwd})
    db.close()


def register_user(username, password):
    db = MysqlUtils(host=MysqlConfig.host, port=MysqlConfig.port,
                    user=MysqlConfig.user, password=MysqlConfig.password,
                    database=MysqlConfig.database, charset=MysqlConfig.charset)
    # check if user exists
    existing = db.select('users', '*', condition='username=%s', params=(username,), fetch_one=True)
    if existing:
        db.close()
        return False, '用户名已存在'
    # create user
    pwd_hash = generate_password_hash(password)
    db.insert('users', {'username': username, 'password': pwd_hash})
    db.close()
    return True, '注册成功'


@login_manager.user_loader
def load_user(user_id):
    db = MysqlUtils(host=MysqlConfig.host, port=MysqlConfig.port,
                    user=MysqlConfig.user, password=MysqlConfig.password,
                    database=MysqlConfig.database, charset=MysqlConfig.charset)
    row = db.select('users', '*', condition='id=%s', params=(user_id,), fetch_one=True)
    db.close()
    if row:
        return User(row['id'], row['username'], row['password'])
    return None
