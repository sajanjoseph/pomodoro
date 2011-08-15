from pomlogger.models import PomEntry,PomCategory
from pomlogger.models import PomEntryForm,PomCategoryForm,PomCategoryNameForm,PomEntryShareForm
from pomlogger.models import PomEntryDescForm
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect,Http404
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

from django.contrib.auth.models import User
import settings

import logging
import matplotlib.pyplot as plt
import pylab
from matplotlib.backends.backend_pdf import PdfPages

logger = logging.getLogger("pomodoro")

@login_required
def index(request, template_name):
    print 'index()::template=',template_name
    return custom_render(request, {},template_name )

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

def get_durations_for_entries(entryset):
    entry_duration_dict={}
    for anentry in entryset:
        duration_mts=timediff(anentry.start_time,anentry.end_time)
        entry_duration_dict[anentry.__unicode__() ] = duration_mts
    return entry_duration_dict

def custom_render(request,context,template):
    req_context=RequestContext(request,context)
    return render_to_response(template,req_context)

@login_required
def entry_archive_index(request,page_title,template_name):
    entryset=PomEntry.objects.filter(author=request.user).order_by('-today','-start_time')
    entry_duration_dict=get_duration_for_categories(entryset)
    now=datetime.datetime.now()
    entries_sharedto_me=PomEntry.objects.filter(sharedwith=request.user).order_by('-today','-start_time')#added for sharing
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'entries_sharedto_me':entries_sharedto_me,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_year(request,year,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,author=request.user).order_by('-today','-start_time')
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_month(request,year,month,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),author=request.user).order_by('-today','-start_time')
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'month':month,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_day(request,year,month,day,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),today__day=day,author=request.user).order_by('-today','-start_time')
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'month':month,'day':day,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_detail(request,id,page_title,template_name):
    print 'entry_detail()::'
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

@login_required
@transaction.commit_on_success
def delete_entry(request,id):
    entry=get_object_or_404(PomEntry,id=id,author=request.user )
    print 'delete_entry()::entry=',entry
    #need to remove user from its categories
    cats=entry.categories.all()
    print 'delete_entry()::cats=',cats
    remove_user_from_categories(cats,request.user)
    entry.delete()
    print 'entry deleted'
    #remove categories that have no entries associated
    remove_lone_categories()
    return redirect('pomlog_entry_archive_index')


def remove_lone_categories():
    print 'remove_lone_categories()'
    allcats=PomCategory.objects.all()
    for acat in allcats:
        entries_of_acat=PomEntry.objects.filter(categories=acat)
        if entries_of_acat.count()==0:
            acat.delete()
            print 'deleted ',acat


def get_categories(catnames):
    cats=[]
    for name in catnames:
        if name and  not name.isspace():
            cat,status=PomCategory.objects.get_or_create(name__iexact=name.strip(),defaults={'name':name,'description':name})# if no defaults ,IntegrityError
            cats.append(cat)
    return cats

@login_required
@transaction.commit_on_success
def add_new_entry(request,template_name,page_title):
    form_data=get_form_data(request)
    form=PomEntryDescForm(form_data)
    catnameform=PomCategoryNameForm(form_data)
    errorlist=[]   
    context={'page_title':page_title,'entryform':form,'categoryform':catnameform,'errorlist':errorlist}
    if request.method=='POST' and form.is_valid() and catnameform.is_valid():
        desc=form.cleaned_data['description']
        start_time=request.POST[u'timerstarted']
        stop_time=request.POST[u'timerstopped']
        
        try:
            logger.debug("start_time is="+start_time)
            logger.debug("stop_time is="+stop_time)
            start_ttpl,stop_ttpl = get_timetuples(start_time,stop_time)
            logger.debug("start_ttpl="+str(start_ttpl))
            logger.debug("stop_ttpl="+str(stop_ttpl))
            
            start_timeval=datetime.time(*start_ttpl)
            stop_timeval=datetime.time(*stop_ttpl)
            
            logger.debug("start_timeval="+str(start_timeval))
            logger.debug("stop_timeval="+str(stop_timeval))
            print 'start_timeval=',start_timeval
            print 'stop_timeval=',stop_timeval
            if not (start_timeval < stop_timeval):
                #need to put this in errors
                logger.debug('starttime should be less than endtime')
                errorlist.append('starttime should be less than endtime')
                return custom_render(request,context,template_name)
        except ValueError:
            print 'add_new_entry()::format not correct'
            logger.debug('add_new_entry()::format not correct')
            #need to put this in errors
            errorlist.append('format of time entries not correct')
            return custom_render(request,context,template_name)
        
        newentry=PomEntry(description=desc)
        newentry.save()
        
        newentry.start_time=start_timeval
        newentry.end_time=stop_timeval
        newentry.save()
        catnames=catnameform.cleaned_data['categories']
        catnames=get_list_of_names(catnames)            
        cats=get_categories(catnames)
        for x in cats:
            if request.user not in x.users.all():
                x.users.add(request.user)#need to append, not assign
        newentry.categories=cats
        newentry.author=request.user
        newentry.save()
        print 'redirecting to index'
        return redirect('pomlog_entry_archive_index')
    return custom_render(request,context,template_name)

