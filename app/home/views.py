# !/usr/bin/env python
# coding: utf-8

from . import home
from flask import render_template, redirect, url_for, flash, request, session
from app.home.forms import RegistForm, LoginForm, UserProfileForm, PwdForm, CommentForm
from app.models import User, Userlog, Preview, Tag, Movie, Comment, Moviecol
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import uuid
import os
import datetime
from app import db, app


# 定义用户访问控制装饰器，可以从flask导入login_required实现相同功能
def user_login_req(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'user' not in session:
			return redirect(url_for('home.login', next=request.url))
		return f(*args, **kwargs)

	return decorated_function


# 修改上传的文件名
def change_filename(filename):
	fileinfo = os.path.splitext(filename)
	filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S')+str(uuid.uuid4().hex)+fileinfo[-1]
	return filename


# 根据标签筛选电影
@home.route("/<int:page>/", methods=["GET"])
@home.route("/", methods=["GET"])
def index(page=None):
    tags = Tag.query.all()
    page_data = Movie.query
    # 标签
    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    # 星级
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    # 时间
    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()  # 这里可以用release_time
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )
    # 播放量
    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(
                Movie.playnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.playnum.asc()
            )
    # 评论量
    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(
                Movie.commentnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.commentnum.asc()
            )
    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=8)
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )
    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)


# 预告管理只显示5张，存入数据库时id可能不是1-5顺序存入，会出现大于5 的id，导致图片轮播不正常
# 需要考虑添加预告时id 的判断，最多添加5张预告，并且删除预告添加新预告时，id做替换，而不是累加
# 其他table 也是一样的问题
@home.route('/animation/')
def animation():
	data = Preview.query.all()
	return render_template('home/animation.html',data=data)


