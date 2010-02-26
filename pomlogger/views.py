from pomlogger.models import PomEntry,PomCategory
from pomlogger.models import PomEntryForm,PomCategoryForm,PomCategoryNameForm
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
import datetime
import time
import string
import calendar
from django.template.defaultfilters import title
from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response,get_object_or_404,redirect

def get_month_as_number(monthname):
    if title(monthname) not in calendar.month_abbr:
        raise Http404
    mlist=list(calendar.month_abbr)
    return mlist.index(title(monthname))

def timediff(start,end):
    delta_start=datetime.timedelta(hours=start.hour,minutes=start.minute,seconds=start.second)
    delta_end=datetime.timedelta(hours=end.hour,minutes=end.minute,seconds=end.second)
    diff=delta_end-delta_start
    diffminutes=diff.seconds/60
    return diffminutes

def get_duration_for_categories(entryset):
    entry_duration_dict={}
    for anentry in entryset:
        categories=anentry.categories
        duration_mts=timediff(anentry.start_time,anentry.end_time)
        for acat in categories.all():
            if acat.name in entry_duration_dict:
                entry_duration_dict[acat.name]+=duration_mts
                print 'cat:%s already in dict. durn=%s'%(acat.name,entry_duration_dict[acat.name])
            else:
                entry_duration_dict[acat.name]=duration_mts
                print 'new cat:%s ,durn=%s'%(acat.name,duration_mts)
    return entry_duration_dict

def custom_render(request,context,template):
    req_context=RequestContext(request,context)
    return render_to_response(template,req_context)

@login_required
def entry_archive_index(request,page_title,template_name):
    entryset=PomEntry.objects.filter(author=request.user)
    entry_duration_dict=get_duration_for_categories(entryset)
    now=datetime.datetime.now()    
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'page_title':page_title}
    #return custom_render(request,entry_duration_info,'pomlogger/pomentry_archive.html')
    #print 'entry_archive_index():template=%s'%template_name
    return custom_render(request,context,template_name)

@login_required
def entry_archive_year(request,year,page_title,template_name):
    print 'year=',year,'of type=',type(year)
    entryset=PomEntry.objects.filter(today__year=year)
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'page_title':page_title}
    #return render_to_response('pomlogger/pomentry_archive_year.html',entry_duration_info)
    return custom_render(request,context,template_name)

@login_required
def entry_archive_month(request,year,month,page_title,template_name):
    print 'year=',year,'of type=',type(year)
    print 'month=',month,'of type=',type(month)
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month))
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'month':month,'page_title':page_title}
    #return render_to_response('pomlogger/pomentry_archive_month.html',entry_duration_info)
    return custom_render(request,context,template_name)

@login_required
def entry_archive_day(request,year,month,day,page_title,template_name):
    print 'year=',year,'of type=',type(year)
    print 'month=',month,'of type=',type(month)
    print 'day=',day,'of type=',type(day)
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),today__day=day)
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'month':month,'day':day,'page_title':page_title}
    #return render_to_response('pomlogger/pomentry_archive_day.html',entry_duration_info)
    return custom_render(request,context,template_name)

@login_required
def entry_detail(request,id,page_title,template_name):	
    entry=get_object_or_404(PomEntry,id=id)
    duration=timediff(entry.start_time,entry.end_time)
    context={'object':entry,'duration':duration,'page_title':page_title}
    #return render_to_response('pomlogger/pomentry_detail.html',entry_detail_dict)
    return custom_render(request,context,template_name)

@login_required
def delete_entry(request,id):
    entry=get_object_or_404(PomEntry,id=id)
    print 'delete_entry()-entry=',entry
    entry.delete()
    print 'delete_entry()--deleted'
    return redirect('pomlog_entry_archive_index')


def _get_categories(catnames):
    categories=string.split(catnames,',')
    cats=[]
    for name in categories:
        if name and  not name.isspace():
            cat,status=PomCategory.objects.get_or_create(name__iexact=name.strip(),defaults={'name':name,'description':name})# if no defaults ,IntegrityError
            cats.append(cat)
    return cats

