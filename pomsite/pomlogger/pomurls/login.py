from django.conf.urls.defaults import *
from registration.urls import urlpatterns as regurlpatterns
urlpatterns=patterns('',
url(r'^login/$','django.contrib.auth.views.login',{'template_name':'pomlogger/mylogin.html'},name='pomlog_login'),
url(r'^logout/$', 'pomlogger.views.logout', {}, name = 'pomlog_logout'),
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