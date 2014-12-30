from blog.extend.UrlsHelper import url
from blog import blog
from blog import views

blog.add_url_rule('/', view_func=views.index, methods=['GET', 'POST'])
blog.add_url_rule('/index', view_func=views.index, methods=['GET', 'POST'])
blog.add_url_rule('/<string:categoryname>/<string:month>/<int:page>',
                  view_func=views.index,
                  methods=['GET', 'POST'])
url('/login', 'views.login', methods=['GET', 'POST'])
url('/login/authorized', 'views.authorized', methods=['GET', 'POST'])
url('/logout', 'views.logout')
url('/usereditinfo/', 'views.usereditinfo', methods=['GET', 'POST'])
url('/userchangepwd/', 'views.userchangepwd', methods=['GET', 'POST'])
url('/register', 'views.register', methods=['GET', 'POST'])
url('/article_create', 'views.article_create', methods=['GET', 'POST'])
url('/article_edit/<int:id>', 'views.article_edit', methods=['GET', 'POST'])
url('/search', 'views.search', methods=['GET', 'POST'])
url('/search_result/<string:sch>/<int:page>', 'views.search_result')
url('/upload', 'upload.upload', methods=['GET', 'POST'])
url('/uploads/<filename>', 'upload.uploaded_file')
url('/blog_msg', 'views.blog_msg')
url('/about', 'views.blog_about')
url('/calendar', 'views.blog_calendar')
url('/calendar_json', 'views.calendar_json', methods=['GET', 'POST'])
url('/visit_json', 'views.visit_json')
url('/article_json', 'views.article_json')
# ############ admin ###############

url('/admin/main', 'admin.index1')
url('/admin/users', 'admin.users')
url('/admin/useredit/<id>', 'admin.useredit', methods=['GET', 'POST'])
url('/admin/userdelete/<id>', 'admin.userdelete')
url('/admin/category', 'admin.category')
url('/admin/categorycreate', 'admin.categorycreate', methods=['GET', 'POST'])
url('/admin/categoryedit/<id>', 'admin.categoryedit', methods=['GET', 'POST'])
url('/admin/categorydelete/<id>', 'admin.categorydelete')
url('/admin/article', 'admin.article')
url('/admin/articledelete/<id>', 'admin.articledelete')
url('/admin/admin_second_bar', 'admin.admin_second_bar')
url('/admin/admin_second_baredit/<id>', 'admin.admin_second_baredit', methods=['GET', 'POST'])
url('/admin/settings', 'admin.settings', methods=['GET', 'POST'])
url('/admin/imgs', 'admin.imgs')
url('/admin/atts', 'admin.atts')
url('/admin/rmfile/<filename>/<urls>', 'upload.rmfile')
url('/admin/backup', 'backup.backup')
url('/admin/dobackup', 'backup.dobackup')
url('/admin/visit_statistics', 'Taskscheduler.visit_statistics')