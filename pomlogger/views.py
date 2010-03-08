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
    return custom_render(request,context,template_name)

@login_required
def entry_archive_year(request,year,page_title,template_name):
    print 'year=',year,'of type=',type(year)
    entryset=PomEntry.objects.filter(today__year=year,author=request.user)
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_month(request,year,month,page_title,template_name):
    print 'year=',year,'of type=',type(year)
    print 'month=',month,'of type=',type(month)
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),author=request.user)
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'month':month,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_archive_day(request,year,month,day,page_title,template_name):
    print 'year=',year,'of type=',type(year)
    print 'month=',month,'of type=',type(month)
    print 'day=',day,'of type=',type(day)
    entryset=PomEntry.objects.filter(today__year=year,today__month=get_month_as_number(month),today__day=day,author=request.user)
    entry_duration_dict=get_duration_for_categories(entryset)
    context={'entry_duration_dict':entry_duration_dict,'object_list':entryset,'year':year,'month':month,'day':day,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def entry_detail(request,id,page_title,template_name):
    print 'entry_detail()'	
    entry=get_object_or_404(PomEntry,id=id,author=request.user)
    duration=timediff(entry.start_time,entry.end_time)
    context={'object':entry,'duration':duration,'page_title':page_title}
    return custom_render(request,context,template_name)

@login_required
def delete_entry(request,id):
    entry=get_object_or_404(PomEntry,id=id,author=request.user )
    print 'delete_entry()-entry=',entry
    entry.delete()
    print 'delete_entry()--deleted'
    return redirect('pomlog_entry_archive_index')


def get_categories(catnames):
    print 'get_categories():catnames=%s=%s'%(catnames,type(catnames))
    #categories=string.split(catnames,',')
    cats=[]
    #for name in categories:
    for name in catnames:
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
        catnames=get_list_of_names(catnames)            
        #newentry.categories=get_categories(catnames)
        #sj 2 mar 2010
        cats=get_categories(catnames)
        print 'add_new_entry():req.usr=',request.user
        for x in cats:
            print 'x.userscount=',x.users.count()
            if request.user not in x.users.all():
                print 'user:',request.user,'not in users'
                x.users.add(request.user)#need to append, not assign
            print 'x.userscount=',x.users.count()
        newentry.categories=cats
        newentry.save()
        return redirect('pomlog_entry_archive_index')
        
    return custom_render(request,context,template_name)

def get_category_names_as_one_string(categorynameslist):
    return ','.join(categorynameslist)

def get_list_of_names(names):
    print 'get_list_of_names():names=',names,type(names)
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
    print 'before editing entry:categorynames_as_one_string=',categorynames_as_one_string
    categorynamesdata={'categories':categorynames_as_one_string}
    form_data=get_form_data(request)
    form=PomEntryForm(form_data,instance=entry)
    catnameform=PomCategoryNameForm(form_data,initial=categorynamesdata)
    context={'entryform':form,'categoryform':catnameform,'page_title':page_title}
    form_valid=form.is_valid()
    catnameform_valid=catnameform.is_valid()
    print 'b4 post'
    print 'form_valid=',form_valid
    print 'catnameform_valid=',catnameform_valid 
    if request.method=='POST' and form_valid and catnameform_valid:
        print 'in post'       
        edited_entry=form.save()
        catnames=catnameform.cleaned_data['categories']
        #catnames=get_list_of_names(catnames)
        print 'after editing entry:catnames=',catnames
        new_categorynames_list=get_list_of_names(catnames)
        newlyaddedcatnames=set(new_categorynames_list)-set(old_categorynames_list)
        newlyaddedcatnames=list(newlyaddedcatnames)
        removedcatnames=set(old_categorynames_list)-set(new_categorynames_list)
        removedcatnames=list(removedcatnames)
        print 'edit_entry():newlyaddedcatnames=',newlyaddedcatnames
        print 'edit_entry():removedcatnames=',removedcatnames
        print 'edit_entry():catnames=',catnames
        #for each name in newlyaddedcatnames,get or create category object, add this user in its users field
        if newlyaddedcatnames:
            newlyaddedcats=get_categories(newlyaddedcatnames)
            add_user_to_categories(newlyaddedcats,request.user)
        #for each name in removedcatnames ,get category object ,remove this user from its users field
        if removedcatnames:
            removedcats=get_categories(removedcatnames)
            remove_user_from_categories(removedcats,request.user)
        #sj 2 mar
        cats=get_categories(get_list_of_names(catnames))
        print 'edit_entry():got cats'
        edited_entry.categories=cats
        edited_entry.save()           
        return redirect('pomlog_entry_archive_index')
    return custom_render(request,context,template_name)

def update_cats_with_editable_status(user,categories):
    cats={}
    print '****************************'
    for cat in categories:
        usrcnt=cat.users.count()
        allcatusrs=cat.users.all()
        user_in_users=user in allcatusrs
        print 'user',user,'in',allcatusrs,'=',user_in_users
        if usrcnt==1 and user in allcatusrs:
            print 'user :',user,' can edit :',cat 
            cats[cat]=True
        else:
            print 'user :',user,' cannot edit :',cat 
            cats[cat]=False
    return cats
            

@login_required
def category_list(request,template_name,page_title):
    categories=PomCategory.objects.all()
    cats_of_user=PomCategory.objects.filter(users=request.user)
    print 'category_list():cats of :',request.user,' are=',cats_of_user
    #category_list_dict={'object_list':categories,'page_title':page_title }
    #create a dict with catobject as key and editablestatus as value
    cats=update_cats_with_editable_status(request.user,cats_of_user)
    print 'user:',request.user,cats
    category_list_dict={'object_list':cats_of_user,'page_title':page_title ,'cats_status':cats}# user can only see his categories
    return custom_render(request,category_list_dict,template_name)

@login_required
def category_detail(request,slug,template_name,page_title):
    category=get_object_or_404(PomCategory,slug=slug)
    now=datetime.datetime.now()
    context={'object':category,'now':now, 'page_title': page_title}
    print 'category_detail():cat users=',category.users.all()
    return custom_render(request,context,template_name)

@login_required
def delete_category(request,slug):
    print 'slug=',slug
    cat=get_object_or_404(PomCategory,slug=slug)
    print 'delete cat()=',cat
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
                return custom_render(request,context,template_name)
        else:
            print 'we are adding a new cat %s'%name
            form.save()
            return redirect('pomlog_category_list') 
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


    

