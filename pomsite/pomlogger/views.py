from pomlogger.models import PomEntry,PomCategory
from pomlogger.forms import PomCategoryForm,PomCategoryNameForm
from pomlogger.forms import PomEntryForm,PomEntryEditForm,PomEntryDifficultyForm
from pomlogger.forms import PomEntryDescForm,PomEntryShareForm

from django.core.urlresolvers import reverse

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.views import logout_then_login
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count,Avg
from django.template.defaultfilters import title
from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response,get_object_or_404,redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.models import User
from django.core.mail import send_mail,EmailMessage
import datetime
import time
import string
import calendar
import os.path
import logging
from operator import itemgetter

#import settings
from settings import CHART_TYPE,BAR_WIDTH,PLOT_OFFSET,BAR_COLOR,LABEL_COLOR,TITLE_COLOR,REPORT_IMG_FMT,REPORT_DOC_FMT,FIGURE_WIDTH_SCALE_FACTOR,YSTEP_FACTOR
from settings import IMAGE_FOLDER_PATH
from settings import PAGINATE_BY
from settings import MEDIA_URL

from django.http import HttpResponse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab
from matplotlib.backends.backend_pdf import PdfPages

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import simplejson

from django.core.cache import cache

from settings import DEFAULT_FROM_EMAIL

#logger = logging.getLogger("pomodoro")

prefix = 'pomodoro'
def key_function(args,prefix=prefix):
    #sample pomodoro-myusername-entrylist'
    #
    keyargs =[prefix]
    keyargs.extend(args)
    key = '-'.join(keyargs)
    return key

@require_POST
@never_cache
def logout(request):
    #nxt=request.POST.get('next')
    return logout_then_login(request)

def server_error(request,template_name="500.html"):
    return custom_render(request,{},template_name)

@login_required
def index(request, template_name):
    path=request.path
    entries_count=[]
    index_key = key_function([request.user.username],'index')
    entry_count_dump = cache.get(index_key) if cache.has_key(index_key) else None
    if not entry_count_dump:
        #print 'no index_key in cache..calling db'
        entries_dict=PomEntry.objects.filter(author=request.user).values('today').annotate(dcount=Count('today'))
        for record in entries_dict:
            count=record['dcount']
            datevalue=record['today']
            url = create_url_for_entries_of_day(datevalue)
            entries_count.append({
                                  'title':str(count),
                                  'start':datevalue.strftime("%Y-%m-%d"),
                                  'end':datevalue.strftime("%Y-%m-%d"),
                                  'url': url
                                  })
        entry_count_dump=simplejson.dumps(entries_count)
        cache.set(index_key,entry_count_dump)
    #print 'index:dump=',entry_count_dump
    cr=custom_render(request, {'path':path,'entry_count':entry_count_dump },template_name)
    return cr

@login_required
def category_select_page(request,page_title,template_name):
    #print 'req for diff'
    path=request.path
    context={'page_title':page_title}
    return custom_render(request,context,template_name)

def create_url_for_entries_of_day(datevalue):
    month = datevalue.strftime("%m")
    month = int(month)
    month = calendar.month_abbr[month]
    month = month.lower()
    year = datevalue.strftime("%Y")
    day = datevalue.strftime("%d")
    url = reverse('pomlog_entry_archive_day',args=[year,month,day])
    return url

@login_required
def average_difficulty(request,page_title,template_name,slug):
    path=request.path
    category = PomCategory.objects.get(slug=slug,creator=request.user)
    category_name = category.name
    #print 'category=',category_name
    cat_avg_diff_list = []
    avg_diff_key = key_function([request.user.username,slug],'cat_avg_diff')
    avg_diff_dump = cache.get(avg_diff_key) if cache.has_key(avg_diff_key) else None
    
    if not avg_diff_dump:
        entries_dict=PomEntry.objects.filter(author=request.user,categories=category).values('today').annotate(davg=Avg('difficulty'))
        for record in entries_dict:
            avgdiff=record['davg']
            datevalue=record['today']
            url = create_url_for_entries_of_day(datevalue)
            cat_avg_diff_list.append({
                                  'title':str(avgdiff),
                                  'start':datevalue.strftime("%Y-%m-%d"),
                                  'end':datevalue.strftime("%Y-%m-%d"),
                                  'url': url
                                  })
        avg_diff_dump = simplejson.dumps(cat_avg_diff_list)
        cache.set(avg_diff_key,avg_diff_dump)
    #print 'avg_diff_dump=',avg_diff_dump
    cr=custom_render(request, {'page_title':page_title,'category_name':category_name,'path':path,'avg_diff_dump':avg_diff_dump },template_name)
    return cr
            

