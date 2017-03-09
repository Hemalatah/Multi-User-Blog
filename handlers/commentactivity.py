from handler import *
from models.posts import Post
from models.users import User
from models.comments import Comment

from google.appengine.ext import db

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

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