def get_timetuples(starttime,endtime):
    try:
        #start_l = list(time.strptime(starttime,fmtstr)[3:6])
        starttime = long(starttime)
        start_time = datetime.datetime.fromtimestamp(starttime/1000.0)
        start_l = list(start_time.timetuple()[3:6])
        logger.debug("start_l="+str(start_l))
        
        print 'get_timetuples()::start_l=',start_l;
        #stop_l = list(time.strptime(endtime,fmtstr)[3:6])
        endtime = long(endtime)
        stop_time = datetime.datetime.fromtimestamp(endtime/1000.0)
        stop_l = list(stop_time.timetuple()[3:6])
        logger.debug("stop_l="+str(stop_l))
        print 'get_timetuples()::stop_l=',stop_l;
        start_ttpl = tuple(start_l)
        logger.debug("start_ttpl="+str(start_ttpl))
        stop_ttpl = tuple(stop_l)
        logger.debug("stop_ttpl="+str(stop_ttpl))
    except ValueError:
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
    entry=get_object_or_404(PomEntry,id=id,author=request.user)
    old_categorynames_list=[x.name for x in entry.categories.all()]    
    categorynames_as_one_string=get_category_names_as_one_string(old_categorynames_list)
    categorynamesdata={'categories':categorynames_as_one_string}
    form_data=get_form_data(request)
    form=PomEntryForm(form_data,instance=entry)
    catnameform=PomCategoryNameForm(form_data,initial=categorynamesdata)
    context={'entryform':form,'categoryform':catnameform,'page_title':page_title}
    form_valid=form.is_valid()
    catnameform_valid=catnameform.is_valid()
    if request.method=='POST' and form_valid and catnameform_valid:
        edited_entry=form.save()
        catnames=catnameform.cleaned_data['categories']
        new_categorynames_list=get_list_of_names(catnames)
        newlyaddedcatnames=set(new_categorynames_list)-set(old_categorynames_list)
        newlyaddedcatnames=list(newlyaddedcatnames)
        removedcatnames=set(old_categorynames_list)-set(new_categorynames_list)
        removedcatnames=list(removedcatnames)
        #for each name in newlyaddedcatnames,get or create category object, add this user in its users field
        if newlyaddedcatnames:
            newlyaddedcats=get_categories(newlyaddedcatnames)
            add_user_to_categories(newlyaddedcats,request.user)
        #for each name in removedcatnames ,get category object ,remove this user from its users field
        if removedcatnames:
            removedcats=get_categories(removedcatnames)
            remove_user_from_categories(removedcats,request.user)
        cats=get_categories(get_list_of_names(catnames))
        edited_entry.categories=cats
        edited_entry.save()
        remove_lone_categories()#update to remove cats with no entries           
        return redirect('pomlog_entry_archive_index')
    return custom_render(request,context,template_name)

def update_cats_with_editable_status(user,categories):
    print 'update_cats_with_editable_status()::'
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

