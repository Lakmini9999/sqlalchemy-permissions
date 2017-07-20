class Permissions(object):

    def __init__(self, app=None, db=None):
        if app is not None:
            self.init_app(app, db)

    def init_app(self, app, db, user_getter=None):
        self.app = app
        self.db = db
        self.user_getter = user_getter
