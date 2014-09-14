from blog.extend.UrlsHelper import url





url('/login', 'views.login',methods = ['GET', 'POST'])
url('/logout','views.logout')
url('/user/<nickname>','views.user')
url('/edit/','views.edit',methods = ['GET', 'POST'])
url('/register','views.register', methods = ['GET', 'POST'])
url('/article_show/<string:title>','views.article_show')
url('/article_create','views.article_create',methods = ['GET', 'POST'])
url('/article_edit/<int:id>','views.article_edit',methods = ['GET', 'POST'])
url('/category_create','views.category_create',methods = ['GET', 'POST'])
url('/search','views.search',methods = ['GET', 'POST'])
url('/search_result/<string:search>','views.search_result')