#@login_required
#def index1(request, template_name):
#    path=request.path
#    entries_count=[]
#    entries_dict=PomEntry.objects.filter(author=request.user).values('today').annotate(dcount=Count('today'))
#    for record in entries_dict:
#        count=record['dcount']
#        datevalue=record['today']
#        entries_count.append({
#                              'title':str(count),
#                              'start':datevalue.strftime("%Y-%m-%d"),
#                              'end':datevalue.strftime("%Y-%m-%d")
#                              })
#    entry_count_dump=simplejson.dumps(entries_count)
#    #print 'index()::entry_count_dump[0]=',entry_count_dump[0:70]
#    cr=custom_render(request, {'path':path,'entry_count':entry_count_dump },template_name)
#    return cr

def get_month_as_number(monthname):
    if title(monthname) not in calendar.month_abbr:
        raise Http404
    mlist=list(calendar.month_abbr)
    return mlist.index(title(monthname))

@login_required
def entries_shared(request,page_title,template_name):
    entries_sharedto_me=PomEntry.objects.filter(sharedwith=request.user).order_by('-today','-end_time')#added for sharing
    context={'entries_sharedto_me':entries_sharedto_me,'page_title':page_title}
    return custom_render(request,context,template_name)
    
def timediff(start,end):
    #assumes that start,end times are within 24 hours of each other
    #logger.debug("start="+str(start)+"end="+str(end))
    delta_start=datetime.timedelta(hours=start.hour,minutes=start.minute,seconds=start.second)
    delta_end=datetime.timedelta(hours=end.hour,minutes=end.minute,seconds=end.second)
    diff=delta_end-delta_start
    diffminutes=diff.seconds/60
    #logger.debug("diffminutes="+str(diffminutes))
    return diffminutes

def get_duration_for_categories(entryset):
    entry_duration_dict={}
    for anentry in entryset:
        categories=anentry.categories
        duration_mts=timediff(anentry.start_time,anentry.end_time)
        for acat in categories.all():
            if acat.name in entry_duration_dict:
                entry_duration_dict[acat.name]+=duration_mts
            else:
                entry_duration_dict[acat.name]=duration_mts
    return entry_duration_dict

def get_durations_for_entries(entryset):
    entry_duration_dict={}
    for anentry in entryset:
        duration_mts=timediff(anentry.start_time,anentry.end_time)
        #store duration against entry sothat entries can be sorted in asc order of start_time
        entry_duration_dict[anentry] = duration_mts
    return entry_duration_dict

def get_durations_for_entries_old(entryset):
    entry_duration_dict={}
    for anentry in entryset:
        duration_mts=timediff(anentry.start_time,anentry.end_time)
        #logger.debug("anentry="+str(anentry)+"duration_mts="+str(duration_mts))
        entry_duration_dict[anentry.__unicode__() ] = duration_mts
    return entry_duration_dict

def custom_render(request,context,template):
    req_context=RequestContext(request,context)
    return render_to_response(template,req_context)

@login_required
def entry_archive_index(request,page_title,template_name):
    archive_index_key = key_function([request.user.username],'archive_index')
    entryset = cache.get(archive_index_key) if cache.has_key(archive_index_key) else None
    if not entryset:
        #print 'no archive index in cache..calling db'
        entryset=PomEntry.objects.filter(author=request.user).order_by('-today','-end_time')
        cache.set(archive_index_key,entryset)
    category_duration_dict=get_duration_for_categories(entryset)
    sorteddurations=sorted(category_duration_dict.items(),key=itemgetter(1),reverse=True)
    #sorteddurations=get_pagination_entries(request, sorteddurations)#do we need this?or a simple scrollable area?
    now=datetime.datetime.now()
    entries = get_pagination_entries(request, entryset)
    #entries_sharedto_me=PomEntry.objects.filter(sharedwith=request.user).order_by('-today','-end_time')#added for sharing
    #entries_sharedto_me=get_pagination_entries(request,entries_sharedto_me)
    context={'sorteddurations':sorteddurations,'entries':entries,'page_title':page_title}
    #context={'sorteddurations':sorteddurations,'category_duration_dict':category_duration_dict,'entries':entries,'entries_sharedto_me':entries_sharedto_me,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def get_pagination_entries(request, entryset):
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    paginator = Paginator(entryset, PAGINATE_BY)
    try:
        entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)
    return entries

