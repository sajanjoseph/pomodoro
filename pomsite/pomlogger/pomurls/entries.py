from django.conf.urls.defaults import *
from pomlogger.models import PomEntry

urlpatterns=patterns('',

url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$','pomlogger.views.entry_archive_day',
{
    'template_name':'pomlogger/pomentry_archive_day.html',
    'page_title':'Entries for the day'

},
name='pomlog_entry_archive_day'),
url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$','pomlogger.views.entry_archive_month',
{
    'template_name':'pomlogger/pomentry_archive_month.html',
    'page_title':'Entries for the month'
},
    name='pomlog_entry_archive_month'),



url(r'^(?P<year>\d{4})/$','pomlogger.views.entry_archive_year',
    {
        'template_name':'pomlogger/pomentry_archive_year.html',
        'page_title':'Entries for the Year'

    },name='pomlog_entry_archive_year' ),



url(r'^(?P<id>\d+)/$','pomlogger.views.entry_detail',
{
    'template_name':'pomlogger/pomentry_detail.html',
    'page_title':'Details of Entry'

},
name='pomlog_entry_detail'),



url(r'^addentry/$','pomlogger.views.add_new_entry',
    {
        'template_name':'pomlogger/add_entry.html',
        'page_title':'Add Entry'

    },
    name='pomlog_add_entry'),



url(r'^editentry/(?P<id>\d+)/$','pomlogger.views.edit_entry',
{
'template_name':'pomlogger/edit_entry.html',
 'page_title':'Edit Entry',

},name='pomlog_edit_entry'),




url(r'^deletentry/(?P<id>\d+)/$','pomlogger.views.delete_entry',name='pomlog_delete_entry'),




url(r'^$','pomlogger.views.entry_archive_index',
    {
        'template_name':'pomlogger/pomentry_archive.html',
        'page_title':'All entries'

    },
    name='pomlog_entry_archive_index'),

url(r'^share/$','pomlogger.views.share_entries',
    {   'template_name':'pomlogger/share_entries.html',
        'page_title':'Share Entries'  
    },
    name='pomlog_share_entries'),

url(r'^unshare/(?P<entryid>\d+)/(?P<userid>\d+)/$','pomlogger.views.unshare_entry',
    
    name='pomlog_unshare_entry'),
                     
url(r'^entries_shared/$','pomlogger.views.entries_shared',
    {'template_name':'pomlogger/includes/entries_shared.html',
        'page_title':'Entries Shared'  
    },
    name='pomlog_entries_shared'),                     




)
