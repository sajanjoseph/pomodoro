from django.conf.urls.defaults import *

urlpatterns=patterns('',
	url(r'^account/',include('pomlogger.pomurls.login')),
	url(r'^categories/',include('pomlogger.pomurls.categories')),
	url(r'^entries/',include('pomlogger.pomurls.entries')),
	url(r'^reports/',include('pomlogger.pomurls.reports')),
	
	#url(r'^month_summary/(?P<year>\d{4})/(?P<month>\d{1,2})/$','pomlogger.views.month_summary',dict(template_name = 'xxx'), name = 'msummary'),
    url(r'^$', 'pomlogger.views.index',
        dict(template_name = 'pomlogger/index.html'), name = 'home'),
	

)
