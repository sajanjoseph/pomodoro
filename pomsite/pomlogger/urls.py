from django.conf.urls.defaults import *

urlpatterns=patterns('',
	url(r'^account/',include('pomlogger.pomurls.login')),
	url(r'^categories/',include('pomlogger.pomurls.categories')),
	url(r'^entries/',include('pomlogger.pomurls.entries')),
    url(r'^$', 'pomlogger.views.index',
        dict(template_name = 'pomlogger/index.html'), name = 'home'),
	

)
