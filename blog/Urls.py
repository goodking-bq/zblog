from blog.extend.UrlsHelper import url
from blog import blog
from blog.views import views

blog.add_url_rule('/', view_func=views.index, methods=['GET', 'POST'])
blog.add_url_rule('/index', view_func=views.index, methods=['GET', 'POST'])
blog.add_url_rule('/<string:categoryname>/<string:month>/<int:page>',
                  view_func=views.index,
                  methods=['GET', 'POST'])
url('/login', 'views.views.login', methods=['GET', 'POST'])
url('/login/authorized', 'views.views.authorized', methods=['GET', 'POST'])
url('/logout', 'views.views.logout')
url('/usereditinfo/', 'views.views.usereditinfo', methods=['GET', 'POST'])
url('/userchangepwd/', 'views.views.userchangepwd', methods=['GET', 'POST'])
url('/register', 'views.views.register', methods=['GET', 'POST'])
url('/article_create', 'views.views.article_create', methods=['GET', 'POST'])
url('/article_edit/<int:id>', 'views.views.article_edit', methods=['GET', 'POST'])
url('/search', 'views.views.search', methods=['GET', 'POST'])
url('/search_result/<string:sch>/<int:page>', 'views.search_result')
url('/upload', 'views.upload.upload', methods=['GET', 'POST'])
url('/uploads/<filename>', 'views.upload.uploaded_file')
url('/blog_msg', 'views.views.blog_msg')
url('/about', 'views.views.blog_about')
url('/calendar', 'views.views.blog_calendar')
url('/calendar_json', 'views.views.calendar_json', methods=['GET', 'POST'])
url('/visit_json', 'views.views.visit_json')
url('/article_json', 'views.views.article_json')
url('/article_commit', 'views.views.article_commit', methods=['GET', 'POST'])
# ############ admin ###############

url('/admin/main', 'views.admin.index1')
url('/admin/users', 'views.admin.users')
url('/admin/useredit/<id>', 'views.admin.useredit', methods=['GET', 'POST'])
url('/admin/userdelete/<id>', 'views.admin.userdelete')
url('/admin/category', 'views.admin.category')
url('/admin/categorycreate', 'views.admin.categorycreate', methods=['GET', 'POST'])
url('/admin/categoryedit/<id>', 'views.admin.categoryedit', methods=['GET', 'POST'])
url('/admin/categorydelete/<id>', 'views.admin.categorydelete')
url('/admin/article', 'views.admin.article')
url('/admin/articledelete/<id>', 'views.admin.articledelete')
url('/admin/admin_second_bar', 'views.admin.admin_second_bar')
url('/admin/admin_second_baredit/<id>', 'views.admin.admin_second_baredit', methods=['GET', 'POST'])
url('/admin/settings', 'views.admin.settings', methods=['GET', 'POST'])
url('/admin/imgs', 'views.admin.imgs')
url('/admin/atts', 'views.admin.atts')
url('/admin/rmfile/<filename>/<urls>', 'views.upload.rmfile')
url('/admin/backup', 'views.backup.backup')
url('/admin/dobackup', 'views.backup.dobackup')
url('/admin/visit_statistics', 'views.Taskscheduler.visit_statistics')