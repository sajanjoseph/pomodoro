from pomlogger.models import PomEntry,PomCategory
from pomlogger.models import PomEntryForm,PomCategoryForm,PomCategoryNameForm,PomEntryShareForm,PomEntryPartialForm
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

def custom_render(request,context,template):
    req_context=RequestContext(request,context)
    return render_to_response(template,req_context)

@login_required
def entry_archive_index(request,page_title,template_name):
    entryset=PomEntry.objects.filter(author=request.user)
    entry_duration_dict=get_duration_for_categories(entryset)
    now=datetime.datetime.now()
    entries_sharedto_me=PomEntry.objects.filter(sharedwith=request.user)#added for sharing
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'entries_sharedto_me':entries_sharedto_me,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_year(request,year,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,author=request.user)
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_month(request,year,month,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),author=request.user)
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'month':month,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_day(request,year,month,day,page_title,template_name):
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),today__day=day,author=request.user)
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
    form=PomEntryPartialForm(form_data)
    catnameform=PomCategoryNameForm(form_data)
    context={'page_title':page_title,'entryform':form,'categoryform':catnameform}
    if request.method=='POST' and form.is_valid() and catnameform.is_valid():
        newentry=form.save()
        start_time=request.POST[u'timerstarted']
        stop_time=request.POST[u'timerstopped']
        start_ttpl,stop_ttpl=adjust_pmtime(start_time,stop_time)
        start_timeval=datetime.time(*start_ttpl)
        stop_timeval=datetime.time(*stop_ttpl)
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
        return redirect('pomlog_entry_archive_index')
        
    return custom_render(request,context,template_name)

def adjust_pmtime(starttime,endtime):
    print 'adjust_pmtime():'
    fmtstr='%H:%M:%S %p'
    start_l=list(time.strptime(starttime,fmtstr)[3:6])
    stop_l=list(time.strptime(endtime,fmtstr)[3:6])
    print 'starttime=',starttime
    print 'endtime=',endtime
    if starttime.find('PM') !=-1:
        print 'PM found in starttime:',starttime
        if start_l[0]!=12:
            print 'starttime:not 12 so adding 12'
            start_l[0]+=12
    
    if endtime.find('PM') !=-1:
        print 'PM found in endtime:',endtime
        if stop_l[0]!=12:
            print 'endtime:not 12 so adding 12'
            stop_l[0]+=12
    start_ttpl=tuple(start_l)
    stop_ttpl=tuple(stop_l)
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
    
'''
@login_required
def share_entries_oldway(request,template_name,page_title):
    allusers=User.objects.all()
    others=User.objects.exclude(username=request.user.username)
    ownentries=PomEntry.objects.filter(author=request.user)
    owncats=get_categories_of_user(request.user)    
    context={'ownentries':ownentries,'owncats':owncats,'otherusers':others,'allusers':allusers,'page_title':page_title}
    if request.method=='POST':
        print '===========request.POST==========='
        print request.POST
        selected_users=request.POST.getlist('users_selected')
        entries_to_share=request.POST.getlist('sharing_options')        
        if len(entries_to_share)==1 and len(selected_users)>0:
            usrs_to_share_with=[User.objects.get(username=name) for name in selected_users]
            entries=[]
            if entries_to_share[0]==u'allentries':
                entries=PomEntry.objects.filter(author=request.user)
                print 'you selected all entries option:',entries
            elif entries_to_share[0]=='selectedentries':
                entry_id_list=request.POST.getlist('entries_selected')
                print 'you selected selectedentries option:',
                entries=get_entries_from_idstring(entry_id_list)
            elif entries_to_share[0]=='entries_with_cat':
                cat_idlist=request.POST.getlist('entries_with_cat')
                print 'you selected entries_with_cat option:',cat_idlist
                cats=get_categories_from_idstring(cat_idlist)
                entries=get_own_entries_with_cats(cats,request.user)

            print 'sharing',entries,'with users',usrs_to_share_with            
            share_entries_with_users(entries,usrs_to_share_with)
            return redirect('pomlog_entry_archive_index')

    print 'GET or invalid'
    return custom_render(request,context,template_name)

'''

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







    

