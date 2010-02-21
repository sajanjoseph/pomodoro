from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from pomlogger.models import PomCategory,PomEntry,PomEntryForm,PomCategoryNameForm
from pomlogger.views import timediff,get_duration_for_categories,get_month_as_number
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from datetime import time,date

class PomTestCase(TestCase):
    def setUp(self):
        super(PomTestCase,self).setUp()
        self.client.login(username='sajan',password='sajan')
    

class PomCategoryTest(PomTestCase):
    fixtures=['cats.json']
    def test_slug_generated(self):
        catname="PROGRAMMING PYTHON"
        cat=PomCategory(name=catname ,description='programming lessons')
        cat.save()
        result=cat.slug
        expectedvalue=slugify(catname)
        self.assertEqual(expectedvalue,result)

    def test_category_list_view(self):
        response=self.client.get(reverse('pomlog_category_list'))
        status_code=response.status_code
        print 'status_code=',status_code
        self.assertEqual(200,status_code)
    
    def test_add_category_view(self):
        print 'test_add_category'
        response=self.client.post(reverse('pomlog_add_category'),{'name':'magic','description':'mantra tantra'})        
        status_code=response.status_code
        print 'status_code=',status_code        
        self.assertRedirects(response,reverse('pomlog_category_list'),status_code=302)
    
    def test_category_detail(self):
        response=self.client.get(reverse('pomlog_category_detail',args=['maths']))
        #print response.context
        self.assertEqual(PomCategory.objects.get(name='maths'),response.context['object'])

    def test_404_if_category_not_found(self):
        response=self.client.get(reverse('pomlog_category_detail',args=['magic']))
        self.assertEqual(404,response.status_code)

    '''
    def test_add_category_trim_name(self):
        catscount=PomCategory.objects.count()
        cat1=PomCategory.get(name='biology')
        new_name=cat1.name
        response=self.client.post(reverse('pomlog_add_category'),{name=' biology',description='space bio'})
        self.assertEqual(200,response.status_code)
        self.assertEqual(catscount,PomCategory.objects.count())
    '''
        

class AddEntryTest(PomTestCase):
    fixtures=['cats.json']
    
    def setUp(self):
        super(AddEntryTest,self).setUp()
        self.post_data={
                        'today':'2010-02-20',
                        'start_time':'10:50:30',
                        'end_time':'11:15:30',
                        'description':'some desc',
                        'author':'1',
                        'categories':'yogic science'

                        }

    def test_add_entry_get_view(self):
        response=self.client.get(reverse('pomlog_add_entry'))
        self.assertEqual(200,response.status_code)
        self.assertTemplateUsed(response,'pomlogger/add_or_edit_entry.html')
        self.assertTrue(isinstance(response.context['entryform'],PomEntryForm))
        self.assertTrue(isinstance(response.context['categoryform'],PomCategoryNameForm))
        self.assertEquals('Add Entry',response.context['page_title'])

    def test_add_entry_post_new_cat(self):     
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
        print 'resp=',response
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.assertEqual(1,PomEntry.objects.count())
        entry=PomEntry.objects.latest('id')
        cat=PomCategory.objects.get(name='yogic science')
        self.assertEqual(cat,entry.categories.latest('id'))

    def test_add_entry_post_existing_category(self):
        self.post_data['categories']='maths'
        catcount=PomCategory.objects.count()
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.assertEqual(catcount,PomCategory.objects.count())
        entry=PomEntry.objects.latest('id')
        cat=PomCategory.objects.get(name='maths')
        self.assertEqual(cat,entry.categories.latest('id'))# from join table..will only have maths
        
    def test_add_entry_multiple_cats_one_existing(self):
        catcount=PomCategory.objects.count()
        self.post_data['categories']='maths,physics'
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.assertEqual(catcount+1,PomCategory.objects.count())
        entry=PomEntry.objects.latest('id')
        cat_physics=PomCategory.objects.get(name='physics')
        cat_maths=PomCategory.objects.get(name='maths')
        self.assertEqual(2,entry.categories.count())
        self.assertEqual([cat_maths,cat_physics],[cat for cat in  entry.categories.all().order_by('name')])
    
    def test_add_entry_trim_cat_name(self):
        catscount=PomCategory.objects.count()
        entrycount=PomEntry.objects.count()
        self.post_data['categories']=' maths'        
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.assertEqual(catscount,PomCategory.objects.count())
        self.assertEqual(entrycount+1,PomEntry.objects.count())

    def test_add_entry_existing_cat_trailing_comma(self):
        catscount=PomCategory.objects.count()
        entrycount=PomEntry.objects.count()
        self.post_data['categories']='maths, '
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        print 'cats=',PomCategory.objects.all()
        self.assertEqual(catscount,PomCategory.objects.count())
        self.assertEqual(entrycount+1,PomEntry.objects.count())

    def test_add_entry_existing_cats_commas_inside(self):
        catscount=PomCategory.objects.count()
        entrycount=PomEntry.objects.count()
        print 'cats=',PomCategory.objects.all()
        self.post_data['categories']='maths, , , ,biology,'
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        print 'cats=',PomCategory.objects.all()
        self.assertEqual(catscount,PomCategory.objects.count())
        self.assertEqual(entrycount+1,PomEntry.objects.count())
        

