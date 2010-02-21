from django.conf.urls.defaults import *

urlpatterns=patterns('django.contrib.auth.views',
url(r'^login/$','login',{'template_name':'pomlogger/mylogin.html'},name='pomlog_login'),
url(r'^logout/$','logout',{'template_name':'pomlogger/mylogout.html'},name='pomlog_logout'),
)