@login_required
def entry_archive_year(request,year,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,author=request.user).order_by('-today','-end_time')
    category_duration_dict=get_duration_for_categories(entryset)
    sorteddurations=sorted(category_duration_dict.items(),key=itemgetter(1),reverse=True)
    entries = get_pagination_entries(request, entryset)
    context={'sorteddurations':sorteddurations,'entries':entries,'year':year,'page_title':page_title}
    #context={'category_duration_dict':category_duration_dict,'sorteddurations':sorteddurations,'entries':entries,'year':year,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_month(request,year,month,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),author=request.user).order_by('-today','-end_time')
    category_duration_dict=get_duration_for_categories(entryset)
    entries = get_pagination_entries(request, entryset)
    sorteddurations=sorted(category_duration_dict.items(),key=itemgetter(1),reverse=True)
    context={'sorteddurations':sorteddurations,'entries':entries,'year':year,'month':month,'page_title':page_title}
    #context={'category_duration_dict':category_duration_dict,'entries':entries,'year':year,'month':month,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_day(request,year,month,day,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),today__day=day,author=request.user).order_by('-today','-end_time')
    category_duration_dict=get_duration_for_categories(entryset)
    entries = get_pagination_entries(request, entryset)
    sorteddurations=sorted(category_duration_dict.items(),key=itemgetter(1),reverse=True)
    context={'sorteddurations':sorteddurations,'entries':entries,'year':year,'month':month,'day':day,'page_title':page_title}
    #context={'category_duration_dict':category_duration_dict,'entries':entries,'year':year,'month':month,'day':day,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_detail(request,id,page_title,template_name):
    entry=get_object_or_404(PomEntry,id=id)
    if not canview(entry,request.user):
        raise Http404
    duration=timediff(entry.start_time,entry.end_time)
    context={'object':entry,'duration':duration,'page_title':page_title}
    return custom_render(request,context,template_name)

def canview(entry,user):
    if entry.author==user or user in entry.sharedwith.all():
        return True
    else:
        return False


def remove_index_key_from_cache(request):
    index_key = key_function([request.user.username],'index')
    if cache.has_key(index_key):
        cache.delete(index_key)

def remove_archive_index_key_from_cache(request):
    archive_index_key = key_function([request.user.username],'archive_index')
    if cache.has_key(archive_index_key):
        cache.delete(archive_index_key)

def remove_current_month_chart_key_from_cache(request):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    current_month_chart_key = key_function([request.user.username,str(year),str(month)],'current_month')
    if cache.has_key(current_month_chart_key):
        cache.delete(current_month_chart_key)

@login_required
@transaction.commit_on_success
def delete_entry(request,id):
    entry=get_object_or_404(PomEntry,id=id,author=request.user )
    #need to remove user from its categories
    #remove_user_from_categories(cats,request.user)
    entry.delete()
    #delete index key from cache
    remove_index_key_from_cache(request)
    remove_archive_index_key_from_cache(request)
    remove_current_month_chart_key_from_cache(request)
    #logger.debug("entry deleted")
    #remove categories that have no entries associated
    remove_lone_categories(request.user)
    return redirect('pomlog_entry_archive_index')


def remove_lone_categories(user):
    #print 'remove_lone_categories()'
    allcats=PomCategory.objects.filter(creator=user)
    for acat in allcats:
        entries_of_acat=PomEntry.objects.filter(categories=acat)
        if entries_of_acat.count()==0:
            acat.delete()
            #print 'deleted ',acat
def get_categories(user,catnames):
    cats=[]
    for name in catnames:
        if name and  not name.isspace():
            cat,status=PomCategory.objects.get_or_create(name__iexact=name.strip(),creator=user,defaults={'name':name,'description':name,'creator':user})# added creator
            cats.append(cat)
    return cats

