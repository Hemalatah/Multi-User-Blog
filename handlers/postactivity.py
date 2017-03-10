from handler import *
from models.posts import Post
from models.users import User

from google.appengine.ext import db


def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


class NewPost(Handler):
    def get(self):
        if self.user:
            self.render("new-post.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect("/login")
        else:
            title = self.request.get('title')
            story = self.request.get('story')
            blogger = self.user.name

            if title and story:
                p = Post(parent=blog_key(), title=title, story=story,
                         blogger=blogger, likes=0, liked_by=[])
                p.put()
                self.redirect('/blog/%s' % str(p.key().id()))
            else:
                error = "Please enter the title and story!"
                self.render("new-post.html", title=title, story=story, error=er
                            ror)


class RemovePost(Handler):
    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
        else:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            if not post:
                self.error(404)
                return
            blogger = post.blogger
            blogged_user = self.user.name

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
            if not post:
                self.error(404)
                return
            blogger = post.blogger
            logged_user = self.user.name

            if logged_user in post.liked_by:
                self.redirect('/error')
            elif blogger == logged_user:
                self.redirect('/user-error')
            else:
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
            if not post:
                self.error(404)
                return
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
            post = db.get(key)
            if not post:
                self.error(404)
                return
            blogger = post.blogger
            logged_user = self.user.name

            if self.request.get('submit') and blogger == logged_user:
                post.title = self.request.get('title')
                post.story = self.request.get('story')
                post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
