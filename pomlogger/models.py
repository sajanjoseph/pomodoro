from django.db import models
from datetime import datetime,date,time
from django.contrib.auth.models import User
from django.forms import ModelForm,Form,CharField,ValidationError
from django.forms import RadioSelect,SelectMultiple
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
    start_time=models.TimeField(default=(lambda:datetime.now().time))
    end_time=models.TimeField(default=(lambda:datetime.now().time))
    description=models.TextField()
    author=models.ForeignKey(User,null=True)
    sharedwith=models.ManyToManyField(User,related_name='sharedwith',null=True)
    categories=models.ManyToManyField(PomCategory)
    
    class Meta:
	    verbose_name_plural="PomEntries"

    def __unicode__(self):
        return "%s%s"%([x.name for x in self.categories.all()],self.start_time)

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
            #self._errors.update({'start,end timedate error':'end time must be greater than start time'})
            raise ValidationError('end time must be greater than start time')			
        return cleaned_data

class PomCategoryForm(ModelForm):
	class Meta:
		model=PomCategory
		exclude = ('slug','users',)
class PomCategoryNameForm(Form):
	categories=CharField(max_length=200)


class PomEntryShareForm(Form):
    RADIO_CHOICES=(('allentries','All Entries'),('selectedentries','Select from Entries'),('entriesofcat','Entries of Category'),)
    sharing_options=ChoiceField(widget=RadioSelect,label='Sharing Options',choices=RADIO_CHOICES)

    def clean_sharing_options(self):
        try:
            share_options=self.cleaned_data['sharing_options']
                        
        except KeyError:
            raise ValidationError('you must select one of the sharing options')

        return share_options

    def clean_entries_selected(self):
        try:
            entries_sel=self.cleaned_data['entries_selected']
                        
        except KeyError:
            raise ValidationError('you must select at least one of the entries')

        return entries_sel

    def clean_users_selected(self):
        try:
            users_sel=self.cleaned_data['users_selected']

        except KeyError:
            raise ValidationError('you must select at least one of the users')

        return users_sel


    def clean_ecategories_selected(self):
        try:
            cats_sel=self.cleaned_data['categories_selected']

        except KeyError:
            raise ValidationError('you must select at least one of the categories')
        return cats_sel
        
    def clean(self):
        cleaned_data=self.cleaned_data
        if 'sharing_options' in cleaned_data and 'entries_selected' in cleaned_data:
            if cleaned_data['sharing_options']==u'selectedentries' and len(cleaned_data['entries_selected'])==0:
                raise ValidationError('select at least one entry from list box')
        print 'PomEntryShareForm::cleaned_data=',cleaned_data
        return  cleaned_data






