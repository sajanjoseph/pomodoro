from django.conf.urls.defaults import *

urlpatterns=patterns('',

url(r'^entries/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$','pomlogger.views.report_entries_for_day',
{
    'template_name':'pomlogger/report_entries_for_day.html',
    'page_title':'Report for Entries of the day'

},name='pomlog_report_entries_for_day'),
                     
url(r'^entries/render_graph_for_day/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$','pomlogger.views.render_graph_for_day',
name='pomlog_render_graph_for_day'),                    
    
url(r'^categories/$','pomlogger.views.categories_report',
    {
        'template_name':'pomlogger/allcategoriesreport.html',
        'page_title':'All categories'

    },
    name='pomlog_allcategories_report'),

url(r'^categories/categories_chart/$','pomlogger.views.render_categories_chart',
name='pomlog_render_categories_chart'),
                     
url(r'^categories/current_month_categories_chart/$','pomlogger.views.render_categories_chart_for_current_month',
name='pomlog_render_categories_chart_for_current_month'),            

url(r'^categories/categoryselect/$','pomlogger.views.category_select_page',
    {
    'page_title':'select category',
    'template_name':'pomlogger/category_select_page.html'
    },
    name='pomlog_category_select_page'), 

url(r'^categories/avgdifficultycalendar/(?P<slug>[-\w]+)/$','pomlogger.views.average_difficulty',
    {
    'page_title':'average_difficulty calendar',
    'template_name':'pomlogger/average_difficulty.html'
    },
    name='pomlog_avgdifficultycalendar'), 

url(r'^$','pomlogger.views.reports',
    {
        'template_name':'pomlogger/reports.html',
        'page_title':'All reports'

    },
    name='pomlog_reports'),
    
)
