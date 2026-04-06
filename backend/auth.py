from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

from configs import MysqlConfig
from sql.sql_tools import MysqlUtils

# 初始化用户管理
login_manager = LoginManager()
login_manager.login_view = '/login'


@login_manager.unauthorized_handler
def unauthorized_callback():
    # return JSON 401 rather than redirect to a login page
    from flask import jsonify
    return jsonify({'error': 'authentication required'}), 401


class User(UserMixin):
    def __init__(self, id_, username, password_hash, role='user'):
        self.id = id_
        self.username = username
        self.password_hash = password_hash
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# helper functions

def ensure_user_role_column(db: MysqlUtils):
    try:
        row = db.execute_query("SHOW COLUMNS FROM users LIKE 'role'", fetch_one=True)
        if not row:
            db.execute_update("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'")
    except Exception as e:
        # 如果用户表不存在或查询失败，则让后续逻辑继续处理
        pass


def init_user_table():
    db = MysqlUtils(host=MysqlConfig.host, port=MysqlConfig.port,
                    user=MysqlConfig.user, password=MysqlConfig.password,
                    database=MysqlConfig.database, charset=MysqlConfig.charset)
    ensure_user_role_column(db)
    # create default admin if none exists
    existing_admin = db.select('users', '*', condition='username=%s', params=('admin',), fetch_one=True)
    if not existing_admin:
        pwd = generate_password_hash('admin')
        db.insert('users', {'username': 'admin', 'password': pwd, 'role': 'admin'})
    elif existing_admin.get('role') != 'admin':
        db.update('users', {'role': 'admin'}, condition='username=%s', condition_params=('admin',))
    db.close()


def register_user(username, password):
    db = MysqlUtils(host=MysqlConfig.host, port=MysqlConfig.port,
                    user=MysqlConfig.user, password=MysqlConfig.password,
                    database=MysqlConfig.database, charset=MysqlConfig.charset)
    ensure_user_role_column(db)
    # check if user exists
    existing = db.select('users', '*', condition='username=%s', params=(username,), fetch_one=True)
    if existing:
        db.close()
        return False, '用户名已存在'
    # create user
    pwd_hash = generate_password_hash(password)
    db.insert('users', {'username': username, 'password': pwd_hash, 'role': 'user'})
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
        return User(row['id'], row['username'], row['password'], row.get('role', 'user'))
    return None
