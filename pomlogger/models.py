from django.db import models
from datetime import datetime,date,time
from django.contrib.auth.models import User
from django.forms import ModelForm,Form,CharField,ValidationError
from django.template.defaultfilters import slugify


class PomCategory(models.Model):
    name=models.CharField(unique=True,max_length=50)
    description=models.TextField(blank=True)
    slug=models.SlugField(editable=False)
    
    class Meta:
		verbose_name_plural="PomCategories"

    def __unicode__(self):
        return self.name


    def save(self,*args,**kwargs):
        print 'cat:save()'
        self.name=self.name.strip()
        '''
        if (not self.pk):
            print 'not self.pk=',self.pk
            if PomCategory.objects.filter(name__iexact=self.name).count()!=0:
                raise Exception('category %s already exists'%self.name)
        '''
        print 'cat:save():name=%s'%self.name
        self.slug=slugify(self.name)
        print 'cat:save():slug=%s'%self.slug
        super(PomCategory,self).save(*args,**kwargs)
    
    @models.permalink
    def get_absolute_url(self):
        return ('pomlog_category_detail',(),{'slug':self.slug})

class PomEntry(models.Model):
    today=models.DateField(default=date.today)
    start_time=models.TimeField(default=(lambda:datetime.now().time))
    end_time=models.TimeField(default=(lambda:datetime.now().time))
    description=models.TextField()
    author=models.ForeignKey(User)
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
        exclude = ('categories',)
    def clean(self):
        cleaned_data=self.cleaned_data
        st_t=cleaned_data.get('start_time')
        en_t=cleaned_data.get('end_time')
        if not (st_t and en_t):
            return
        if not st_t < en_t:
            self._errors.update({'start,end timedate error':'end time must be greater than start time'})			
        return cleaned_data

class PomCategoryForm(ModelForm):
	class Meta:
		model=PomCategory
		exclude = ('slug',)
'''
        def clean_name(self):
            print 'clean_name()'
            name=self.cleaned_data['name']
            name=name.strip()
            print 'name=',name
            if PomCategory.objects.filter(name__iexact=name).count()!=0:
                raise ValidationError('category %s already exists'% name)
            return name
'''
class PomCategoryNameForm(Form):
	categories=CharField(max_length=200)






