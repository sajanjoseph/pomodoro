from django.conf.urls.defaults import *
from registration.urls import urlpatterns as regurlpatterns
from registration.forms import RegistrationFormUniqueEmail
#from registration.views import register

urlpatterns=patterns('',
url(r'^login/$','django.contrib.auth.views.login',{'template_name':'pomlogger/mylogin.html'},name='pomlog_login'),
url(r'^logout/$', 'pomlogger.views.logout', {}, name = 'pomlog_logout'),
)



from registration.views import register

custom_reg_patterns=patterns('',
     url(r'^register/', register, 
      {'form_class':RegistrationFormUniqueEmail ,'backend':'registration.backends.default.DefaultBackend'},
      
      name='registration_register'),
)
urlpatterns+=custom_reg_patterns

#
urlpatterns+=regurlpatterns

#urlpatterns+=patterns('pomlogger.views',
#url(r'^sendmail/$','sendmail',{},name='sendmail'),                  
#                      )