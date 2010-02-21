from django.conf.urls.defaults import *
from pomlogger.models import PomEntry

urlpatterns=patterns('',

url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$','pomlogger.views.entry_archive_day'),
url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$','pomlogger.views.entry_archive_month'),
url(r'^(?P<year>\d{4})/$','pomlogger.views.entry_archive_year'),
url(r'^(?P<id>\d+)/$','pomlogger.views.entry_detail',name='pomlog_entry_detail'),

url(r'^addentry/$','pomlogger.views.add_new_entry',
    {
        'template_name':'pomlogger/add_or_edit_entry.html',
        'page_title':'Add Entry'

    },
    name='pomlog_add_entry'),

url(r'^editentry/(?P<id>\d+)/$','pomlogger.views.edit_entry',
{
'template_name':'pomlogger/add_or_edit_entry.html',
 'page_title':'Edit Entry',

},name='pomlog_edit_entry'),


url(r'^deletentry/(?P<id>\d+)/$','pomlogger.views.delete_entry',name='pomlog_delete_entry'),

url(r'^$','pomlogger.views.entry_archive_index',name='pomlog_entry_archive_index'),

)
