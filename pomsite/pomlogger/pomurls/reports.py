from django.conf.urls.defaults import *

urlpatterns=patterns('',

url(r'^entries/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$','pomlogger.views.report_entries_for_day',
{
    'template_name':'pomlogger/report_entries_for_day.html',
    'page_title':'Report for Entries of the day'

},name='pomlog_report_entries_for_day'),

url(r'^entries/(?P<year>\d{4})/(?P<month>\w{3})/$','pomlogger.views.report_entries_for_month',
{
    'template_name':'pomlogger/report_entries_for_month.html',
    'page_title':'Report for Entries in the month'
}, name='pomlog_report_entries_for_month'),

url(r'^entries/(?P<year>\d{4})/$','pomlogger.views.report_entries_for_year',
    {
        'template_name':'pomlogger/report_entry_archive_year.html',
        'page_title':'Report for Entries in the Year'

    },name='pomlog_report_entries_year' ),

url(r'^entries/$','pomlogger.views.entries_report',
    {
     'page_title':'All Entries Report',
     'template_name':'pomlogger/allentriesreport.html'
    },
    name='pomlog_allentries_report'),
    
url(r'^categories/$','pomlogger.views.categories_report',
    {
        'template_name':'pomlogger/allcategoriesreport.html',
        'page_title':'All categories'

    },
    name='pomlog_allcategories_report'),
    
url(r'^$','pomlogger.views.reports',
    {
        'template_name':'pomlogger/reports.html',
        'page_title':'All reports'

    },
    name='pomlog_reports'),
    
)
