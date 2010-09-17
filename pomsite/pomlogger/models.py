from django.db import models
from datetime import datetime,date,time
from django.contrib.auth.models import User
from django.forms import ModelForm,Form,ValidationError
from django.forms import CharField,Textarea,TimeField

from django.template.defaultfilters import slugify
from django.forms import RadioSelect,ChoiceField,ModelMultipleChoiceField

class PomCategory(models.Model):
    name=models.CharField(unique=True,max_length=50)
    description=models.TextField(blank=True)
    users=models.ManyToManyField(User)    
    slug=models.SlugField(editable=False)
    
    class Meta:
		verbose_name_plural="PomCategories"

    def __unicode__(self):
        return self.name


    def save(self,*args,**kwargs):
        self.name=self.name.strip()
        self.slug=slugify(self.name)
        super(PomCategory,self).save(*args,**kwargs)
    
    @models.permalink
    def get_absolute_url(self):
        return ('pomlog_category_detail',(),{'slug':self.slug})

class PomEntry(models.Model):
    today=models.DateField(default=date.today)
    #start_time=models.TimeField(default=(lambda:datetime.now().time))
    #end_time=models.TimeField(default=(lambda:datetime.now().time))
    start_time=models.TimeField(null=True)
    end_time=models.TimeField(null=True)
    description=models.TextField()
    author=models.ForeignKey(User,null=True)
    sharedwith=models.ManyToManyField(User,related_name='sharedwith',null=True)
    categories=models.ManyToManyField(PomCategory)
    
    class Meta:
	    verbose_name_plural="PomEntries"

    def __unicode__(self):
        return "%s%s"%([str(x.name) for x in self.categories.all()],self.start_time)

    @models.permalink
    def get_absolute_url(self):
        return ('pomlog_entry_detail',(),{'id':self.id})


class PomEntryForm(ModelForm):	
    class Meta:
        model=PomEntry
        exclude = ('categories','author','sharedwith',)
    def clean(self):
        cleaned_data=self.cleaned_data
        st_t=cleaned_data.get('start_time')
        en_t=cleaned_data.get('end_time')
        if not (st_t and en_t):
            return
        if not st_t < en_t:
            raise ValidationError('end time must be greater than start time')			
        return cleaned_data

class PomEntryDescForm(Form):
    description=CharField(max_length=200,widget=Textarea)
    
class PomEntryPartialForm(ModelForm):
    class Meta:
        model=PomEntry
        exclude = ('today','start_time','end_time','categories','sharedwith','author',)

class PomCategoryForm(ModelForm):
	class Meta:
		model=PomCategory
		exclude = ('slug','users',)
class PomCategoryNameForm(Form):
	categories=CharField(max_length=200)


class PomEntryShareForm(Form):
    RADIO_CHOICES=(('allentries','All Entries'),('selectedentries','Select from Entries'),('entriesofcat','Entries of Category'),)
    sharing_options=ChoiceField(widget=RadioSelect,label='Sharing Options',choices=RADIO_CHOICES)
    
    def __init__(self,formdata,request,*args,**kwargs):
        Form.__init__(self,formdata, *args, **kwargs)
        self.fields['entries_selected']=ModelMultipleChoiceField(required=False,queryset=PomEntry.objects.filter(author=request.user))
        self.fields['categories_selected']=ModelMultipleChoiceField(required=False,queryset=PomCategory.objects.filter(pomentry__author=request.user).distinct())
        self.fields['users_selected']=ModelMultipleChoiceField(queryset=User.objects.exclude(username=request.user.username))

    def clean_sharing_options(self):
        print 'PomEntryShareForm::clean_sharing_options()'
        try:
            share_options=self.cleaned_data['sharing_options']
                        
        except KeyError:
            raise ValidationError('you must select one of the sharing options')

        return share_options

    def clean_entries_selected(self):
        print 'PomEntryShareForm::clean_entries_selected()'
        try:
            entries_selected=self.cleaned_data['entries_selected']
                        
        except KeyError:
            raise ValidationError('you must select at least one of the entries')

        return entries_selected

    def clean_users_selected(self):
        print 'PomEntryShareForm::clean_users_selected()'
        try:
            users_selected=self.cleaned_data['users_selected']

        except KeyError:
            raise ValidationError('you must select at least one of the users')

        return users_selected

    def clean_categories_selected(self):
        print 'PomEntryShareForm::clean_categories_selected()'
        try:
            cats_selected=self.cleaned_data['categories_selected']

        except KeyError:
            raise ValidationError('you must select at least one of the categories')
        return cats_selected
        
    def clean(self):
        print 'PomEntryShareForm::clean()'
        cleaned_data=self.cleaned_data
        if 'sharing_options' in cleaned_data and 'entries_selected' in cleaned_data:
            if cleaned_data['sharing_options']==u'selectedentries' and len(cleaned_data['entries_selected'])==0:
                raise ValidationError('select at least one entry from list box')
        else:
            print 'if condition failed'
        print 'PomEntryShareForm::cleaned_data=',cleaned_data
        return  cleaned_data