'''
def update_cats_with_editable_status(user,categories):
    print 'update_cats_with_editable_status()::'
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
'''
'''
def update_cats_with_editable_status_old(user,categories):
    print 'update_cats_with_editable_status()::'
    cats={}
    for cat in categories:
        usrcnt=cat.users.count()
        allcatusrs=cat.users.all()
        user_in_users=user in allcatusrs
        entries_of_cat=PomEntry.objects.filter(categories=cat)
        edit_delete_status=[False,False]
        if entries_of_cat.count()==0:
            #print 'entries_of_cat.count()==%d'%entries_of_cat.count()
            #print 'setting edit=True,delete=True'
            edit_delete_status[0]=True
            edit_delete_status[1]=True
        if usrcnt==1 and user in allcatusrs:
            #print '1 usr only..setting edit=True'
            edit_delete_status[0]=True
        cats[cat]=edit_delete_status
        #print 'for',cat,' edit_delete_status=',edit_delete_status
    return cats
'''

def get_categories_of_user(user):
    ownentries=PomEntry.objects.filter(author=user)
    owncats=[]
    for entry in ownentries:
        catsofentry=entry.categories.all()
        owncats.extend(catsofentry)
    return list(set(owncats))

@login_required
def category_list(request,template_name,page_title):
    categories=get_categories_of_user(request.user)
    print 'categories=',categories
    #cats_with_status=update_cats_with_editable_status(request.user,categories)
    #category_list_dict={'page_title':page_title ,'cats_status':cats_with_status}
    category_list_dict={'page_title':page_title ,'cats':categories}
    return custom_render(request,category_list_dict,template_name)

@login_required
def category_detail(request,slug,template_name,page_title):
    category=get_object_or_404(PomCategory,slug=slug,users=request.user)
    now=datetime.datetime.now()
    context={'object':category,'now':now, 'page_title': page_title}
    return custom_render(request,context,template_name)



@login_required
@transaction.commit_on_success
def delete_category(request,slug):
    cat=get_object_or_404(PomCategory,slug=slug)
    if cat.users.count()==1 and request.user in cat.users.all():
        cat.delete()
        print 'cat deleted'
    else:
        print 'cannot delete category'       
    return redirect('pomlog_category_list')


def is_duplicate_cat(name):
    if PomCategory.objects.filter(name__iexact=name).count()!=0:
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
        if is_duplicate_cat(name):
            if instance!=None:
                print 'we want to edit %s'%name
                form.save()
                return redirect('pomlog_category_list')
            else:
                return custom_render(request,context,template_name)
        else:
            print 'we are adding a new cat %s'%name
            form.save()
            return redirect('pomlog_category_list') 
    return custom_render(request,context,template_name)



@login_required
def add_category(request,template_name,page_title):
    return add_or_edit(request,page_title,template_name) 

def has_permission(user,category):
    catsofuser=get_categories_of_user(user)
    return (category in catsofuser)

'''
def has_permission(user,category):
    return (category.users.count()==1  or category.users.count()==0 )and user in category.users.all()
'''

@login_required
def edit_category(request,slug,template_name,page_title):
    cat=get_object_or_404(PomCategory,slug=slug)
    if has_permission(request.user,cat):
        print 'edit_category()::user has permission'
        return add_or_edit(request,page_title,template_name,instance=cat)
    else:
        print 'edit_category()::user has no permission..raising 404'
        raise Http404


@login_required
def get_form_data(request):
    return request.POST if request.method=='POST' else None


def get_categories_from_idstring(cat_id_list):
    cats=[]
    for id in cat_id_list:
        print 'id is=',id,type(id)
        cat=PomCategory.objects.get(id=id)
        print 'cat=',cat,type(cat)
        cats.append(cat)

    print 'cats=',cats
    return cats

def get_entries_from_idstring(entry_id_list):
    entries=[]
    for id in entry_id_list:
        print 'id is=',id,type(id)
        entry=PomEntry.objects.get(id=id)
        print 'entry=',entry,type(entry)
        entries.append(entry)
    return entries

def get_own_entries_with_cats(cats,user):
    ownentries_with_cats=[]
    for cat in cats:
        entries=PomEntry.objects.filter(categories=cat).filter(author=user)
        ownentries_with_cats.extend(entries)

    return list(set(ownentries_with_cats))


