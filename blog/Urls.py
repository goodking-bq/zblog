from blog.extend.UrlsHelper import url





url('/login', 'views.login',methods = ['GET', 'POST'])
url('/logout','views.logout')
url('/usereditinfo/','views.usereditinfo',methods = ['GET', 'POST'])
url('/userchangepwd/','views.userchangepwd',methods = ['GET', 'POST'])
url('/register','views.register', methods = ['GET', 'POST'])
url('/article_show/<string:title>','views.article_show')
url('/article_create','views.article_create',methods = ['GET', 'POST'])
url('/article_edit/<int:id>','views.article_edit',methods = ['GET', 'POST'])
url('/search','views.search',methods = ['GET', 'POST'])
url('/search_result/<string:search>','views.search_result')
url('/upload','upload.upload',methods = ['GET', 'POST'])
url('/uploads/<filename>','upload.uploaded_file')
url('/blog_msg', 'views.blog_msg')
url('/about', 'views.blog_about')


############# admin ###############

url('/admin/main','admin.index1')
url('/admin/users','admin.users')
url('/admin/useredit/<id>','admin.useredit',methods = ['GET', 'POST'])
url('/admin/userdelete/<id>','admin.userdelete')
url('/admin/category','admin.category')
url('/admin/categorycreate','admin.categorycreate',methods = ['GET', 'POST'])
url('/admin/categoryedit/<id>','admin.categoryedit',methods = ['GET', 'POST'])
url('/admin/categorydelete/<id>','admin.categorydelete')
url('/admin/article','admin.article')
url('/admin/articledelete/<id>', 'admin.articledelete')
