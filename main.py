import webapp2
import os
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BPost(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class Main(Handler):
    def get(self):
        self.redirect("/blog")

class Blog(Handler):
    def render_blog(self, title="", body=""):
        bposts = db.GqlQuery("SELECT * FROM BPost ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, body=body, bposts=bposts)

    def get(self):
        self.render_blog()

    def post(self):
        self.redirect("/newpost")

class NewPost(Handler):
    def render_new(self, title="", body="", error=""):
        self.render("newpost.html", title=title, body=body, error=error)

    def get(self):
        self.render_new()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = BPost(title=title, body=body)
            b.put()

            self.redirect("/blog/"+str(b.key().id()))
        else:
            error = "Submissions must include a title and body."
            self.render_new(title, body, error)

class ViewPostHandler(Handler):
    def get(self, id):
        bpost = BPost.get_by_id(int(id))
        title = ""
        body = ""

        if bpost:
            self.render("post.html", title=title, body=body, bpost=bpost)
        else:
            self.response.write("This post doesn't exist")

app = webapp2.WSGIApplication([
    ('/', Main),
    ('/blog', Blog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
