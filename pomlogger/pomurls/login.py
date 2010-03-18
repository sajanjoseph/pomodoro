from django.conf.urls.defaults import *

urlpatterns=patterns('django.contrib.auth.views',
url(r'^login/$','login',{'template_name':'pomlogger/mylogin.html'},name='pomlog_login'),
url(r'^logout/$', 'logout_then_login', {}, name = 'pomlog_logout'),
)