@login_required
@transaction.commit_on_success
def add_new_entry(request,template_name,page_title):
    form_data = get_form_data(request)
    form = PomEntryDescForm(form_data)
    difficulty_form = PomEntryDifficultyForm(form_data)#added difficulty
    catnameform = PomCategoryNameForm(form_data)
    errorlist = []
    
    context={'page_title':page_title,'difficulty_form':difficulty_form,'entryform':form,'categoryform':catnameform,'errorlist':errorlist,'start_time_string':'','stop_time_string':'','form_errors':False}
    
    if request.method=='POST':
        start_time_string = request.POST[u'timerstarted']
        stop_time_string = request.POST[u'timerstopped']
        context['start_time_string'] = start_time_string
        context['stop_time_string'] = stop_time_string
        if  form.is_valid()  and catnameform.is_valid() and difficulty_form.is_valid():
            desc = form.cleaned_data['description']
            difficulty = difficulty_form.cleaned_data['difficulty']#added difficulty
            #print 'cleaned_data difficulty=',difficulty,'type=',type(difficulty)
            
            #print 'start_time_string=',start_time_string,len(start_time_string)
            #print 'stop_time_string=',stop_time_string,len(stop_time_string)
            if len(start_time_string)==0 or len(stop_time_string)==0:
                #print 'starttime and endtime cannot be empty'
                errorlist.append('starttime and endtime cannot be empty')
                return custom_render(request,context,template_name)
            start_time = long(start_time_string)
            stop_time = long(stop_time_string)
            if not (start_time < stop_time):
                #need to put this in errors
                errorlist.append('starttime should be less than endtime')
                return custom_render(request,context,template_name)
            try:
                start_ttpl,stop_ttpl = get_timetuples(start_time,stop_time)
                start_timeval=datetime.time(*start_ttpl)
                stop_timeval=datetime.time(*stop_ttpl)
            except ValueError:
                errorlist.append('format of time entries not correct')
                return custom_render(request,context,template_name)
            newentry=PomEntry(description=desc)
            newentry.save()
            newentry.start_time=start_timeval
            newentry.end_time=stop_timeval
            catnames=catnameform.cleaned_data['categories']
            catnames=get_list_of_names(catnames)
            cats=get_categories(request.user,catnames)#added user as creator
            """
            for x in cats:
                if request.user not in x.users.all():
                    x.users.add(request.user)#need to append, not assign
            """
            newentry.categories=cats
            newentry.author=request.user
            newentry.difficulty = difficulty#added difficulty
            #print 'before save with diff=',difficulty
            newentry.save()
            remove_index_key_from_cache(request)#removes index_key from cache
            remove_archive_index_key_from_cache(request)
            remove_current_month_chart_key_from_cache(request)
            #print 'newentry saved with diff=',difficulty
            return redirect('pomlog_entry_archive_index')
        else:
            context['form_errors']=True
            return custom_render(request,context,template_name)
    elif request.method == 'GET':
        return custom_render(request,context,template_name)

def get_timetuples(starttime,endtime):
    try:
        #start_l = list(time.strptime(starttime,fmtstr)[3:6])
        #starttime = long(starttime)
        start_time = datetime.datetime.fromtimestamp(starttime/1000.0)
        start_l = list(start_time.timetuple()[3:6])
        #logger.debug("start_l="+str(start_l))        
        #stop_l = list(time.strptime(endtime,fmtstr)[3:6])
        #endtime = long(endtime)
        stop_time = datetime.datetime.fromtimestamp(endtime/1000.0)
        stop_l = list(stop_time.timetuple()[3:6])
        #logger.debug("stop_l="+str(stop_l))
        start_ttpl = tuple(start_l)
        #logger.debug("start_ttpl="+str(start_ttpl))
        stop_ttpl = tuple(stop_l)
        #logger.debug("stop_ttpl="+str(stop_ttpl))
    except ValueError as verr:
        #logger.debug("valueError in get_timetuples",verr)
        raise ValueError
    return (start_ttpl,stop_ttpl)

def get_category_names_as_one_string(categorynameslist):
    return ','.join(categorynameslist)

def get_list_of_names(names):
    '''
    from a given string of comma separated names return a list of names
    '''
    return [x.strip() for x in names.split(',') if len( x.strip())  !=0]

def add_user_to_categories(categories,user):
    if categories:
        for acat in categories:
            if user not in acat.users.all():
                acat.users.add(user)

def remove_user_from_categories(categories,user):
    if categories:
        for acat in categories:
            if user in acat.users.all():
                acat.users.remove(user)

