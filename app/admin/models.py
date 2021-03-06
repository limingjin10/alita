from inc import db
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import func
from flask_login import UserMixin
from sqlalchemy import (Column, Integer, String, DateTime, Date, ForeignKey,
                        SmallInteger, Text, Float, TEXT)
from inc.cached import cached
from app.admin import rc

role2permission = db.Table(
    'role2permission',
    Column('role_id', Integer, ForeignKey('role.id')),
    Column('permission_id', Integer, ForeignKey('permission.id')),
    info={'bind_key': 'alita_admin'}
)


class Manager(db.Model, UserMixin):
    __bind_key__ = "alita_admin"
    __tablename__ = "manager"
    __table_args__ = {"useexisting":True, "mysql_charset":"utf8", "mysql_engine":"InnoDB"}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(32), unique=True, nullable=False, doc=u"")
    password = Column("password", String(128), nullable=True, doc=u"")
    language = Column("language", String(10), nullable=True, doc="浏览页面使用的语言")
    avatar = Column("avatar", String(256), nullable=True, doc="头像")
    update_time = Column("update_time", DateTime, default=func.now(), onupdate=func.now())
    create_time = Column("create_time", DateTime, default=func.now())
    state = Column("state", mysql.TINYINT(display_width=1), nullable=False, default=1, doc=u"0:invalid,1:valid")
    role_id = Column('role_id', Integer, ForeignKey('role.id'))

    def __repr__(self):
        return '<Manager %s,%s>' % (self.id, self.name)

    @property
    def state_cn(self):
        return ('invalid', 'valid', 'deleted')[self.state]

    @property
    def alerts(self):
        return Alert.gets_by_id(self.id)

    @classmethod
    def get(cls, _id):
        return db.session.query(Manager).filter(Manager.id==_id).first()


class Role(db.Model):
    __bind_key__ = 'alita_admin'
    __tablename__ = 'role'
    __table_args__ = {"useexisting":True, 'mysql_charset':'utf8mb4', 'mysql_engine':'InnoDB'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    en_name = Column("en_name", String(45), nullable=False, unique=True, default="", doc=u"")
    name = Column("name", String(45), nullable=False, unique=True, default="", doc=u"")
    description = Column("description", String(255), nullable=True, default="", doc=u"")
    routes = Column("routes", Text, nullable=True, default="", doc=u"page routes")

    managers = db.relationship('Manager', backref='role')
    permissions = db.relationship('Permission', secondary=role2permission, backref='roles')


class Permission(db.Model):
    __bind_key__ = 'alita_admin'
    __tablename__ = 'permission'
    __table_args__ = {"useexisting":True, 'mysql_charset':'utf8mb4', 'mysql_engine':'InnoDB'}

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(45), nullable=False, default="", doc=u"")
    method = Column("method", String(45), nullable=True, default="", doc=u"method")
    uri = Column("uri", String(128), nullable=True, default="", doc=u"page uri")


class AdminLog(db.Model):
    __bind_key__ = "alita_admin"
    __tablename__ = "admin_log"
    __table_args__ = {"useexisting":True, "mysql_charset":"utf8", "mysql_engine":"InnoDB"}

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    title = Column('title', String(32), nullable=False, doc=u"")
    info = Column('info', Text(20000), nullable=True, doc=u"")
    create_time = Column('create_time', DateTime, default=func.now())
    creator_id = Column('creator_id', Integer, nullable=False, doc=u"manager id")
    state = Column('state', mysql.TINYINT(display_width=1), nullable=False, default=1, doc=u"")

    def __repr__(self):
        return '<admin_log %s,%s>' % (self.id, self.title)


class Alert(db.Model):
    __bind_key__ = "alita_admin"
    __tablename__ = "admin_alert"
    __table_args__ = {"useexisting":True, "mysql_charset":"utf8", "mysql_engine":"InnoDB"}

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    manager_id = Column('manager_id', Integer, nullable=False)
    content = Column('content', String(64), nullable=False, doc="")
    create_time = Column('create_time', DateTime, default=func.now())
    state = Column('state', mysql.TINYINT(display_width=1), nullable=False, default=1, doc="0:invalid 1:unread 2:readed")
    
    @classmethod
    @cached('%s:alert:%s' % (Manager.__tablename__, '{_id}'), rc, 3600)
    def gets_by_id(self, _id):
        return Alert.query.filter_by(manager_id=_id, state=1).all()
