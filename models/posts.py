import os
import jinja2

from users import *
from comments import *

from google.appengine.ext import db

template_dir = os.path.join(os.getcwd(), 'templates/')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

class Post(db.Model):
	title = db.StringProperty(required = True)
	story = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	blogger = db.StringProperty()
	liked_by = db.ListProperty(str)

	def render(self):
		self._render_text = self.story.replace('\n', '<br>')
		return render_str('post.html', p = self)

	@property
	def likes(self):
		return len(self.liked_by)

	@property
	def comments(self):
		return Comment.all().filter("post = ", str(self.key().id()))
