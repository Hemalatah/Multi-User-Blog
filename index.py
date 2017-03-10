import os
import jinja2
import webapp2

from handlers.handler import Handler
from handlers.signup import Register
from handlers.postpage import PostPage
from handlers.postactivity import *
from handlers.commentactivity import *
from handlers.log import Login
from handlers.log import Logout
from handlers.error import *
from handlers.blog import *

from google.appengine.ext import db


def render_post(response, post):
    response.out.write('<b>' + post.title + '</b><br>')
    response.out.write(post.story)


class MainPage(Handler):
    def get(self):
        self.write('Hello, Udacity!')

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
                               ('/blog/([0-9]+)/update-comment/([0-9]+)', Updat
                                eComment),
                               ('/blog/([0-9]+)/delete-comment/([0-9]+)', Delet
                                eComment),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout)], debug=True)