@login_required
@transaction.commit_on_success
def add_new_entry(request,template_name,page_title):
    form_data=get_form_data(request)
    form=PomEntryForm(form_data)
    catnameform=PomCategoryNameForm(form_data)
    context={'page_title':page_title,'entryform':form,'categoryform':catnameform}
    if request.method=='POST' and form.is_valid() and catnameform.is_valid():
        newentry=form.save()         
        catnames=catnameform.cleaned_data['categories']            
        newentry.categories=_get_categories(catnames)
        newentry.save()
        return redirect('pomlog_entry_archive_index')
        
    #return render_to_response(template_name,context)
    return custom_render(request,context,template_name)

def get_category_names_as_one_string(categorynameslist):
    return ','.join(categorynameslist)

@login_required
@transaction.commit_on_success
def edit_entry(request,id,template_name,page_title):
    entry=get_object_or_404(PomEntry,id=id)
    categorynames_as_separate=[x.name for x in entry.categories.all()]
    categorynames_as_one_string=get_category_names_as_one_string(categorynames_as_separate)
    categorynamesdata={'categories':categorynames_as_one_string}
    form_data=get_form_data(request)
    form=PomEntryForm(form_data,instance=entry)
    catnameform=PomCategoryNameForm(form_data,initial=categorynamesdata)
    context={'entryform':form,'categoryform':catnameform,'page_title':page_title}
    if request.method=='POST' and form.is_valid() and catnameform.is_valid():       
        edited_entry=form.save()
        catnames=catnameform.cleaned_data['categories']
        edited_entry.categories=_get_categories(catnames)
        edited_entry.save()           
        return redirect('pomlog_entry_archive_index')
    #return render_to_response(template_name,context)
    return custom_render(request,context,template_name)

@login_required
def category_list(request,template_name,page_title):
    categories=PomCategory.objects.all()
    category_list_dict={'object_list':categories,'page_title':page_title }
    return custom_render(request,category_list_dict,template_name)
    #return render_to_response('pomlogger/pomcategory_list.html',category_list_dict)

@login_required
def category_detail(request,slug,template_name,page_title):
    category=get_object_or_404(PomCategory,slug=slug)
    now=datetime.datetime.now()
    context={'object':category,'now':now, 'page_title': page_title}
    #return render_to_response(template_name,category_detail_dict)
    return custom_render(request,context,template_name)

@login_required
def delete_category(request,slug):
    print 'slug=',slug
    cat=get_object_or_404(PomCategory,slug=slug)
    print 'delete cat()=',cat
    cat.delete()
    print 'cat deleted'
    return redirect('pomlog_category_list')



def is_duplicate_cat(name):
    if PomCategory.objects.filter(name__iexact=name).count()!=0:
        return True
    else:
        return False


def _add_or_edit(request,page_title,template_name,instance=None):
    form_data=get_form_data(request)
    form=PomCategoryForm(form_data,instance=instance)
    context={'categoryform':form,'page_title':page_title}
    if request.method=='POST' and form.is_valid():
        name=form.cleaned_data['name']
        name=name.strip()
        if is_duplicate_cat(name):
            if instance!=None:
                print 'we want to edit %s'%name
                form.save()
                return redirect('pomlog_category_list')
            else:
                #return render_to_response(template_name,context)
                return custom_render(request,context,template_name)
        else:
            print 'we are adding a new cat %s'%name
            form.save()
            return redirect('pomlog_category_list') 
    #return render_to_response(template_name,context)                       
    return custom_render(request,context,template_name)



@login_required
def add_category(request,template_name,page_title):
    return _add_or_edit(request,page_title,template_name) 


@login_required
def edit_category(request,slug,template_name,page_title):
    cat=get_object_or_404(PomCategory,slug=slug)
    return _add_or_edit(request,page_title,template_name,instance=cat)


@login_required
def get_form_data(request):
    return request.POST if request.method=='POST' else None


    

