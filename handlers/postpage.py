from google.appengine.ext import db

from handler import *
from models.users import *
from models.comments import *

def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

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