@login_required
@transaction.commit_on_success
def edit_entry(request,id,template_name,page_title):
    #print 'edit_entry()::id=',id
    entry=get_object_or_404(PomEntry,id=id,author=request.user)
    #print 'edit_entry()::entry=',entry
    old_categorynames_list=[x.name for x in entry.categories.all()]
    #print 'edit_entry()::old_categorynames_list=',old_categorynames_list    
    categorynames_as_one_string=get_category_names_as_one_string(old_categorynames_list)
    categorynamesdata={'categories':categorynames_as_one_string}
    form_data=get_form_data(request)
    form=PomEntryEditForm(form_data,instance=entry)#try not allowing today,start,end times etc be edited
    
    catnameform=PomCategoryNameForm(form_data,initial=categorynamesdata)
    context={'entryform':form,'categoryform':catnameform,'page_title':page_title}
    form_valid=form.is_valid()
    catnameform_valid=catnameform.is_valid()
    #print 'edit_entry()::catnameform_valid=',catnameform_valid
    #print 'edit_entry()::form_valid=',form_valid
    #print 'for errors=',form.errors
    #print 'edit_entry()::request.method=',request.method
    if request.method=='POST' and form_valid and catnameform_valid:
        #print 'edit_entry()::POST:today=',request.POST['today']
        #print 'edit_entry()::POST:start_time=',request.POST['start_time']
        #print 'edit_entry()::POST:end_time=',request.POST['end_time']
        edited_entry=form.save()
        #print 'edit_entry()::edited_entry=',edited_entry
        catnames=catnameform.cleaned_data['categories']
        #print 'edit_entry()::catnames=',catnames
#        new_categorynames_list=get_list_of_names(catnames)
#        newlyaddedcatnames=set(new_categorynames_list)-set(old_categorynames_list)
#        newlyaddedcatnames=list(newlyaddedcatnames)
#        removedcatnames=set(old_categorynames_list)-set(new_categorynames_list)
#        removedcatnames=list(removedcatnames)
        #print 'edit_entry()::removedcatnames=',removedcatnames
        #for each name in newlyaddedcatnames,get or create category object, add this user in its users field
#        if newlyaddedcatnames:
#            newlyaddedcats=get_categories(newlyaddedcatnames)
#            add_user_to_categories(newlyaddedcats,request.user)
#        #for each name in removedcatnames ,get category object ,remove this user from its users field
#        if removedcatnames:
#            removedcats=get_categories(removedcatnames)
#            #print 'edit_entry()::removedcats=',removedcats
#            remove_user_from_categories(removedcats,request.user)
        cats=get_categories(request.user,get_list_of_names(catnames))
        edited_entry.categories=cats
        edited_entry.save()
        remove_archive_index_key_from_cache(request)#remove archive index key
        remove_index_key_from_cache(request)#check this needed?
        remove_current_month_chart_key_from_cache(request)
        remove_lone_categories(request.user)#update to remove cats with no entries           
        return redirect('pomlog_entry_archive_index')
    return custom_render(request,context,template_name)

def update_cats_with_editable_status(user,categories):
    cats={}
    for cat in categories:
        usrcnt=cat.users.count()
        allcatusrs=cat.users.all()
        user_in_users=user in allcatusrs
        entries_of_cat=PomEntry.objects.filter(categories=cat)
        edit_status=False        
        if usrcnt==1 and user in allcatusrs:
            #print '1 usr only..setting edit=True'
            edit_status=True
        cats[cat]=edit_status
    return cats

def get_categories_of_user(user):
    owncats= PomCategory.objects.filter(creator=user)
    return list(set(owncats))

@login_required
def category_list(request,template_name,page_title):
    categories=get_categories_of_user(request.user)
    #cats_with_status=update_cats_with_editable_status(request.user,categories)
    #category_list_dict={'page_title':page_title ,'cats_status':cats_with_status}
    category_list_dict={'page_title':page_title ,'cats':categories}
    return custom_render(request,category_list_dict,template_name)

@login_required
def category_detail(request,slug,template_name,page_title):
    category=get_object_or_404(PomCategory,slug=slug,creator=request.user)
    now=datetime.datetime.now()
    entryset=PomEntry.objects.filter(categories=category,author=request.user).order_by('-today','-end_time')
    category_duration_dict=get_duration_for_categories(entryset)
    entries = get_pagination_entries(request, entryset)
    
    context={'object':category,'now':now,'category_duration_dict':category_duration_dict,'entries':entries,'page_title':page_title}
    return custom_render(request,context,template_name)


@login_required
@transaction.commit_on_success
def delete_category(request,slug):
    cat=get_object_or_404(PomCategory,slug=slug,creator=request.user)
    if cat.pomentry_set.count()==0:
        cat.delete()
        #logger.info('deleted category:'+slug)
    else:
        pass
        #logger.info('cannot delete category')
    return redirect('pomlog_category_list')



def is_duplicate_cat(user,name):
    if PomCategory.objects.filter(name__iexact=name,creator=user).count()!=0:
        return True
    else:
        return False