@home.route('/login/', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		data = form.data
		user = User.query.filter_by(name=data['name']).first()
		if not user.check_pwd(data['pwd']):
			flash('密码错误！','err')
			return redirect(url_for('home.login'))
		session['user'] = user.name
		session['user_id'] = user.id

		userlog = Userlog(
			user_id = user.id,
			ip = request.remote_addr
		)
		db.session.add(userlog)
		db.session.commit()
		return redirect(url_for('home.user'))
	return render_template('home/login.html', form=form)


@home.route('/logout/')
@user_login_req
def logout():
	session.pop('user', None)
	session.pop('user_id', None)
	return redirect(url_for('home.login'))


@home.route('/register/', methods=['GET','POST'])
def register():
	form = RegistForm()
	if form.validate_on_submit():
		data = form.data
		user = User(
			name = data['name'],
			email = data['email'],
			phone = data['phone'],
			pwd = generate_password_hash(data['pwd']),
			uuid = uuid.uuid4().hex
		)
		db.session.add(user)
		db.session.commit()
		flash('注册成功！', 'ok')
		return redirect(url_for('home.login'))
	return render_template('home/register.html', form=form)


# 修改资料
@home.route('/user/', methods=['GET','POST'])
@user_login_req
def user():
	form = UserProfileForm()
	user = User.query.get_or_404(int(session['user_id']))
	form.face.validators = []
	if request.method == 'GET':
		form.name.data = user.name
		form.email.data = user.email
		form.phone.data = user.phone
		form.info.data = user.info

	if form.validate_on_submit():
		data = form.data
		file_face = secure_filename(form.face.data.filename)
		if not os.path.exists(app.config['FC_DIR']):
			os.makedirs(app.config['FC_DIR'])
			os.chmod(app.config['FC_DIR'], 'rw')		
		user.face = change_filename(file_face)
		form.face.data.save(app.config['FC_DIR'] + user.face)

		name_count = User.query.filter_by(name=data['name']).count()
		if data['name'] != user.name and name_count == 1:
			flash('昵称已经存在！', 'err')
			return redirect(url_for('home.user'))

		email_count = User.query.filter_by(email=data['email']).count()
		if data['email'] != user.email and email_count == 1:
			flash('邮箱已经存在！', 'err')
			return redirect(url_for('home.user'))

		phone_count = User.query.filter_by(phone=data['phone']).count()
		if data['phone'] != user.phone and phone_count == 1:
			flash('手机号码已经存在！', 'err')
			return redirect(url_for('home.user'))

		user.name = data['name']
		user.email = data['email']
		user.phone = data['phone']
		user.info = data['info']
		db.session.add(user)
		db.session.commit()
		flash('修改成功！','ok')
		return redirect(url_for('home.user'))

	return render_template('home/user.html', form=form, user=user)


@home.route('/pwd/', methods=['GET','POST'])
@user_login_req
def pwd():
	form = PwdForm()
	if form.validate_on_submit():
		data = form.data
		user = User.query.filter_by(name=session['user']).first()
		if not user.check_pwd(data['old_pwd']):
			flash('旧密码错误！','err')
			return redirect(url_for('home.pwd'))
		user.pwd = generate_password_hash(data['new_pwd'])
		db.session.add(user)
		db.session.commit()
		flash('修改密码成功，请重新登录！', 'ok')
		return redirect(url_for('home.logout'))
	return render_template('home/pwd.html', form=form)


@home.route('/comments/<int:page>/')
@user_login_req
def comments(page=None):
	if page is None:
		page = 1
	page_data = Comment.query.join(
		Movie
	).join(
		User
	).filter(
		Movie.id == Comment.movie_id,
		User.id == session['user_id']
	).order_by(
		Comment.addtime.desc()
	).paginate(page=page, per_page=10)

	return render_template('home/comments.html', page_data=page_data)


@home.route('/loginlog/<int:page>/', methods=['GET'])
@user_login_req
def loginlog(page=None):
	if page is None:
		page = 1
	page_data = Userlog.query.filter_by(
		user_id=int(session['user_id'])
	).order_by(
		Userlog.addtime.desc()
	).paginate(page=page, per_page=2)
	return render_template('home/loginlog.html', page_data=page_data)


# play.html页面中点击收藏，添加到数据库moviecol表中
@home.route('/moviecol/add/', methods=['GET', 'POST'])
@user_login_req
def moviecol_add():
	uid = request.args.get("uid", "")
	mid = request.args.get("mid", "")
	moviecol = Moviecol.query.filter_by(
		user_id=int(uid),
		movie_id=int(mid)
	).count()
	if moviecol == 1:
		data = dict(ok=0)

	if moviecol == 0:
		moviecol = Moviecol(
			user_id=int(uid),
			movie_id=int(mid)
		)
		db.session.add(moviecol)
		db.session.commit()
		data = dict(ok=1)
	import json
	return json.dumps(data)


@home.route('/moviecol/<int:page>/')
@user_login_req
def moviecol(page=None):
	if page is None:
		page = 1

	page_data = Moviecol.query.join(
		Movie
	).join(
		User
	).filter(
		Movie.id == Moviecol.movie_id,
		User.id == session['user_id']
	).order_by(
		Moviecol.addtime.desc()
	).paginate(page=page, per_page=10)
	return render_template('home/moviecol.html', page_data=page_data)


@home.route('/search/<int:page>/')
def search(page=None):
	if page is None:
		page = 1
	key  = request.args.get('key','')
	movie_count = Movie.query.filter(
		Movie.title.ilike('%' + key + '%') # ilike 模糊搜索
	).count()

	page_data = Movie.query.filter(
		Movie.title.ilike('%' + key + '%')
	).order_by(
		Movie.addtime.desc()
	).paginate(page=page, per_page=5)
	return render_template('home/search.html', movie_count=movie_count, key=key, page_data=page_data)


@home.route('/play/<int:id>/<int:page>/', methods=['GET','POST'])
def play(id=None, page=None):
	movie = Movie.query.join(Tag).filter(
		Tag.id == Movie.tag_id,
		Movie.id == int(id)
	).first_or_404()

	if page is None:
		page = 1
	page_data = Comment.query.join(
		Movie
	).join(
		User
	).filter(
		Movie.id == movie.id,
		User.id == Comment.user_id
	).order_by(
		Comment.addtime.desc()
	).paginate(page=page, per_page=10)

	movie.playnum = movie.playnum + 1

	# 添加评论
	form = CommentForm()
	if 'user' in session and form.validate_on_submit():
		data = form.data
		comment = Comment(
			content = data['content'],
			movie_id = movie.id,
			user_id = session['user_id']
		)
		db.session.add(comment)
		db.session.commit()
		movie.commentnum = movie.commentnum + 1
		db.session.add(movie)
		db.session.commit()
		flash('添加评论成功！', 'ok')
		return redirect(url_for('home.play', id=movie.id, page=1))
		
	db.session.add(movie)
	db.session.commit()
	return render_template('home/play.html', movie=movie, form=form, page_data=page_data)

