from handler import *


class Error(Handler):
    def get(self):
        self.render('error.html')


class UserError(Handler):
    def get(self):
        self.render('user-error.html')