@login_required
def share_entries(request,template_name,page_title):
    print 'share_entries()::'  
    allusers=User.objects.all()
    others=User.objects.exclude(username=request.user.username)
    ownentries=PomEntry.objects.filter(author=request.user)
    owncats=get_categories_of_user(request.user)
    form_data=get_form_data(request)
    form=PomEntryShareForm(form_data,request)
    context={'ownentries':ownentries,'otherusers':others,'allusers':allusers,'page_title':page_title,'sharemyentryform':form}
    selected_entries=None
    if request.method=='POST' and form.is_valid():
        print 'POST::form.cleaned_data:',form.cleaned_data
        print 'you selected radio option:%s'% form.cleaned_data['sharing_options']
        if form.cleaned_data['sharing_options']==u'selectedentries':
            print 'you chose the share multiple entries..'
            selected_entries=form.cleaned_data['entries_selected']
            print 'your selection=' ,selected_entries,type(selected_entries)
            
        elif form.cleaned_data['sharing_options']==u'allentries':
            print 'you chose the share all entries..'
            selected_entries=ownentries
            print 'your selection=' ,selected_entries,type(selected_entries)

        elif form.cleaned_data['sharing_options']==u'entriesofcat':
            print 'you chose the share entries with categories..'
            selected_cats=form.cleaned_data['categories_selected']
            print 'your selection of cats=',selected_cats
            selected_entries=get_own_entries_with_cats(selected_cats,request.user)
            print 'your selection of entries=',selected_entries
        
        users_to_sharewith=form.cleaned_data['users_selected']
        
        print 'you have chosen to share:' ,selected_entries,type(selected_entries)
        print 'with these users:' ,users_to_sharewith,type(users_to_sharewith)
        share_entries_with_users(selected_entries,users_to_sharewith)
        return redirect('pomlog_entry_archive_index')

    print 'GET or invalid post data'
    return custom_render(request,context,template_name)

def share_entries_with_users(entries,users):
    for entry in entries:
        for user in users:
            share_entry_with_user(entry,user)

def share_entry_with_user(entry,user):
    if not is_shared(entry,user):
        entry.sharedwith.add(user)
    else:
        print 'the entry:',entry,' is already shared with user:',user

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
    elif month:
        return redirect('pomlog_report_entries_for_month',year=year,month=month)
    elif year :
        return redirect('pomlog_report_entries_year',year=year)
    return custom_render(request,datemap,template_name)

@login_required
def report_entries_for_day(request,year,month,day,page_title,template_name):
    monthname = month
    month = get_month_as_number(month)
    entryset=PomEntry.objects.filter(today__year=year,today__month=month,today__day=day,author=request.user)
    entry_duration_dict = get_durations_for_entries(entryset)
    basefilename = "entriesofday%s-%s-%s"%(year,month,day)
    page_title = page_title+" "+day+"-"+monthname+"-"+year
    imgfilename,docfilename = create_chart(settings.CHART_TYPE,entry_duration_dict,basefilename)
    report_data={'basefilename':basefilename,'report_image':imgfilename,'report_doc':docfilename,'page_title':page_title,'year':year,'month':monthname,'day':day}
    report_data["entry_duration_dict"]=entry_duration_dict
    return custom_render(request,report_data,template_name)

@login_required
def report_entries_for_month(request,year,month,page_title,template_name):
    monthname = month
    month = get_month_as_number(month)
    entryset=PomEntry.objects.filter(today__year=year,today__month=month,author=request.user)
    entry_duration_dict = get_durations_for_entries(entryset)
    basefilename = "entriesofmonth%s-%s"%(monthname,year)
    page_title = page_title+" "+monthname+"-"+year
    imgfilename,docfilename = create_chart(settings.CHART_TYPE,entry_duration_dict,basefilename)
    report_data={'basefilename':basefilename,'report_image':imgfilename,'report_doc':docfilename,'page_title':page_title,'year':year,'month':monthname}
    report_data["entry_duration_dict"]=entry_duration_dict
    return custom_render(request,report_data,template_name)

