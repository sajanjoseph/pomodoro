from pomlogger.models import PomEntry,PomCategory
from django.forms import ModelForm,Form,ValidationError
from django.forms import CharField,Textarea,TimeField,IntegerField
from django.forms import RadioSelect,ChoiceField,ModelMultipleChoiceField
from django.contrib.auth.models import User

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

class PomEntryEditForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PomEntryEditForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['today'].widget.attrs['readonly'] = True
            self.fields['start_time'].widget.attrs['readonly'] = True
            self.fields['end_time'].widget.attrs['readonly'] = True

    class Meta:
        model=PomEntry
        exclude = ('categories','author','sharedwith',)
        
class PomEntryDescForm(Form):
    description=CharField(max_length=200,widget=Textarea)


class PomEntryDifficultyForm(Form):
    difficulty = IntegerField(max_value=10,min_value=1)

class PomCategoryForm(ModelForm):
    class Meta:
        model=PomCategory
        exclude = ('slug','creator')
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
        try:
            share_options=self.cleaned_data['sharing_options']
                        
        except KeyError:
            raise ValidationError('you must select one of the sharing options')

        return share_options

    def clean_entries_selected(self):
        try:
            entries_selected=self.cleaned_data['entries_selected']
                        
        except KeyError:
            raise ValidationError('you must select at least one of the entries')

        return entries_selected

    def clean_users_selected(self):
        try:
            users_selected=self.cleaned_data['users_selected']

        except KeyError:
            raise ValidationError('you must select at least one of the users')

        return users_selected

    def clean_categories_selected(self):
        try:
            cats_selected=self.cleaned_data['categories_selected']

        except KeyError:
            raise ValidationError('you must select at least one of the categories')
        return cats_selected
        
    def clean(self):
        cleaned_data=self.cleaned_data
        if 'sharing_options' in cleaned_data and 'entries_selected' in cleaned_data:
            if cleaned_data['sharing_options']==u'selectedentries' and len(cleaned_data['entries_selected'])==0:
                raise ValidationError('select at least one entry from list box')
        return  cleaned_data