@transaction.commit_on_success
def add_or_edit(request,page_title,template_name,instance=None):
    form_data=get_form_data(request)
    form=PomCategoryForm(form_data,instance=instance)
    context={'categoryform':form,'page_title':page_title}
    if request.method=='POST' and form.is_valid():
        name=form.cleaned_data['name']
        name=name.strip()
        if is_duplicate_cat(request.user,name):
            if instance!=None:
                form.save()
                return redirect('pomlog_category_list')
            else:
                return custom_render(request,context,template_name)
        else:
            form.save()
            return redirect('pomlog_category_list') 
    return custom_render(request,context,template_name)

@login_required
def add_category(request,template_name,page_title):
    return add_or_edit(request,page_title,template_name) 



@login_required
def edit_category(request,slug,template_name,page_title):
    cat=get_object_or_404(PomCategory,slug=slug,creator=request.user)
    return add_or_edit(request,page_title,template_name,instance=cat)


@login_required
def list_entries_of_category(request,slug,template_name,page_title):
    cat = get_object_or_404(PomCategory,slug=slug,creator=request.user)
    entryset=PomEntry.objects.filter(categories=cat,author=request.user).order_by('-today','-end_time')
    category_duration_dict=get_duration_for_categories(entryset)
    entries = get_pagination_entries(request, entryset)
    context={'category_duration_dict':category_duration_dict,'entries':entries,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def get_form_data(request):
    return request.POST if request.method=='POST' else None


def get_own_entries_with_cats(cats,user):
    ownentries_with_cats=[]
    for cat in cats:
        entries=PomEntry.objects.filter(categories=cat).filter(author=user)
        ownentries_with_cats.extend(entries)
    return list(set(ownentries_with_cats))


@login_required
def share_entries(request,template_name,page_title):
    allusers=User.objects.all()
    others=User.objects.exclude(username=request.user.username)
    ownentries=PomEntry.objects.filter(author=request.user)
    owncats=get_categories_of_user(request.user)
    form_data=get_form_data(request)
    form=PomEntryShareForm(form_data,request)
    context={'ownentries':ownentries,'otherusers':others,'allusers':allusers,'page_title':page_title,'sharemyentryform':form}
    selected_entries=None
    if request.method=='POST' and form.is_valid():
        if form.cleaned_data['sharing_options']==u'selectedentries':
            selected_entries=form.cleaned_data['entries_selected']
            
        elif form.cleaned_data['sharing_options']==u'allentries':
            selected_entries=ownentries

        elif form.cleaned_data['sharing_options']==u'entriesofcat':
            selected_cats=form.cleaned_data['categories_selected']
            selected_entries=get_own_entries_with_cats(selected_cats,request.user)
        
        users_to_sharewith=form.cleaned_data['users_selected']
        
        share_entries_with_users(selected_entries,users_to_sharewith)
        return redirect('pomlog_entry_archive_index')

    return custom_render(request,context,template_name)

def share_entries_with_users(entries,users):
    for entry in entries:
        for user in users:
            share_entry_with_user(entry,user)

def share_entry_with_user(entry,user):
    if not is_shared(entry,user):
        entry.sharedwith.add(user)

def is_shared(entry,user):
    if user in entry.sharedwith.all():
        return True
    else:
        return False

@login_required
def unshare_entry(request,entryid,userid):
    entry=get_object_or_404(PomEntry,id=entryid,author=request.user)
    user=get_object_or_404(User,id=userid)
    if is_shared(entry,user):
        entry.sharedwith.remove(user)
    return redirect('pomlog_entry_archive_index')

#reports
@login_required
def reports(request,page_title,template_name):
    currentyear = datetime.datetime.today().year
    oldyear = currentyear-5
    days=[x for x in range(1,32)]
    years=[x+oldyear for x in range(10)]
    months = list(calendar.month_abbr)[1:]
    datemap = {'years':years,'months':months,'days':days}
    year = request.GET.get('year')
    month =  request.GET.get('month')
    day = request.GET.get('day')
    if day:
        return redirect('pomlog_report_entries_for_day',year=year,month=month,day=day)
    return custom_render(request,datemap,template_name)


@login_required
def report_entries_for_day(request,year,month,day,page_title,template_name):
    monthname = month
    month = get_month_as_number(monthname)
    page_title = page_title+" "+day+"-"+monthname+"-"+year
    entrycount=PomEntry.objects.filter(author=request.user,today__year=year,today__month=month,today__day=day).count()
    context=dict(year=year,month=monthname,day=day,page_title=page_title,entrycount=entrycount)
    return custom_render(request,context,template_name)

@login_required
def render_graph_for_day(request,year,month,day):
    month = get_month_as_number(month)
    entryset=PomEntry.objects.filter(today__year=year,today__month=month,today__day=day,author=request.user).order_by('today','start_time')
    #entry_duration_dict = get_durations_for_entries(entryset)
    entry_duration_dict = get_durations_for_entries(entryset)
    #category_duration_dict = get_duration_for_categories(entryset)
    canvas = create_chart(CHART_TYPE,entry_duration_dict)
    response = HttpResponse(content_type = 'image/png')
    canvas.print_png(response)
    return response
    
def create_chart(chart_type,map):
    if chart_type is "bar":
        return create_barchart(map)
    elif chart_type is "pie":
        return create_piechart(map)

def create_barchart(map):
    now = datetime.datetime.now().strftime("%I:%M:%S %p   %d %b,%Y")
    xvalues = map.keys()
    #sort in asc order of date,time
    xvalues.sort(key = lambda e:datetime.datetime.combine(e.today,e.start_time))
    xvaluenames = [xvalue.__unicode__() for xvalue in xvalues]
    #print 'xvaluenames=',xvaluenames
    yvalues = map.values()
    #print 'yvalues=',yvalues
    maxyvalue = get_max_value(yvalues)
    #print 'maxyvalue=',maxyvalue
    xdata = range(len(xvalues))
    #print 'xdata=',xdata
    ydata = [map[x] for x in xvalues]
    #print 'ydata=',ydata
    min_x,max_x = get_extreme_values(xdata)
    #print 'min_x,max_x=',min_x,max_x
    splitxdata = [x.split('-',1) for x in xvaluenames]
    #print 'splitxdata=',splitxdata
    xlabels = [x[0].split()[0] for x in splitxdata]
    #print 'xlabels=',xlabels
    dates = [x[1] for x in splitxdata if len(x)>1]
    figsize= (12,6)
    figure = plt.figure(figsize = figsize, facecolor = "white")
    ax = figure.add_subplot(1,1,1)
    barwidth = BAR_WIDTH
    ystep = create_ystep(maxyvalue)
    plt.grid(True)
    if xdata and ydata:
        ax.bar(xdata, ydata, width=barwidth,align='center',color=BAR_COLOR)
        ax.set_xlabel('categories',color=LABEL_COLOR)
        ax.set_ylabel('duration in  minutes',color=LABEL_COLOR)
        ax.set_title('duration plot created at :'+now,color=TITLE_COLOR)
        ax.set_xticks(xdata)
        #ax.set_xbound(-1.0 ,5.0)#scaling xaxis -check this
        #ax.set_xlim([min_x - PLOT_OFFSET, max_x + PLOT_OFFSET])
        ax.set_xlim(-1,len(xdata))
        ax.set_xticklabels(xlabels)
        if ystep:
            ax.set_yticks(range(0,maxyvalue+ystep,ystep))
            ax.set_ylim(0,max(ydata)+ystep)
        figure.autofmt_xdate(rotation=30)
        canvas = FigureCanvas(figure)
        plt.close(figure)
        return canvas
    
    
def create_barchart_old(map):
    now = datetime.datetime.now().strftime("%I:%M:%S %p   %d %b,%Y")
    xvalues = map.keys()
    xvalues.sort()
    yvalues = map.values()
    maxyvalue = get_max_value(yvalues)
    xdata = range(len(xvalues))
    ydata = [map[x] for x in xvalues]
    min_x,max_x = get_extreme_values(xdata)
    splitxdata = [x.split('-',1) for x in xvalues]
    xlabels = [x[0].split()[0] for x in splitxdata] 
    dates = [x[1] for x in splitxdata if len(x)>1]
    figsize= calculate_plotfigure_size(len(xvalues))
    figure = plt.figure(figsize = figsize, facecolor = "white")
    ax = figure.add_subplot(1,1,1)
    barwidth = BAR_WIDTH
    ystep = create_ystep(maxyvalue)
    plt.grid(True)
    if xdata and ydata:
        ax.bar(xdata, ydata, width=barwidth,align='center',color=BAR_COLOR)
        ax.set_xlabel('categories',color=LABEL_COLOR)
        ax.set_ylabel('duration in  minutes',color=LABEL_COLOR)
        ax.set_title('duration plot created at :'+now,color=TITLE_COLOR)
        ax.set_xticks(xdata)
        ax.set_xlim([min_x - PLOT_OFFSET, max_x + PLOT_OFFSET])
        ax.set_xticklabels(xlabels)
        if ystep:
            ax.set_yticks(range(0,maxyvalue+ystep,ystep))
            ax.set_ylim(0,max(ydata)+ystep)
        figure.autofmt_xdate(rotation=30)
        canvas = FigureCanvas(figure)
        plt.close(figure)
        return canvas

@login_required
def categories_report(request,page_title,template_name):
    report_data={'page_title':page_title}
    entrycount=PomEntry.objects.filter(author=request.user).count()
    report_data["entrycount"]=entrycount
    return custom_render(request,report_data,template_name)

@login_required
def render_categories_chart(request):
    entryset=PomEntry.objects.filter(author=request.user)
    category_duration_dict = get_duration_for_categories(entryset)
    canvas = None
    if category_duration_dict:
        canvas = create_piechart(category_duration_dict,chartsize=(8,8))
    response = HttpResponse(content_type = 'image/png')
    if canvas:
        canvas.print_png(response)
    return response

@login_required
def render_categories_chart_for_current_month(request):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    current_month_chart_key = key_function([request.user.username,str(year),str(month)],'current_month')
    entryset  = cache.get(current_month_chart_key) if cache.has_key(current_month_chart_key) else None
    if not entryset:
        entryset = PomEntry.objects.filter(today__year=year,today__month=month,author=request.user).order_by('-today','-end_time')
        cache.set(current_month_chart_key,entryset )
    category_duration_dict = get_duration_for_categories(entryset)
    canvas = None
    if category_duration_dict:
        canvas = create_piechart(category_duration_dict,chartsize=(8,8))
    response = HttpResponse(content_type = 'image/png')
    if canvas:
        canvas.print_png(response)
    return response

"""
@login_required
def render_categories_chart_for_current_month(request):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    entryset = PomEntry.objects.filter(today__year=year,today__month=month,author=request.user).order_by('-today','-end_time')
    category_duration_dict = get_duration_for_categories(entryset)
    canvas = None
    if category_duration_dict:
        canvas = create_piechart(category_duration_dict,chartsize=(8,8))
    response = HttpResponse(content_type = 'image/png')
    if canvas:
        canvas.print_png(response)
    return response
"""
#untested
@login_required
def render_categories_chart_for_month(request,month):
    now = datetime.datetime.now()
    year = now.year
    entryset = PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),author=request.user).order_by('-today','-end_time')
    category_duration_dict = get_duration_for_categories(entryset)
    canvas = None
    if category_duration_dict:
        canvas = create_piechart(category_duration_dict,chartsize=(8,8))
    response = HttpResponse(content_type = 'image/png')
    if canvas:
        canvas.print_png(response)
    return response

