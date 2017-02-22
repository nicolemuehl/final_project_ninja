# -*- coding: utf-8 -*-
# #!/usr/bin/env python
import os
import jinja2
import webapp2
import json
from google.appengine.api import users
from google.appengine.api import urlfetch
from models import Nachricht


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        user = users.get_current_user()
        params["user"] = user
        if user:
            logged_in = True
            logout_url = users.create_logout_url("/")
            params["logout_url"] = logout_url
        else:
            logged_in = False
            login_url = users.create_login_url(self.request.url)
            params["login_url"] = login_url
        params["logged_in"] = logged_in
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class Startseite(BaseHandler):
    def get(self):
        return self.render_template("startseite.html")


class Nachrichten(BaseHandler):
    def get(self):
        return self.render_template("nachrichten.html")


class NachrichtSchreiber(BaseHandler):
    def get(self):
        return self.render_template("n_schreiben.html")

    def post(self):
        user = users.get_current_user()
        sender = self.request.get(user.nickname())
        empfaenger = self.request.get("empfaenger")
        betreff = self.request.get("betreff")
        nachrichttext = self.request.get("nachrichttext")
        if not sender:
            sender = user.nickname()
        if not empfaenger:
            return self.write("Was macht eine Nachricht ohne Empfänger für einen Sinn?")
        if not betreff:
            return self.write("Gib doch bitte einen Betreff ein!")
        if "<script>" in nachrichttext:
            return self.write("Du bist ja voll fies... Hack dich doch selber!")
        gesendete = Nachricht(sender=sender, empfaenger=empfaenger, betreff=betreff, nachrichttext=nachrichttext)
        gesendete.put()
        return self.redirect_to("Nachrichten")


class Eingang(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            return self.render_template("n_eingang.html")
        nachrichten = Nachricht.query(Nachricht.empfaenger == user.nickname()).fetch()
        params = {"nachrichten": nachrichten}
        return self.render_template("n_eingang.html", params=params)


class Ausgang(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            return self.render_template("n_eingang.html")
        nachrichten = Nachricht.query(Nachricht.sender == user.nickname()).fetch()
        params = {"nachrichten": nachrichten}
        return self.render_template("n_ausgang.html", params=params)


class NachrichtDetails(BaseHandler):
    def get(self, nachricht_id):
        nachricht = Nachricht.get_by_id(int(nachricht_id))
        params = {"nachricht": nachricht}
        return self.render_template("n_details.html", params=params)


class NachrichtLoeschen(BaseHandler):
    def get(self, nachricht_id):
        nachricht = Nachricht.get_by_id(int(nachricht_id))
        params = {"nachricht": nachricht}
        return self.render_template("n_loeschen.html", params=params)

    def post(self, nachricht_id):
        nachricht = Nachricht.get_by_id(int(nachricht_id))
        nachricht.key.delete()
        return self.redirect_to("Nachrichten")


class Wetter(BaseHandler):
    def get(self):
        url = "http://api.openweathermap.org/data/2.5/weather?q=Vienna,at&lang=de&units=metric&appid=27e02cda7ac5d2ab9f80017d9a29dd0d"
        wetterinfo = json.loads(urlfetch.fetch(url).content)
        params = {"wetterinfo": wetterinfo}
        return self.render_template("wetter.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', Startseite),
    webapp2.Route('/Nachrichten', Nachrichten, name="Nachrichten"),
    webapp2.Route('/Wetter', Wetter),
    webapp2.Route('/Nachricht schreiben', NachrichtSchreiber),
    webapp2.Route('/Eingang', Eingang),
    webapp2.Route('/Ausgang', Ausgang),
    webapp2.Route('/nachricht/<nachricht_id:\d+>', NachrichtDetails),
    webapp2.Route('/nachricht/<nachricht_id:\d+>/loeschen', NachrichtLoeschen),
], debug=True)
