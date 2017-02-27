import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

## secret for hmac cookie value

secret = 'imsosecret'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def hash_str(s):
	return hmac.new(secret, s).hexdigest()

def make_secure_val(val):
	return "%s|%s" % (val, hash_str(val))

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		#self.response.headers['content-Type'] = 'text/HTML'
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		params['user'] = self.user
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))
	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))

def render_post(response, post):
	response.out.write('<b>' + post.title + '</b><br>')
	response.out.write(post.story)

class MainPage(Handler):
	def get(self):
		self.write('Hello, Udacity!')

def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
	return db.Key.from_path('users', group)


class User(db.Model):
	name = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty()

	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid, parent = users_key())

	@classmethod
	def by_name(cls, name):
		u = User.all().filter('name =', name).get()
		return u

	@classmethod
	def register(cls, name, pw, email = None):
		pw_hash = make_pw_hash(name, pw)
		return User(parent = users_key(),
					name = name,
					pw_hash = pw_hash,
					email = email)

	@classmethod
	def login(cls, name, pw):
		u = cls.by_name(name)
		if u and valid_pw(name, pw, u.pw_hash):
			return u


def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

class Post(db.Model):
	title = db.StringProperty(required = True)
	story = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	blogger = db.StringProperty()
	likes = db.IntegerProperty()
	liked_by = db.ListProperty(str)

	def render(self):
		self._render_text = self.story.replace('\n', '<br>')
		return render_str('post.html', p = self)

	@property
	def comments(self):
		return Comment.all().filter("post = ", str(self.key().id()))

class BlogFront(Handler):
	def get(self):
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		self.render('blog.html', posts = posts)

class PostPage(Handler):
	def get(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if not post:
			self.error(404)
			return
		if self.user and post.blogger == self.user.name:
			self.render("mypost.html", post = post)
		else:
	 		self.render("permalink.html", post = post)

class NewPost(Handler):
	def get(self):
		if self.user:
			self.render("new-post.html")
		else:
			self.redirect("/login")

	def post(self):
		title = self.request.get('title')
		story = self.request.get('story')
		blogger = self.request.get('blogger')

		if title and story:
			p = Post(parent = blog_key(), title = title, story = story, blogger=blogger, likes=0, liked_by=[])
			p.put()
			self.redirect('/blog/%s' % str(p.key().id()))
		else:
			error = "Please enter the title and story!"
			self.render("new-post.html", title = title, story = story, error = error)

class RemovePost(Handler):
    def get(self, post_id):
    	if not self.user:
            self.redirect('/login')
        else:
	        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
	        post = db.get(key)
	        blogger = post.blogger
	        logged_user = self.user.name

	        if blogger == logged_user:
	            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
	            post = db.get(key)
	            post.delete()
	            self.render("remove-post.html")
	        else:
	            self.redirect("/")

class LikePost(Handler):
    def get(self, post_id):
    	if not self.user:
            self.redirect('/login')
        else:
	        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
	        post = db.get(key)
	        blogger = post.blogger
	        logged_user = self.user.name

	        if logged_user in post.liked_by:
	            self.redirect('/error')
	        elif blogger == logged_user:
	        	self.redirect('/user-error')
	        else:
	        	if post.likes == None:
	        		post.likes = 1 
	        	else:
	        		post.likes += 1
	        	post.liked_by.append(logged_user)
	        	post.put()
	        	self.redirect("/blog")


class EditPost(Handler):
    def get(self, post_id):
    	if not self.user:
            self.redirect('/login')
        else:
	        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
	        post = db.get(key)
	        blogger = post.blogger
	        logged_user = self.user.name

	        if blogger == logged_user:
	            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
	            post = db.get(key)
	            error = ""
	            self.render("edit-post.html", title=post.title,
	                        story=post.story, error=error)

    def post(self, post_id):
    	if not self.user:
            self.redirect("/login")
        else:
        	key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        	p = db.get(key)
        	if self.request.get('submit'): 
        		p.title = self.request.get('title')
		        p.story = self.request.get('story')
		        p.put()
	        self.redirect('/blog/%s' % str(p.key().id()))


class Comment(db.Model):
    comment = db.StringProperty(required = True)
    post = db.StringProperty(required = True)
    blogger = db.StringProperty(required = True)

    @classmethod
    def render(self):
        self.render("comment.html")

class NewComment(Handler):
    def get(self, post_id):
        if not self.user:
            self.redirect("/login")
            return

        post = Post.get_by_id(int(post_id), parent=blog_key())
        title = post.title
        story = post.story
        self.render("new-comment.html", title=title, story=story, pkey=post.key())

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if not post:
            self.error(404)
            return

        if not self.user:
            self.redirect('login')

        comment = self.request.get('comment')

        if comment:
            blogger = self.request.get('blogger')
            c = Comment(comment=comment, post=post_id, parent=self.user.key(), blogger=blogger)
            c.put()
            self.redirect('/blog/%s' % str(post_id))
        else:
            self.render("permalink.html", post=post, error=error)

class UpdateComment(Handler):
    def get(self, post_id, comment_id):
        post = Post.get_by_id(int(post_id), parent=blog_key())
        comment = Comment.get_by_id(int(comment_id), parent=self.user.key())
        if comment:
            self.render("update-comment.html", title=post.title, story=post.story, comment=comment.comment, pkey=post.key())
        else:
            self.write('Something went wrong!')

    def post(self, post_id, comment_id):
        comment = Comment.get_by_id(int(comment_id), parent=self.user.key())
        if comment.parent().key().id() == self.user.key().id():
            comment.comment = self.request.get('comment')
            comment.put()
        self.redirect('/blog/%s' % str(post_id))

class DeleteComment(Handler):
    def get(self, post_id, comment_id):
        comment = Comment.get_by_id(int(comment_id), parent=self.user.key())
        if comment:
            comment.delete()
            self.redirect('/blog/%s' % str(post_id))
        else:
            self.write('Something went wrong!')


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(Handler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog')

class Login(Handler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/blog')

class Error(Handler):
    def get(self):
        self.render('error.html')

class UserError(Handler):
    def get(self):
        self.render('user-error.html')

app = webapp2.WSGIApplication([('/', MainPage),
							   ('/blog/?', BlogFront),
							   ('/blog/([0-9]+)', PostPage),
							   ('/blog/new-post', NewPost),
							   ('/blog/([0-9]+)/remove-post', RemovePost),
							   ('/blog/([0-9]+)/edit-post', EditPost),
							   ('/blog/([0-9]+)/like-post', LikePost),
							   ('/error', Error),
							   ('/user-error', UserError),
							   ('/blog/([0-9]+)/new-comment', NewComment),
							   ('/blog/([0-9]+)/update-comment/([0-9]+)', UpdateComment),
							   ('/blog/([0-9]+)/delete-comment/([0-9]+)', DeleteComment),
							   ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout)],
                               debug=True)