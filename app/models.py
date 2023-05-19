
# coding: utf-8

'''
added at 2017-10-6. 添加用户、管理员、电影等各个模型的定义
'''

from datetime import datetime
from app import db

#add test git

# 定义用户信息
class User(db.Model):
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	pwd = db.Column(db.String(128))
	email = db.Column(db.String(64), unique=True)
	phone = db.Column(db.String(11), unique=True)
	info = db.Column(db.Text()) # 个人简介
	face = db.Column(db.String(255), unique=True) # 头像信息
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) # 用户注册时间(使用utcnow属性可能导致时间不准确)
	uuid = db.Column(db.String(128), unique=True) # 用户唯一标志符
	userlogs = db.relationship('Userlog', backref='user') # 定义用户登录日志的外键关联关系
	comment = db.relationship('Comment', backref='user') # 定义电影评论的外键关联关系
	moviecols = db.relationship('Moviecol', backref='user') # 定义电影收藏的外键关联关系

	def __repr__(self):
		return "<User {}>".format(self.name)


	# 验证输入密码是否正确
	def check_pwd(self, pwd):
		from werkzeug.security import check_password_hash
		return check_password_hash(self.pwd, pwd)


# 用户登录日志
class Userlog(db.Model):
	__tablename__ = 'userlog'
	id = db.Column(db.Integer, primary_key=True) # 用户编号	
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # 关联的用户
	ip = db.Column(db.String(64)) # 登录的IP
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) # 登录时间

	def __repr__(self):
		return "<Userlog {}>".format(self.id)


# 定义用户权限	
class Auth(db.Model):
	__tablename__ = 'auth'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	url = db.Column(db.String(255), unique=True) # 权限路由规则的地址
	addtime = db.Column(db.DateTime, index=True, default=datetime.now)

	def __repr__(self):
		return '<Auth {}>'.format(self.name)


# 定义用户角色
class Role(db.Model):
	__tablename__ = 'role'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	auths = db.Column(db.String(512)) # 该角色所拥有的权限列表
	addtime = db.Column(db.DateTime, index=True, default=datetime.now)
	admins = db.relationship('Admin', backref='role') # 定义管理员的外键关联关系

	def __repr__(self):
		return '<Role {}>'.format(self.name)


# 定义管理员信息
class Admin(db.Model):
	__tablename__ = 'admin'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	pwd = db.Column(db.String(128))
	is_super = db.Column(db.SmallInteger) # 是否为超级管理员
	role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
	addtime = db.Column(db.DateTime, index=True, default=datetime.now)
	adminlogs = db.relationship('Adminlog', backref='admin') # 定义管理员登录日志的外键关联关系
	oplogs = db.relationship('Oplog', backref='admin') # 定义管理员操作日志的外键关联关系

	def __repr__(self):
		return '<Admin {}>'.format(self.name)


	# 验证输入密码是否正确
	def check_pwd(self, pwd):
		from werkzeug.security import check_password_hash
		return check_password_hash(self.pwd, pwd)


# 管理员登录日志
class Adminlog(db.Model):
	__tablename__ = 'adminlog'
	id = db.Column(db.Integer, primary_key=True) 
	admin_id = db.Column(db.Integer, db.ForeignKey('admin.id')) # 关联的管理员
	ip = db.Column(db.String(64)) # 登录的IP
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) # 登录时间

	def __repr__(self):
		return "<Adminlog {}>".format(self.id)


# 操作日志Operationlog
class Oplog(db.Model):
	__tablename__ = 'oplog'
	id = db.Column(db.Integer, primary_key=True) 
	admin_id = db.Column(db.Integer, db.ForeignKey('admin.id')) # 关联的管理员
	ip = db.Column(db.String(64)) # 登录的IP
	reason = db.Column(db.String(512))
	addtime = db.Column(db.DateTime, index=True, default=datetime.now) # 登录时间

	def __repr__(self):
		return "<Oplog {}>".format(self.id)


# 电影标签，用于索引电影
class Tag(db.Model):
	__tablename__ = 'tag'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	addtime = db.Column(db.DateTime, index=True, default=datetime.now)
	movie = db.relationship('Movie', backref='tag')

	def __repr__(self):
		return '<Tag {}>'.format(self.name)


# 定义电影的各种信息
class Movie(db.Model):
	__tablename__ = "movie"
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(64), unique=True) # 标题
	url = db.Column(db.String(255), unique=True) # 电影播放地址
	info = db.Column(db.Text()) # 电影简介	
	logo = db.Column(db.String(255), unique=True) # 电影封面
	star = db.Column(db.SmallInteger) # 评分
	playnum = db.Column(db.BigInteger) # 播放量
	commentnum = db.Column(db.BigInteger) # 评论量
	tag_id = db.Column(db.Integer, db.ForeignKey('tag.id')) # 电影所属标签，与Tag表关联	
	area = db.Column(db.String(64)) # 上映地区
	release_time = db.Column(db.Date) # 上映时间
	length = db.Column(db.String(64)) # 播放时间
	addtime = db.Column(db.DateTime, index=True, default=datetime.now)
	comment = db.relationship('Comment', backref='movie') # 定义电影评论的外键关联关系
	moviecols = db.relationship('Moviecol', backref='movie') # 定义电影收藏的外键关联关系

	def __repr__(self):
		return "<Movie {}>".format(self.title)


# 上映预告
class Preview(db.Model):
	__tablename__ = "preview"
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(64), unique=True)
	logo = db.Column(db.String(255), unique=True)
	addtime = db.Column(db.DateTime, index=True, default=datetime.now)

	def __repr__(self):
		return "<Preview {}>".format(self.title)


# 定义评论信息
class Comment(db.Model):
	__tablename__ = 'comment'
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text()) # 评论内容	
	movie_id = db.Column(db.Integer, db.ForeignKey('movie.id')) # 关联电影
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # 关联用户
	addtime = db.Column(db.DateTime, index=True, default=datetime.now)

	def __repr__(self):
		return "<Comment {}>".format(self.id)


# 定义电影收藏信息
class Moviecol(db.Model):
	__tablename__ = 'moviecol'
	id = db.Column(db.Integer, primary_key=True)
	movie_id = db.Column(db.Integer, db.ForeignKey('movie.id')) # 关联电影
	user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # 关联用户
	addtime = db.Column(db.DateTime, index=True, default=datetime.now)

	def __repr__(self):
		return "<Moviecol {}>".format(self.id)