@login_required
def report_entries_for_year(request,year,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,author=request.user)
    entry_duration_dict = get_durations_for_entries(entryset)
    basefilename = "entriesofyear%s"%year
    page_title = page_title+" "+year
    imgfilename,docfilename = create_chart(settings.CHART_TYPE,entry_duration_dict,basefilename)
    report_data={'basefilename':basefilename,'report_image':imgfilename,'report_doc':docfilename,'page_title':page_title,'year':year}
    report_data["entry_duration_dict"]=entry_duration_dict
    return custom_render(request,report_data,template_name)

@login_required
def entries_report(request,page_title,template_name):
    entryset=PomEntry.objects.filter(author=request.user)
    entry_duration_dict = get_durations_for_entries(entryset)
    basefilename = "allentriesreport"
    imgfilename,docfilename = create_chart(settings.CHART_TYPE,entry_duration_dict,basefilename)
    report_data={'basefilename':basefilename,'report_image':imgfilename,'report_doc':docfilename,'page_title':page_title}
    report_data["entry_duration_dict"]=entry_duration_dict
    return custom_render(request,report_data,template_name)

@login_required
def categories_report(request,page_title,template_name):
    entryset=PomEntry.objects.filter(author=request.user)
    entry_duration_dict = get_duration_for_categories(entryset)
    basefilename = "allcategoriesreport"
    imgfilename,docfilename = create_chart(settings.CHART_TYPE,entry_duration_dict,basefilename)
    report_data={'basefilename':basefilename,'report_image':imgfilename,'report_doc':docfilename,'page_title':page_title}
    report_data["entry_duration_dict"]=entry_duration_dict
    return custom_render(request,report_data,template_name)
    
def create_chart(chart_type,map,basefilename):
    if chart_type is "bar":
        return create_barchart(map,basefilename)
    elif chart_type is "pie":
        return create_piechart(map,basefilename)
        
def create_piechart(map,basefilename):
    pass
      
def create_barchart(map,basefilename):
    now = datetime.datetime.now().strftime("%I-%M-%S%p-%d%b%Y")
    imgfilename = settings.IMAGE_FOLDER_PATH+"/"+basefilename+".png"
    docfilename = settings.IMAGE_FOLDER_PATH+"/"+basefilename+".pdf"
    catnames = map.keys()
    catnames.sort()
    durations = map.values()
    maxduration = get_max_duration(durations)
    xdata = range(len(catnames))
    ydata = [map[x] for x in catnames]
    min_x,max_x = get_extreme_values(xdata)
    splitxdata = [x.split('-',1) for x in catnames]
    xlabels = [x[0] for x in splitxdata]
    dates = [x[1] for x in splitxdata if len(x)>1]
    figure = pylab.figure()
    ax = figure.add_subplot(1,1,1)
    barwidth = 0.25
    ystep =  maxduration/10
    pylab.grid(True)
    if xdata and ydata:
        ax.bar(xdata, ydata, width=barwidth,align='center',color='magenta')
        ax.set_xlabel('categories',color='green')
        ax.set_ylabel('durations in  minutes',color='green')
        ax.set_title('durations for categories-created at :'+now,color='blue')
        ax.set_xticks(xdata)
        ax.set_xlim([min(xdata) - 0.5, max(xdata) + 0.5])
        ax.set_xticklabels(xlabels)
        ax.set_yticks(range(0,maxduration+ystep,ystep))
        ax.set_ylim(0,max(ydata)+ystep)
        for i in range(len(xdata)):
            if dates:
                pylab.text(xdata[i], 0, dates[i], rotation='vertical',size='large',fontweight="bold",family='fantasy')
    figure.autofmt_xdate(rotation=30)
    figure.savefig(imgfilename,format="png")
    figure.savefig(docfilename,format="pdf")
    return imgfilename,docfilename

def get_max_duration(durations):
    if durations: 
        maxduration = max(durations)
    else:
        maxduration = 0
    return maxduration
    
def get_extreme_values(data):
    if data:
        min_x = min(data)
        max_x = max(data)
    else:
        min_x = max_x = 0
    return min_x,max_x  



    