def create_piechart(map,chartsize=(16,16)):
    now = datetime.datetime.now().strftime("%I:%M:%S %p   %d %b,%Y")
    xvalues = map.keys()
    xvalues.sort()
    yvalues = map.values()
    sum_y = sum(yvalues)
    sum_y = float(sum_y)
    xdata = range(len(xvalues))
    ydata = [map[x] for x in xvalues]
    if xdata and ydata:
        splitxdata = [x.split('-',1) for x in xvalues]
        xlabels = [x[0] for x in splitxdata]
        dates = [x[1] for x in splitxdata if len(x)>1]
        figsize= chartsize
        figure = plt.figure(figsize = figsize)
        ax = figure.add_subplot(1,1,1)
        fracs=[x*100/sum_y for x in ydata]
        labels=[x for x in xlabels]
        #need to add text with dates
        plt.pie(fracs, labels=labels, autopct='%1.1f%%', shadow=True)
        title('duration pie plot')
        canvas = FigureCanvas(figure)
        plt.close(figure)
        return canvas

def create_ystep(maxvalue):
    return  maxvalue if maxvalue < YSTEP_FACTOR else maxvalue/YSTEP_FACTOR
        
def get_max_value(values):
    return max(values) if values  else 0
def get_extreme_values(data):
    if data:
        min_x = min(data)
        max_x = max(data)
    else:
        min_x = max_x = 0
    return min_x,max_x

def calculate_plotfigure_size(number_of_entries):
    "if number of entries are small use default 8,6 size ,else scale the width a bit"
    if number_of_entries < FIGURE_WIDTH_SCALE_FACTOR:
        return 8,6
    else:
        widthscale = number_of_entries/FIGURE_WIDTH_SCALE_FACTOR
        figsize = (8*widthscale,6)
        return figsize

