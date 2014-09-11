from werkzeug import import_string, cached_property
from blog import blog,admin
class LazyView(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)
    
def url(url_rule, import_name, **options):
    view = LazyView('blog.' + import_name)
    blog.add_url_rule(url_rule, view_func=view, **options)
def admin_url():
    pass