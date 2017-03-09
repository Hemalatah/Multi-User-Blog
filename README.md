# Multi-User-Blog

### About the project...
 In this project you will be building a multi user blog where users can sign in and post blog posts as well as 'Like' and 'Comment' on other posts made on the blog. You will be hosting this blog on Google App Engine and you will also be creating an authentication system for users to be able to register and sign in and then create blog posts!
 
 Checkout the [live](https://multi-user-blog-160020.appspot.com/blog) version of this project.

### To run the Application in your local machine...

* Have Python 2 and Google App Engine installed in the root directory
* git clone the repo
* get the repo as a current working directory in your terminal
* in your terminal, run the google app engine locally by typing 
```sh
$ dev_appserver.py .
```
* Browse the blog site in the localhost, port number: 8000 as a default

### About the files...

* index.py - has all the request handlers with webapp2
* models - a folder has python files contains class which access google app engine DB for users, posts and comments 
* handlers - a folder has a number of python files each with its own methods required for the blog
* .pyc - complied form of all the python files

