from django.db import models
from datetime import datetime,date,time
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator
from django.template.defaultfilters import slugify
from django.template.defaultfilters import truncatewords


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
    start_time=models.TimeField(null=True)
    end_time=models.TimeField(null=True)
    description=models.TextField()
    author=models.ForeignKey(User,null=True)
    difficulty = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(10)],default=5,help_text='integers 1 to 10')
    sharedwith=models.ManyToManyField(User,related_name='sharedwith',null=True)
    categories=models.ManyToManyField(PomCategory)
    
    class Meta:
	    verbose_name_plural="PomEntries"

    def __unicode__(self):
        shortdescription=truncatewords(self.description,2)
        return shortdescription+'-'+unicode(self.today)+'-'+unicode(self.start_time)
    
    @models.permalink
    def get_absolute_url(self):
        return ('pomlog_entry_detail',(),{'id':self.id})




