import random
import redis
from redis.exceptions import RedisError
from redis import ConnectionPool
import pymysql
from pymysql import Error
from dbutils.pooled_db import PooledDB
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MysqlUtils:
    def __init__(self, host='localhost', port=3306, user='root',
                 password=None, database=None, charset='utf8mb4',
                 max_connections=10, min_connections=1):
        """
        初始化MySQL连接池

        Args:
            host: 数据库主机地址
            port: 数据库端口
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名
            charset: 字符集
            max_connections: 最大连接数
            min_connections: 最小连接数
        """
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': charset,
            'cursorclass': pymysql.cursors.DictCursor
        }

        # 创建连接池
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=max_connections,
            mincached=min_connections,
            blocking=True,  # 连接数达到最大时是否等待
            **self.config
        )

    def get_connection(self):
        """从连接池获取连接"""
        return self.pool.connection()

    @contextmanager
    def get_cursor(self, connection=None):
        """
        获取游标的上下文管理器
        可以自动处理连接的获取和释放
        """
        close_conn = False
        if connection is None:
            connection = self.get_connection()
            close_conn = True

        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
            if close_conn:
                connection.close()

    def execute_query(self, sql, params=None, fetch_one=False):
        """
        执行查询语句

        Args:
            sql: SQL语句
            params: 参数列表或字典
            fetch_one: 是否只获取一条记录

        Returns:
            查询结果列表或单条记录
        """
        with self.get_cursor() as cursor:
            try:
                cursor.execute(sql, params or ())
                if fetch_one:
                    return cursor.fetchone()
                return cursor.fetchall()
            except Error as e:
                logger.error(f"Error executing query: {e}, SQL: {sql}")
                raise

    def execute_update(self, sql, params=None):
        """
        执行更新语句（INSERT, UPDATE, DELETE）

        Args:
            sql: SQL语句
            params: 参数列表或字典

        Returns:
            影响的行数
        """
        with self.get_cursor() as cursor:
            try:
                cursor.execute(sql, params or ())
                return cursor.rowcount
            except Error as e:
                logger.error(f"Error executing update: {e}, SQL: {sql}")
                raise

    def insert(self, table, data):
        """
        插入单条数据

        Args:
            table: 表名
            data: 数据字典

        Returns:
            插入的行数
        """
        if not data:
            return 0

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        return self.execute_update(sql, tuple(data.values()))

    def batch_insert(self, table, data_list):
        """
        批量插入数据

        Args:
            table: 表名
            data_list: 数据字典列表

        Returns:
            插入的行数
        """
        if not data_list:
            return 0

        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['%s'] * len(data_list[0]))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        values = [tuple(data.values()) for data in data_list]

        with self.get_cursor() as cursor:
            try:
                cursor.executemany(sql, values)
                return cursor.rowcount
            except Error as e:
                logger.error(f"Error batch inserting: {e}")
                raise

    def update(self, table, data, condition=None, condition_params=None):
        """
        更新数据

        Args:
            table: 表名
            data: 更新数据字典
            condition: WHERE条件语句
            condition_params: WHERE条件参数

        Returns:
            影响的行数
        """
        if not data:
            return 0

        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        params = list(data.values())

        sql = f"UPDATE {table} SET {set_clause}"
        if condition:
            sql += f" WHERE {condition}"
            if condition_params:
                if isinstance(condition_params, (list, tuple)):
                    params.extend(condition_params)
                else:
                    params.append(condition_params)

        return self.execute_update(sql, params)

    def delete(self, table, condition=None, params=None):
        """
        删除数据

        Args:
            table: 表名
            condition: WHERE条件语句
            params: WHERE条件参数

        Returns:
            删除的行数
        """
        sql = f"DELETE FROM {table}"
        if condition:
            sql += f" WHERE {condition}"

        return self.execute_update(sql, params)

    def select(self, table, columns='*', condition=None, params=None,
               order_by=None, limit=None, offset=None, fetch_one=False):
        """
        查询数据

        Args:
            table: 表名
            columns: 查询的列
            condition: WHERE条件语句
            params: WHERE条件参数
            order_by: 排序
            limit: 限制条数
            offset: 偏移量
            fetch_one: 是否只获取一条记录

        Returns:
            查询结果
        """
        if isinstance(columns, (list, tuple)):
            columns = ', '.join(columns)

        sql = f"SELECT {columns} FROM {table}"

        if condition:
            sql += f" WHERE {condition}"

        if order_by:
            sql += f" ORDER BY {order_by}"

        if limit is not None:
            sql += f" LIMIT {limit}"
            if offset is not None:
                sql += f" OFFSET {offset}"

        return self.execute_query(sql, params, fetch_one)

    def get_by_id(self, table, id_value, id_column='id'):
        """
        根据ID获取单条记录

        Args:
            table: 表名
            id_value: ID值
            id_column: ID列名，默认为'id'

        Returns:
            单条记录或None
        """
        sql = f"SELECT * FROM {table} WHERE {id_column} = %s"
        return self.execute_query(sql, (id_value,), fetch_one=True)

    def exists(self, table, condition, params=None):
        """
        检查记录是否存在

        Args:
            table: 表名
            condition: WHERE条件语句
            params: WHERE条件参数

        Returns:
            bool: 是否存在
        """
        sql = f"SELECT 1 FROM {table} WHERE {condition} LIMIT 1"
        result = self.execute_query(sql, params, fetch_one=True)
        return result is not None

    def count(self, table, condition=None, params=None):
        """
        统计记录数

        Args:
            table: 表名
            condition: WHERE条件语句
            params: WHERE条件参数

        Returns:
            int: 记录数
        """
        sql = f"SELECT COUNT(*) as count FROM {table}"
        if condition:
            sql += f" WHERE {condition}"

        result = self.execute_query(sql, params, fetch_one=True)
        return result['count'] if result else 0

    def execute_transaction(self, operations):
        """
        执行事务操作

        Args:
            operations: 操作列表，每个元素为(sql, params)元组

        Returns:
            bool: 是否成功
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            for sql, params in operations:
                cursor.execute(sql, params or ())
            conn.commit()
            return True
        except Error as e:
            conn.rollback()
            logger.error(f"Transaction error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_table_info(self, table):
        """
        获取表结构信息

        Args:
            table: 表名

        Returns:
            表结构信息列表
        """
        sql = f"DESCRIBE {table}"
        return self.execute_query(sql)

    def create_table(self, table, columns_def):
        """
        创建表

        Args:
            table: 表名
            columns_def: 列定义字符串
        """
        sql = f"CREATE TABLE IF NOT EXISTS {table} ({columns_def})"
        return self.execute_update(sql)

    def drop_table(self, table):
        """
        删除表

        Args:
            table: 表名
        """
        sql = f"DROP TABLE IF EXISTS {table}"
        return self.execute_update(sql)

    def execute_raw_sql(self, sql, params=None, fetch_one=False):
        """
        执行原始SQL语句

        Args:
            sql: SQL语句
            params: 参数
            fetch_one: 是否只获取一条记录

        Returns:
            查询结果或影响的行数
        """
        sql_upper = sql.strip().upper()
        if sql_upper.startswith('SELECT'):
            return self.execute_query(sql, params, fetch_one)
        else:
            return self.execute_update(sql, params)

    def close_pool(self):
        """关闭连接池"""
        if hasattr(self, 'pool'):
            self.pool.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_pool()


class RedisUtils:
    def __init__(self, host='localhost', port=6379, db=0, password=None, max_connections=10):
        # 创建 Redis 连接池
        self.pool = ConnectionPool(host=host, port=port, db=db, password=password, max_connections=max_connections)

    def get_connection(self):
        return redis.Redis(connection_pool=self.pool)

    def get(self, key):
        conn = self.get_connection()
        try:
            value = conn.get(key)
            return value
        except RedisError as e:
            print(f"Error accessing Redis: {e}")
            return None
        finally:
            conn.close()

    def set(self, key, value, ex=None, px=None, nx=False, xx=False):
        conn = self.get_connection()
        try:
            conn.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            return True
        except RedisError as e:
            print(f"Error setting value in Redis: {e}")
            return False
        finally:
            conn.close()

    def hget(self, table, key):
        conn = self.get_connection()
        try:
            value = conn.hget(table, key)
            return value
        except RedisError as e:
            print(f"Error accessing Redis: {e}")
            return None
        finally:
            conn.close()

    def hset(self, table, key, value):
        conn = self.get_connection()
        try:
            conn.hset(table, key, value)
            return True
        except RedisError as e:
            print(f"Error setting value in Redis: {e}")
            return False
        finally:
            conn.close()

    def hdel(self, table, key):
        conn = self.get_connection()
        try:
            conn.hdel(table, key)
            return True
        except RedisError as e:
            print(f"Error setting value in Redis: {e}")
            return False
        finally:
            conn.close()

    def delete(self, key):
        conn = self.get_connection()
        try:
            conn.delete(key)
            return True
        except RedisError as e:
            print(f"Error deleting key from Redis: {e}")
            return False
        finally:
            conn.close()

    def expire(self, key, cache_time):
        conn = self.get_connection()
        try:
            # conn.delete(key)
            conn.expire(key, cache_time)
            return True
        except RedisError as e:
            print(f"Error deleting key from Redis: {e}")
            return False
        finally:
            conn.close()

    def llen(self, key):
        conn = self.get_connection()
        try:
            return conn.llen(key)
        except RedisError as e:
            print(f"Error accessing Redis: {e}")
            return 0

    def sadd(self, key, *values):
        """向Set中添加一个或多个成员"""
        conn = self.get_connection()
        try:
            conn.sadd(key, *values)
            return True
        except RedisError as e:
            print(f"Error adding to set in Redis: {e}")
            return False
        finally:
            conn.close()

    def set_expire(self, key, seconds):
        conn = self.get_connection()
        try:
            conn.expire(key, seconds)
            return True
        except RedisError as e:
            print(f"Error deleting key from Redis: {e}")
            return False

    def rpush(self, key, *values):
        """从列表右端添加一个或多个值"""
        conn = self.get_connection()
        try:
            conn.rpush(key, *values)
            return True
        except RedisError as e:
            print(f"Error pushing to list in Redis: {e}")
            return False
        finally:
            conn.close()

    def lpop(self, key):
        """从列表左端弹出一个值"""
        conn = self.get_connection()
        try:
            return conn.lpop(key)
        except RedisError as e:
            print(f"Error popping from list in Redis: {e}")
            return None
        finally:
            conn.close()

    def get_random_hash(self, table, key):
        """随机获取hash表种key值"""
        conn = self.get_connection()
        try:
            all_keys = conn.keys(f'{table}:*')
            if not all_keys:
                return None, None, None

            random_key = random.choice(all_keys)

            value = conn.hget(random_key, key)

            return len(all_keys), random_key.decode('utf-8'), value.decode('utf-8')

        except RedisError as e:
            print(f"Error accessing Redis: {e}")
            return None, None, None

    # 新增需要的方法
    def lrange(self, key, start, end):
        """获取列表指定范围内的元素"""
        conn = self.get_connection()
        try:
            return conn.lrange(key, start, end)
        except RedisError as e:
            print(f"Error accessing Redis: {e}")
            return []
        finally:
            conn.close()

    def lrem(self, key, count, value):
        """从列表中删除元素"""
        conn = self.get_connection()
        try:
            return conn.lrem(key, count, value)
        except RedisError as e:
            print(f"Error removing from list in Redis: {e}")
            return 0
        finally:
            conn.close()

    def exists(self, key):
        """检查键是否存在"""
        conn = self.get_connection()
        try:
            return conn.exists(key)
        except RedisError as e:
            print(f"Error checking key existence in Redis: {e}")
            return False
        finally:
            conn.close()

    def get_all_keys(self, pattern):
        """获取匹配模式的所有键"""
        with self.get_connection() as conn:
            try:
                keys = conn.keys(pattern)
                return [k.decode('utf-8') for k in keys] if keys else []
            except RedisError as e:
                print(f"Error getting keys from Redis: {e}")
                return []
            finally:
                conn.close()
