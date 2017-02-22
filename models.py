from google.appengine.ext import ndb


class Nachricht(ndb.Model):
    sender = ndb.StringProperty()
    empfaenger = ndb.StringProperty()
    betreff = ndb.StringProperty()
    nachrichttext = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)
