from django.conf.urls.defaults import *
from pomlogger.models import PomCategory


urlpatterns=patterns('',

url(r'^addcategory/$','pomlogger.views.add_category',
    {
     'page_title':'Add category',
     'template_name':'pomlogger/add_or_edit_category.html'
    },
    name='pomlog_add_category'),

url(r'^editcategory/(?P<slug>[-\w]+)/$','pomlogger.views.edit_category',
    {
    'page_title':'EditCategory',
    'template_name':'pomlogger/add_or_edit_category.html',
    },
    name='pomlog_edit_category'),


url(r'^deletecategory/(?P<slug>[-\w]+)/$','pomlogger.views.delete_category',name='pomlog_delete_category'),


url(r'^(?P<slug>[-\w]+)/$','pomlogger.views.category_detail',
    {
    'template_name':'pomlogger/pomcategory_detail.html',
      'page_title':'Category Details'  
    },
    name='pomlog_category_detail'),

url(r'^$','pomlogger.views.category_list',
    {
    'page_title':'all categories',
    'template_name':'pomlogger/pomcategory_list.html'
    },
    name='pomlog_category_list'),

)
