from django.conf.urls.defaults import *
from registration.urls import urlpatterns as regurlpatterns
urlpatterns=patterns('django.contrib.auth.views',
url(r'^login/$','login',{'template_name':'pomlogger/mylogin.html'},name='pomlog_login'),
url(r'^logout/$', 'logout_then_login', {}, name = 'pomlog_logout'),
)

urlpatterns+=regurlpatterns
#urlpatterns+=patterns('registration.views',
#url(r'^register/$','register',{},name='pomlog_register'),
#
#                      
#)

#urlpatterns+=patterns('pomlogger.views',
#url(r'^sendmail/$','sendmail',{},name='sendmail'),                  
#                      )