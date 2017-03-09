from google.appengine.ext import db

from handler import *
from models import posts

def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

class BlogFront(Handler):
	def get(self):
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		self.render('blog.html', posts = posts)
