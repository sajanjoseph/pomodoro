from django.conf.urls.defaults import *

import os
import registration

if os.environ.has_key('POMODORO_HEROKU_PRODUCTION') and os.environ.get('POMODORO_HEROKU_PRODUCTION')=='True':
	urlpatterns = patterns('',
			url(r'^account/login/$','django.contrib.auth.views.login',{'template_name':'pomlogger/mylogin.html'},name='pomlog_login'),
			url(r'^account/logout/$', 'pomlogger.views.logout', {}, name = 'pomlog_logout'),
			url(r'^account/',include('registration.backends.default.urls')),
			url(r'^categories/',include('pomlogger.pomurls.categories')),
			url(r'^entries/',include('pomlogger.pomurls.entries')),
			url(r'^reports/',include('pomlogger.pomurls.reports')),
			url(r'^$', 'pomlogger.views.index',dict(template_name = 'pomlogger/index.html'), name = 'home'),
							)
	custom_reg_patterns = patterns('',
		     url(r'^account/register/', registration.views.register, 
		      {'form_class':registration.forms.RegistrationFormUniqueEmail,'backend':'registration.backends.default.DefaultBackend' },
		      
		      name='registration_register'),
		    						)
	urlpatterns += custom_reg_patterns
	urlpatterns += patterns('',
		    url(r'^$', 'pomlogger.views.index',dict(template_name = 'pomlogger/index.html'), name = 'home'),
		)
	

else:
	urlpatterns=patterns('',
		url(r'^account/',include('pomlogger.pomurls.login')),
		url(r'^categories/',include('pomlogger.pomurls.categories')),
		url(r'^entries/',include('pomlogger.pomurls.entries')),
		url(r'^reports/',include('pomlogger.pomurls.reports')),
		
		#url(r'^month_summary/(?P<year>\d{4})/(?P<month>\d{1,2})/$','pomlogger.views.month_summary',dict(template_name = 'xxx'), name = 'msummary'),
	    url(r'^$', 'pomlogger.views.index',dict(template_name = 'pomlogger/index.html'), name = 'home'),
						)



