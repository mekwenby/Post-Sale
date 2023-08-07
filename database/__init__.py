import os
import time

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, IntegerField, BooleanField, AutoField, fn, chunked
from peewee import MySQLDatabase

""" 使用sqlite数据库 """
db = SqliteDatabase('sqlite.db')  # 连接sqlite数据库

""" 使用Mysql"""


# db = MySQLDatabase(host='db', port=3306, user='root', passwd='passwd', database='Web')


class BaseModel(Model):
    class Meta:
        database = db


class Problem(BaseModel):
    """
    工单
    """
    id = AutoField(primary_key=True)
    rid = CharField(index=True)
    establish_id = CharField(null=True, index=True)
    project_name = CharField(null=True)
    user_name = CharField(null=True)
    module = CharField()
    ptype = CharField()
    text = CharField(max_length=1024, null=True)
    generate_time = IntegerField(default=lambda: int(time.time()))
    solve_time = IntegerField(null=True)
    solve_name = CharField(null=True)
    """
    submit 提交标签
    solve  处理标签
    """
    submit = BooleanField(default=True)
    solve = CharField(default='待处理')


class ProblemAtt(BaseModel):
    """ 附件
    rid :               关联表单rid
    ip_time :           上传时间
    filename:           文件名
    *path :              static/upload/rid/filename
    """
    id = AutoField(primary_key=True)
    rid = CharField(index=True)
    up_time = IntegerField(default=lambda: int(time.time()))
    up_name = CharField(default='Infinite')
    filename = CharField(null=False)


class ProblemMessage(BaseModel):
    """
    工单消息
    """
    id = AutoField(primary_key=True)
    problem = ForeignKeyField(Problem, backref='Message')
    up_time = IntegerField(default=lambda: int(time.time()))
    type = CharField(default='text')
    source = CharField(default='user')
    text = CharField()
    author = CharField(default='system')


class User(BaseModel):
    """
    用户
    uid :               跳转页传标识
    u_token :           cookie
    """
    id = AutoField(primary_key=True)
    uid = CharField(index=True)
    u_token = CharField(null=True, index=True)


class ManageUser(BaseModel):
    """
    管理员用户
    name :              姓名|登录名
    passwd :            登录密码|MD5
    m_token :           cookie
    """
    id = AutoField(primary_key=True)
    name = CharField()
    passwd = CharField()
    m_token = CharField(default='0', index=True)


def create_table():
    """
    创建表
    """
    db.connect()
    db.create_tables([Problem, ProblemAtt, User, ManageUser, ProblemMessage], safe=True)
    # 创建默认管理员
    ManageUser.create(name='超管', passwd='123456')
    db.close()


def recover():
    """清空数据库"""
    db.drop_tables([Problem, ProblemAtt, User, ManageUser, ProblemMessage])
    db.close()
    create_table()
