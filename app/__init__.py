# !/usr/bin/env python
# coding: utf-8

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask.ext.redis import FlaskRedis
import pymysql
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@localhost:3306/movie"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.config["SECRET_KEY"] = 'd4cfac197bc2444c83a4273a524d5827'  #定义csrf保护字段，否则会报错
app.config['REDIS_URL'] = "redis://127.0.0.1:6379/0"  # 定义Redis 路径
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads/') # 创建目录用来保存上传的文件和图片
app.config['FC_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/") # 会员头像
app.debug = True
db = SQLAlchemy(app)
rd = FlaskRedis(app) # 创建Redis 对象


from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")


# 地址输入有误的404错误处理
@app.errorhandler(404)
def page_not_found(error):
	return render_template('home/404.html'), 404