class EditEntryTest(PomTestCase):
    fixtures=['cats.json','entries.json']
    def setUp(self):
        super(EditEntryTest,self).setUp()
        self.post_data={
                        'today':'2010-02-19',
                        'start_time':'20:00:56',
                        'end_time':'20:30:56',
                        'description':'maths and biology',
                        'author':'1',
                        'categories':'maths'

                        }
        self.post_part_data={
            'categories':'maths'
        }
    
    def test_edit_entry_get_view(self):
        response=self.client.get(reverse('pomlog_edit_entry',args=[1]))
        self.assertEquals(200,response.status_code)
        self.assertTemplateUsed(response,'pomlogger/add_or_edit_entry.html')
        entry_form=response.context['entryform']
        cat_name_form=response.context['categoryform']
        
        self.assertTrue(isinstance(entry_form,PomEntryForm))
        self.assertTrue(isinstance(cat_name_form,PomCategoryNameForm))        
        self.assertEqual(PomEntry.objects.latest('id'),entry_form.instance)
        self.assertEquals({'categories': 'maths,biology'},cat_name_form.initial)

    def test_edit_entry_post_remove_one_cat(self):              
        self.client.post(reverse('pomlog_edit_entry',args=[1]),self.post_data )
        entry=PomEntry.objects.latest('id')        
        self.assertEquals(1,entry.categories.count())
        
        
        
    
        
        
    


class HelperFunctionsTest(TestCase):
    
    def test_timediff(self):
        start=time(1,15,30)
        end=time(1,35,30)
        expected=20
        result=timediff(start,end)
        self.assertEqual(expected,result)

    def test_duration_for_categories_in_entry(self):
        category1=PomCategory(name='maths',description='mathematics')
        category1.save()
        category2=PomCategory(name='astronomy',description='stars,planets')
        category2.save()
        dummy=User.objects.get(id=1)
        entry1=PomEntry(today=date(2010,2,18),start_time=time(1,0,0),end_time=time(1,30,0),description='testentry1',author= dummy)
        entry1.save()       
        entry1.categories=[category1,category2]
        entry1.save()
        entry2=PomEntry(today=date(2010,2,18),start_time=time(1,10,0),end_time=time(1,30,0),description='testentry2',author= dummy)
        entry2.save()
        entry2.categories=[category1]
        entry2.save()
        entryset=[entry1,entry2]
        result_duration_dict=get_duration_for_categories(entryset)
        expected={u'astronomy': 30,u'maths': 50}      
        self.assertEqual(expected,result_duration_dict)

    def test_get_month_as_number(self):
        month_str='mar'
        expected=3
        result=get_month_as_number(month_str)
        self.assertEqual(expected,result)
       
        
        
        
        

        
