from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from pomlogger.models import PomCategory,PomEntry,PomEntryForm,PomEntryEditForm,PomCategoryNameForm,PomEntryDescForm
from pomlogger.views import timediff,get_duration_for_categories,get_month_as_number
from pomlogger.views import get_list_of_names,get_timetuples,has_permission
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from datetime import time,date
from pomlogger.test_utils import get_context_variable
from django.db.models.query import QuerySet

class PomTestCase(TestCase):
    def setUp(self):
        super(PomTestCase,self).setUp()
        self.client.login(username='sajan',password='sajan')

class PomCategoryTest(PomTestCase):
    fixtures=['cats.json','entries1.json']
    def test_slug_generated(self):
        catname="PROGRAMMING PYTHON"
        cat=PomCategory(name=catname ,description='programming lessons')
        cat.save()
        result=cat.slug
        expectedvalue=slugify(catname)
        self.assertEqual(expectedvalue,result)

    def test_category_list_view(self):
        #print 'reverse=',reverse('pomlog_category_list')
        response=self.client.get(reverse('pomlog_category_list'))
        status_code=response.status_code
        #print 'st code=',status_code
        cats=get_context_variable(response,'cats')
        self.assertEqual(3,len(cats))
        self.assertEqual(200,status_code)

    def test_post_add_category(self):
        response=self.client.post(reverse('pomlog_add_category'),{'name':'magic','description':'mantra tantra'})        
        status_code=response.status_code
        self.assertRedirects(response,reverse('pomlog_category_list'),status_code=302)

    def test_category_detail(self):
        response=self.client.get(reverse('pomlog_category_detail',args=['maths']))
        self.assertEqual(PomCategory.objects.get(name='maths'),response.context['object'])
    
    def test_404_if_category_not_found(self):
        response=self.client.get(reverse('pomlog_category_detail',args=['magic']))
        self.assertEqual(404,response.status_code)
    
    def test_add_category_trim_name(self):
        catscount=PomCategory.objects.count()
        response=self.client.post(reverse('pomlog_add_category'),{'name':' biology','description':'space bio'})
        self.assertEqual(catscount,PomCategory.objects.count())
        self.assertEqual(200,response.status_code)

    def test_add_category_existing_cat_add_uppercase_name(self):
        catscount=PomCategory.objects.count()
        response=self.client.post(reverse('pomlog_add_category'),{'name':'BIOLOGY','description':'uppercase bio'})
        self.assertEqual(catscount,PomCategory.objects.count())
        self.assertEqual(200,response.status_code)

    def test_add_category_existing_cat_add_lowercase_name(self):
        catscount=PomCategory.objects.count()
        response=self.client.post(reverse('pomlog_add_category'),{'name':'chemistry','description':'lowercase chem'})
        self.assertEqual(catscount,PomCategory.objects.count())
        self.assertEqual(200,response.status_code)    

    def test_delete_category(self):
        response=self.client.post(reverse('pomlog_delete_category',args=['chemistry']))
        self.assertEquals(2,PomCategory.objects.count())
        self.assertRedirects(response,reverse('pomlog_category_list'),status_code=302, target_status_code=200)    

    def test_edit_category(self):
        response=self.client.post(reverse('pomlog_edit_category',args=['maths']),{'name':'maths','description':'algebra' })
        self.assertEqual(3,PomCategory.objects.count())
        self.assertRedirects(response,reverse('pomlog_category_list'),status_code=302, target_status_code=200)
        newdescription=PomCategory.objects.get(id=1).description
        self.assertEqual('algebra',newdescription)

    def test_edit_category_newname(self):
        response=self.client.post(reverse('pomlog_edit_category',args=['maths']),{'name':'algebra','description':'algebra in 24 hrs' })
        self.assertEqual(3,PomCategory.objects.count())
        self.assertRedirects(response,reverse('pomlog_category_list'),status_code=302, target_status_code=200)
        newname=PomCategory.objects.get(id=1).name
        self.assertEqual('algebra',newname)

    def test_edit_category_with_existing_name(self):
        response=self.client.post(reverse('pomlog_edit_category',args=['maths']),{'name':'biology','description':'bio' })        
        self.assertContains(response,'category with this Name already exists',status_code=200)
        self.assertEqual(3,PomCategory.objects.count())

    def test_category_deleted_if_no_entry_exists(self):
        response=self.client.get(reverse('pomlog_delete_entry',args=[1]))
        self.assertEqual(2,PomCategory.objects.count())
        response=self.client.get(reverse('pomlog_delete_entry',args=[2]))
        self.assertEqual(1,PomCategory.objects.count())
        response=self.client.get(reverse('pomlog_delete_entry',args=[3]))
        finalcatscount=PomCategory.objects.count()
        #print 'test_category_deleted_if_no_entry_exists() final=%d'%finalcatscount
        self.assertEqual(0,finalcatscount)
        

    def test_get_edit_category_of_another_user(self):
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response=self.client.get(reverse('pomlog_edit_category',args=['maths']))
        self.assertEqual(404,response.status_code)
        self.client.logout()

    def test_post_edit_category_of_another_user(self):
        #print 'test_post_edit_category_of_another_user()::'
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response=self.client.post(reverse('pomlog_edit_category',args=['chemistry']),{'name':'chemical analysis','description':'chem analysis' })
        self.assertEqual(404,response.status_code)
        self.client.logout()     

    def test_category_detail_of_other_user(self):
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response=self.client.get(reverse('pomlog_category_detail',args=['maths']))
        self.assertEqual(404,response.status_code)
        self.client.logout()
        
        

class AddEntryTest(PomTestCase):
    fixtures=['cats.json']
    
    def setUp(self):
        super(AddEntryTest,self).setUp()
        self.post_data={
                        'today':'2010-02-20',
                        'timerstarted':'1266643230000',
                        'timerstopped':'1266644730000',
                        'description':'some desc',                        
                        'categories':'yogic science'
                        }
        
    def test_add_entry_get_view(self):
        response=self.client.get(reverse('pomlog_add_entry'))
        self.assertEqual(200,response.status_code)
        self.assertTemplateUsed(response,'pomlogger/add_entry.html')
        self.assertTrue(isinstance(response.context['entryform'],PomEntryDescForm))
        self.assertTrue(isinstance(response.context['categoryform'],PomCategoryNameForm))
        self.assertEquals('Add Entry',response.context['page_title'])
    def test_add_entry_post_new_cat(self):     
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
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
        self.assertEqual(catscount,PomCategory.objects.count())
        self.assertEqual(entrycount+1,PomEntry.objects.count())

    def test_add_entry_existing_cats_commas_inside(self):
        catscount=PomCategory.objects.count()
        entrycount=PomEntry.objects.count()
        self.post_data['categories']='maths, , , ,biology,'
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.assertEqual(catscount,PomCategory.objects.count())
        self.assertEqual(entrycount+1,PomEntry.objects.count())
        
    def test_add_entry_endtime_less_than_starttime(self):
        print 'test_add_entry_endtime_less_than_starttime()::'
        initialentrycount=PomEntry.objects.count()
        print 'initialentrycount=%d'%initialentrycount
        self.post_data['timerstopped']='1266643110000'                
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)        
        finalentrycount=PomEntry.objects.count()
        print 'finalentrycount=%d'%finalentrycount
        print 'status code=%d'%response.status_code
        erlst=get_context_variable(response,'errorlist')
        self.assertTrue('starttime should be less than endtime' in erlst)
        self.assertEqual(0,finalentrycount)
        self.assertEqual(200,response.status_code)
    
    def test_add_entry_description_empty(self):
        print 'test_add_entry_description_empty()::'        
        self.post_data['description']=u''
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
        finalentrycount=PomEntry.objects.count()
        print 'finalentrycount=%d'%finalentrycount
        self.assertEqual(0,finalentrycount)
    
    def test_add_entry_categories_empty(self):
        print 'test_add_entry_categories_empty()::'        
        self.post_data['categories']=u''
        response=self.client.post(reverse('pomlog_add_entry'),self.post_data)
        finalentrycount=PomEntry.objects.count()
        print 'finalentrycount=%d'%finalentrycount
        self.assertEqual(0,finalentrycount)
        
class EntryListings(PomTestCase):
    fixtures=['cats.json','entries.json']
    
    def test_entry_archive_year(self):
        response=self.client.get(reverse('pomlog_entry_archive_year',kwargs={'year':'2010'}))
        self.assertEqual('Entries for the Year',get_context_variable(response,'page_title'))
        self.assertEqual('2010',get_context_variable(response,'year'))
        entries_page=get_context_variable(response,'entries')
        self.assertEquals(2,entries_page.paginator.count)
        
        response=self.client.get(reverse('pomlog_entry_archive_year',args=['2009']))
        entries_page=get_context_variable(response,'entries')
        self.assertEquals(1,entries_page.paginator.count)
        
        response=self.client.get(reverse('pomlog_entry_archive_year',args=['2008']))
        entries_page=get_context_variable(response,'entries')
        self.assertEquals(3,entries_page.paginator.count)
        
    def test_entry_archive_year_noentry(self):
        response=self.client.get(reverse('pomlog_entry_archive_year',kwargs={'year':'2000'}))
        #ol=get_context_variable(response,'object_list')
        #self.assertEquals(0,ol.count())
        entries_page=get_context_variable(response,'entries')
        self.assertEquals(0,entries_page.paginator.count)
        self.assertContains(response,'No Entries in 2000',status_code=200)

    def test_entry_archive_index(self):
        '''
        object_list should contain same num of entries as in database
        '''
        response=self.client.get(reverse('pomlog_entry_archive_index'))
        #ol=get_context_variable(response,'object_list')
        #self.assertEquals(8,ol.count())# 8 entries
        entries_page=get_context_variable(response,'entries')
        self.assertEquals(8,entries_page.paginator.count)
        self.assertContains(response,'All entries',status_code=200)

    def test_entry_archive_month(self):
        '''
        should contain 3 entries
        '''
        response=self.client.get(reverse('pomlog_entry_archive_month',kwargs={'year':'2008','month':'feb'}))
        #ol=get_context_variable(response,'object_list')
        #self.assertEquals(3,ol.count())# 3 entries in year 2008feb
        entries_page=get_context_variable(response,'entries')
        self.assertEquals(3,entries_page.paginator.count)
        self.assertContains(response,'Entries for the month of feb 2008',status_code=200)

    
    def test_entry_archive_month_noentry(self):
        response=self.client.get(reverse('pomlog_entry_archive_month',kwargs={'year':'2007','month':'feb'}))
        # has 0 items
        entries_page=get_context_variable(response,'entries')
        self.assertEquals(0,entries_page.paginator.count)
        self.assertContains(response,'No Entries in feb 2007',status_code=200)

    def test_entry_archive_day(self):
        '''
         should contain 2 entries
        '''
        response=self.client.get(reverse('pomlog_entry_archive_day',kwargs={'year':'2007','month':'mar','day':'13'}))
        entries_page=get_context_variable(response,'entries')
        self.assertEquals(2,entries_page.paginator.count)
        self.assertContains(response,'Entries for the day of 13 mar 2007',status_code=200)
    
    def test_entry_archive_day_noentry(self):
        response=self.client.get(reverse('pomlog_entry_archive_day',kwargs={'year':'2007','month':'mar','day':'14'}))
        entries_page=get_context_variable(response,'entries')
        
        self.assertEquals(0,entries_page.paginator.count)
        self.assertContains(response,'No Entries on 14 mar 2007',status_code=200)

    def test_entry_detail(self):
        response=self.client.get(reverse('pomlog_entry_detail',kwargs={'id':5}))
        obj=get_context_variable(response,'object')
        self.assertTemplateUsed(response,'pomlogger/pomentry_detail.html')
        self.assertEquals(200,response.status_code)
        self.assertEqual('2008-02-21',str(obj.today))
        self.assertEqual('09:00:00',str(obj.start_time))


class EditEntryTest(PomTestCase):
    fixtures=['cats.json','entries.json']
    def setUp(self):
        super(EditEntryTest,self).setUp()
        self.post_data={
                        'today':'2010-02-19',
                        'start_time':'20:00:56',
                        'end_time':'20:30:56',
                        'description':'maths and biology',
                        'categories':'maths'
                        }
        self.post_part_data={
            'categories':'maths'
        }
    def test_edit_entry_get_view(self):
        response=self.client.get(reverse('pomlog_edit_entry',args=[1]))
        self.assertEquals(200,response.status_code)
        self.assertTemplateUsed(response,'pomlogger/edit_entry.html')
        entry_form=response.context['entryform']
        cat_name_form=response.context['categoryform']
        
        self.assertTrue(isinstance(entry_form,PomEntryEditForm))
        self.assertTrue(isinstance(cat_name_form,PomCategoryNameForm))
        self.assertEqual(PomEntry.objects.get(id=1),entry_form.instance)
        self.assertEquals({'categories': 'maths,biology'},cat_name_form.initial)

    def test_edit_entry_post_remove_one_cat(self):              
        self.client.post(reverse('pomlog_edit_entry',args=[1]),self.post_data )
        print 'allentries=',PomEntry.objects.all()
        entry=PomEntry.objects.get(id=1)       
        self.assertEquals(1,entry.categories.count())

    def test_delete_entry(self):
        entrycount=PomEntry.objects.count()
        test_entry=PomEntry.objects.get(id=1)
        testcat1=PomCategory.objects.get(name='maths')
        testcat2=PomCategory.objects.get(name='biology')
        self.assertEquals(1,testcat1.users.count())
        self.assertEquals(1,testcat2.users.count())
        response=self.client.post(reverse('pomlog_delete_entry',args=[1]))
        self.assertEquals(0,testcat1.users.count())
        self.assertEquals(0,testcat2.users.count())
        self.assertEquals(entrycount-1,PomEntry.objects.count())
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
    

class HelperFunctionsTest(TestCase):
    fixtures=['cats.json','entries.json']
    def test_timediff(self):
        start=time(1,15,30)
        end=time(1,35,30)
        expected=20
        result=timediff(start,end)
        self.assertEqual(expected,result)

    def test_duration_for_categories_in_entry(self):
        category1=PomCategory(name='magic',description='magical')
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
        expected={u'astronomy': 30,u'magic': 50}      
        self.assertEqual(expected,result_duration_dict)

    def test_get_month_as_number(self):
        month_str='mar'
        expected=3
        result=get_month_as_number(month_str)
        self.assertEqual(expected,result)

    def test_get_list_of_names(self):
        names=' sajan ,ravi, manoj ,denny '
        expected_names_list=['sajan' ,'ravi', 'manoj' ,'denny']
        self.assertEqual(expected_names_list,get_list_of_names(names))
        names=' , sajan ,, manoj , '
        expected_names_list=['sajan' ,'manoj']
        self.assertEqual(expected_names_list,get_list_of_names(names))
        names=' , ,,  , '
        expected_names_list=[]
        self.assertEqual(expected_names_list,get_list_of_names(names))
        names=''
        expected_names_list=[]
        self.assertEqual(expected_names_list,get_list_of_names(names))

    def test_get_timetuples(self):        
        self.assertEquals(((23,30,45),(0,34,55)),get_timetuples(1266602445000,1266519895000))

    def test_user_has_permission(self):
        cat1=PomCategory.objects.get(id=1)
        user1=User.objects.get(id=1)
        user2=User.objects.get(id=2)
        self.assertTrue(has_permission(user1,cat1))
        self.assertFalse(has_permission(user2,cat1))

class FunctionalTests(TestCase):
    fixtures=['newcats.json','newentries.json']
    def test_users_login(self):
        user1loggedin=self.client.login(username='sajan',password='sajan')
        self.assertTrue(user1loggedin)
        self.client.logout()
        user2loggedin=self.client.login(username='denny',password='denny')
        self.assertTrue(user2loggedin)
        self.client.logout()
    
    def __test_view_entries_of_user(self,user,passwd,expected_entries):
        userloggedin=self.client.login(username=user,password=passwd)
        if userloggedin:
            response=self.client.get(reverse('pomlog_entry_archive_index'))
            #ol=get_context_variable(response,'object_list')
            #self.assertEquals(expected_entries,ol.count())
            entries_page=get_context_variable(response,'entries')
            self.assertEquals(expected_entries,entries_page.paginator.count)
            self.client.logout()

    def test_view_own_entries(self):
        #login as sajan,list entries,only 3 should be listed ,all created by sajan
        self.__test_view_entries_of_user('sajan','sajan',3)
        #login as denny,list entries,only 2 should be listed ,all created by denny
        self.__test_view_entries_of_user('denny','denny',2)

    def test_view_another_persons_entry(self):
        self.client.login(username='sajan',password='sajan')
        response=self.client.get(reverse('pomlog_entry_detail',kwargs={'id':4}))
        self.assertEqual(404,response.status_code)
        self.client.logout()

    def test_view_get_edit_another_persons_entry(self):
        #if user tries to edit another person's entry show 404
        self.client.login(username='sajan',password='sajan')
        response=self.client.get(reverse('pomlog_edit_entry',args=[4]))
        self.assertEquals(404,response.status_code)
        self.client.logout()

    def test_delete_entry_created_by_another_user(self):
        #if user tries to delete another person's entry show 404
        self.client.login(username='sajan',password='sajan')
        response=self.client.get(reverse('pomlog_delete_entry',args=[4]))
        self.assertEquals(404,response.status_code)
        self.client.logout()

    def test_add_entry_append_cat_users(self):
        self.client.login(username='sajan',password='sajan')

        self.post_data1={
                        'today':'2010-03-01',
                        'timerstarted':'1267410600000',
                        'timerstopped':'1267412700000',
                        'description':'cormen,rivest',
                        'categories':'algorithms'
                        }
        response1=self.client.post(reverse('pomlog_add_entry'),self.post_data1)
        newcat1=PomCategory.objects.latest('id')
        users_cat1=newcat1.users
        self.assertEquals(1,users_cat1.count())
        self.client.logout()
        self.client.login(username='denny',password='denny')


        self.post_data2={
                        'today':'2010-02-11',
                        'timerstarted':'1265859000000',
                        'timerstopped':'1265860200000',
                        'description':'Sedgewick ',
                        'categories':'algorithms'
                        }
        response2=self.client.post(reverse('pomlog_add_entry'),self.post_data2)
        newcat2=PomCategory.objects.latest('id')
        users_cat2=newcat1.users
        self.assertEquals(2,users_cat2.count())
        self.client.logout()

    

    def test_users_edit_entries_to_update_category_users(self):
        self.client.login(username='sajan',password='sajan')
        self.sajan_entry_data={
                        'today':'2010-03-02',
                        'timerstarted':'1267504200000',
                        'timerstopped':'1267506300000',
                        'description':'physical measurements',
                        'categories':'maths,physics'
                        }
        self.client.post(reverse('pomlog_add_entry'),self.sajan_entry_data)
        mathcat=PomCategory.objects.get(name='maths')
        physcat=PomCategory.objects.get(name='physics')
        sajan=User.objects.get(username='sajan')
        self.assertTrue(sajan in mathcat.users.all())
        self.assertTrue(sajan in physcat.users.all())
        resp1=self.client.get(reverse('pomlog_category_list'))
        self.assertContains(resp1,'maths',status_code=200)
        self.assertContains(resp1,'physics',status_code=200)
        sjentries=PomEntry.objects.filter(author=sajan)
        for entry in sjentries:
            print 'entry=',entry
            cats=entry.categories.all()
            print '    entry cats=',cats
            for cat in cats:
                print '        users=',cat.users.all()
        self.client.logout()
        print 'sajan logged out first time'
        
        #now denny login in ,adds an entry with physics cat
        self.client.login(username='denny',password='denny')
        self.denny_entry_data={
                        'today':'2010-03-02',
                        'timerstarted':'1267507800000',
                        'timerstopped':'1267510800000',
                        'description':'classical physics',
                        
                        'categories':'physics'
                        }
        
        self.client.post(reverse('pomlog_add_entry'),self.denny_entry_data)
        physcat=PomCategory.objects.get(name='physics')
        denny=User.objects.get(username='denny')
        self.assertTrue(denny in physcat.users.all())
        self.assertEqual(2,physcat.users.count())
        resp2=self.client.get(reverse('pomlog_category_list'))
        self.assertNotContains(resp2,'maths',status_code=200) #user can only see his cats
        self.assertContains(resp2,'physics',status_code=200)
        
        denentries=PomEntry.objects.filter(author=denny)
        for entry in denentries:
            print 'entry=',entry
            cats=entry.categories.all()
            print '    entry cats=',cats
            for cat in cats:
                print '        users=',cat.users.all()
        self.client.logout()
        print 'denny logged out first time'
        
        #now sajan login in ,edits his entry to remove physics cat,now his entry has only maths as category
        self.client.login(username='sajan',password='sajan')
        
        self.sajan_entry_edit_data={
                                        'today':'2010-03-02',
                                        
                        
                                        'description':'maths only',
                                         'categories':'maths'  }# removes physics so that sajan has only maths cat
        
        resp3=self.client.post(reverse('pomlog_edit_entry',args=[6]),self.sajan_entry_edit_data )
        physcat=PomCategory.objects.get(name='physics')
        
        physusers=physcat.users.all()
        mathusers=mathcat.users.all()
        self.assertEqual(1,physcat.users.count())
        self.assertTrue(denny in physcat.users.all())
        self.assertFalse(sajan in physcat.users.all())
        resp4=self.client.get(reverse('pomlog_category_list'))
        self.assertNotContains(resp4,'physics',status_code=200)#sajan cannot see physics in cat listing
        self.client.logout()

class ShareEntriesTest(TestCase):
    fixtures=['share_entry_cats.json','share_entries.json']
    def test_share_entries_get_view(self):
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        response=self.client.get(reverse('pomlog_share_entries'))
        self.assertEqual(200,response.status_code)
        self.assertTemplateUsed(response,'pomlogger/share_entries.html')
        self.client.logout()

    def test_share_entries_post_allentries(self):
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_allentries_post_data={
                                'sharing_options':[u'allentries'],
                                'users_selected': [u'2']
                              }
        response=self.client.post(reverse('pomlog_share_entries'),self.share_allentries_post_data)
        print 'response.status_code',response.status_code
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        
        user1entries=PomEntry.objects.filter(author=user1)
        #check if user2 is in sharedwith field of all entries of user1
        for entry in user1entries:
            self.assertTrue(user2 in entry.sharedwith.all())
        
        self.client.logout()


    def test_share_entries_post_selectedentries(self):
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_selectedentries_post_data={
                                'sharing_options':[u'selectedentries'],
                                'users_selected': [u'2'],
                                'entries_selected': [u'1']
                              }
        response=self.client.post(reverse('pomlog_share_entries'),self.share_selectedentries_post_data)
        print 'response.status_code',response.status_code
        self.assertRedirects(response,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        shared_entry=PomEntry.objects.get(id=1)
        self.assertTrue(user2 in shared_entry.sharedwith.all())
        entries_not_shared=PomEntry.objects.exclude(id=1)
        for entry in entries_not_shared:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.client.logout()
        
    def test_share_entries_post_entries_of_cat(self):
        print 'test_share_entries_post_entries_of_cat()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_entries_with_cat_post_data={
                                       'sharing_options': [u'entriesofcat'],
                                       'users_selected': [u'2'],
                                       'categories_selected': [u'2']
                                             }
        response=self.client.post(reverse('pomlog_share_entries'),self.share_entries_with_cat_post_data)
        cat_shared=PomCategory.objects.get(id=2)
        #print 'cat_shared=',cat_shared
        entries_shared=PomEntry.objects.filter(categories=cat_shared).filter(author=user1)
        shared_ids=[entry.id for entry in entries_shared]
        print 'shared_ids=',shared_ids 
        #print 'sharing',entries_shared,' with user:',user2
        unshared_entries=PomEntry.objects.exclude(id__in= shared_ids)
        #print 'unshared_entries=',unshared_entries
        for entry in unshared_entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.client.logout()

    def test_other_user_can_view_allentries(self):
        print 'test_other_user_can_view_allentries()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_allentries_post_data={
                                'sharing_options':[u'allentries'],
                                'users_selected': [u'2']
                              }
        response1=self.client.post(reverse('pomlog_share_entries'),self.share_allentries_post_data)
        self.assertRedirects(response1,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response2=self.client.get(reverse('pomlog_entries_shared'))
        ol=list(get_context_variable(response2,'entries_sharedto_me'))
        allentries=list(PomEntry.objects.filter(author=user1))
        #entries_sharedto_user2=list(PomEntry.objects.filter(sharedwith=user2))
        #self.assertEqual(entries_sharedto_user2,ol)
        self.assertEqual(allentries,ol)
        self.client.logout()

    def test_other_user_can_view_selected_entries(self):
        print 'test_other_user_can_view_selected_entries()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_selected_entries_post_data={
                                'sharing_options':[u'selectedentries'],
                                'entries_selected': [u'1'],
                                'users_selected': [u'2']
                              }
        response1=self.client.post(reverse('pomlog_share_entries'),self.share_selected_entries_post_data)
        self.assertRedirects(response1,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response2=self.client.get(reverse('pomlog_entries_shared'))
        ol=list(get_context_variable(response2,'entries_sharedto_me'))
        selected_entries=list(PomEntry.objects.filter(id=1))
        self.assertEqual(selected_entries,ol)
        #entries_sharedto_user2=list(PomEntry.objects.filter(sharedwith=user2))
        #self.assertEqual(entries_sharedto_user2,ol)
        self.client.logout()

    def test_other_user_can_view_entries_of_cat(self):
        print 'test_other_user_can_view_entries_of_cat()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_entries_with_cat_post_data={
                                'sharing_options':[u'entriesofcat'],
                                'users_selected': [u'2'],
                                'categories_selected': [u'2']
                              }
        response1=self.client.post(reverse('pomlog_share_entries'),self.share_entries_with_cat_post_data)
        self.assertRedirects(response1,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response2=self.client.get(reverse('pomlog_entries_shared'))
        ol=list(get_context_variable(response2,'entries_sharedto_me'))
        cat_shared=PomCategory.objects.get(id=2)
        #entries_shared=list(PomEntry.objects.filter(categories=cat_shared).filter(author=user1))
        entries_shared=list(PomEntry.objects.filter(author=user1,categories=cat_shared))
        self.assertEqual(entries_shared,ol)
        self.client.logout()

    def test_allentries_option_no_entries_selected_for_sharing(self):
        print 'test_allentries_option_no_entries_selected_for_sharing()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        self.no_entries_selected_post_data={
                                'sharing_options': [u'allentries']                               
                              }
        response=self.client.get(reverse('pomlog_share_entries'))
        self.assertEqual(200,response.status_code)
        self.assertTemplateUsed(response,'pomlogger/share_entries.html')
        self.client.logout()

    def test_selectedentries_option_no_entries_selected_for_sharing(self):
        print 'test_selectedentries_option_no_entries_selected_for_sharing()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        self.no_entries_selected_post_data={
                                'sharing_options': [u'selectedentries']                               
                              }
        response=self.client.get(reverse('pomlog_share_entries'))
        self.assertEqual(200,response.status_code)
        self.assertTemplateUsed(response,'pomlogger/share_entries.html')
        self.client.logout()

    def test_entries_with_cat_option_no_entries_selected_for_sharing(self):
        print 'test_entries_with_cat_option_no_entries_selected_for_sharing()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        self.no_entries_selected_post_data={
                                'sharing_options': [u'entriesofcat']                               
                              }
        response=self.client.get(reverse('pomlog_share_entries'))
        self.assertEqual(200,response.status_code)
        self.assertTemplateUsed(response,'pomlogger/share_entries.html')
        self.client.logout()

    def test_share_already_shared_entry(self):
        print 'test_share_already_shared_entry()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_selectedentries_post_data={
                                'sharing_options':[u'selectedentries'],
                                'users_selected': [u'2'],
                                'entries_selected': [u'1']
                              }
        response=self.client.post(reverse('pomlog_share_entries'),self.share_selectedentries_post_data)
        self.share_repeat_selectedentries_post_data={
                                'sharing_options':[u'selectedentries'],
                                'users_selected': [u'2'],
                                'entries_selected': [u'1']
                              }
        print '..........trying to share the same entry again.......'
        response1=self.client.post(reverse('pomlog_share_entries'),self.share_repeat_selectedentries_post_data)
        self.assertRedirects(response1,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response2=self.client.get(reverse('pomlog_entries_shared'))
        ol=list(get_context_variable(response2,'entries_sharedto_me'))
        selected_entries=list(PomEntry.objects.filter(id=1))
        self.assertEqual(selected_entries,ol)
        self.client.logout()

    def test_can_view_shared_entry_detail(self):
        print 'test_can_view_shared_entry_detail()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_selectedentries_post_data={
                                'sharing_options':[u'selectedentries'],
                                'users_selected': [u'2'],
                                'entries_selected': [u'2']
                              }
        response=self.client.post(reverse('pomlog_share_entries'),self.share_selectedentries_post_data)
        #user2 tries to view details of this entry
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response2=self.client.get(reverse('pomlog_entry_detail',kwargs={'id':2}))
        obj=get_context_variable(response2,'object')
        self.assertTemplateUsed(response2,'pomlogger/pomentry_detail.html')
        self.assertEquals(200,response2.status_code)
        self.assertEqual('2010-05-13',str(obj.today))
        self.assertEqual('09:29:50',str(obj.start_time))
        self.client.logout()

    def test_user_cannot_edit_entry_shared_to_him(self):
        print 'test_user_cannot_edit_entry_shared_to_him()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_selectedentries_post_data={
                                'sharing_options':[u'selectedentries'],
                                'users_selected': [u'2'],
                                'entries_selected': [u'2']
                              }
        response=self.client.post(reverse('pomlog_share_entries'),self.share_selectedentries_post_data)
        #user2 tries to edit this entry
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response=self.client.get(reverse('pomlog_edit_entry',args=[2]))
        self.assertEquals(404,response.status_code)
        self.edit_post_data={
                        'today':'2010-05-13',
                        'start_time':'20:00:56',
                        'end_time':'20:30:56',
                        'description':'feinmann lectures',
                        'categories':'physics'
                        }
        response1=self.client.post(reverse('pomlog_edit_entry',args=[2]),self.edit_post_data)
        self.assertEquals(404,response1.status_code)
        self.client.logout()

    def test_user_cannot_delete_entry_shared_to_him(self):
        print 'test_user_cannot_delete_entry_shared_to_him()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_selectedentries_post_data={
                                'sharing_options':[u'selectedentries'],
                                'users_selected': [u'2'],
                                'entries_selected': [u'2']
                              }
        response=self.client.post(reverse('pomlog_share_entries'),self.share_selectedentries_post_data)
        #user2 tries to delete this entry
        self.client.logout()
        self.client.login(username='denny',password='denny')
        response=self.client.get(reverse('pomlog_delete_entry',args=[2]))
        self.assertEquals(404,response.status_code)
        self.client.logout()

    def test_sharing_entry_of_another_user(self):
        print 'test_sharing_entry_of_another_user::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        print 'user1entries=',len(user1entries),'\n',user1entries
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        self.share_not_own_entry_data={
                                'sharing_options':[u'selectedentries'],
                                'users_selected': [u'2'],
                                'entries_selected': [u'4']
                              }
        response=self.client.post(reverse('pomlog_share_entries'),self.share_not_own_entry_data)
        print 'here'
        self.assertEquals(200,response.status_code)
        #need to find the right way,just checking that the entry with id=4 is not shared to user2
        not_own_entry=PomEntry.objects.get(id=4)
        self.assertTrue(user2 not in not_own_entry.sharedwith.all())
        
        self.client.logout()

    def test_unshare_entry(self):
        print 'test_unshare_entry()::'
        self.client.logout()
        self.client.login(username='sajan',password='sajan')
        user1=User.objects.get(username='sajan')
        user2=User.objects.get(username='denny')
        user1entries=PomEntry.objects.filter(author=user1)
        print 'user1entries=',len(user1entries),'\n',user1entries
        for entry in user1entries:
            self.assertTrue(user2 not in entry.sharedwith.all())
        
        self.share_selectedentries_post_data={
                                'sharing_options':[u'selectedentries'],
                                'users_selected': [u'2'],
                                'entries_selected': [u'2']
                              }
        

        response=self.client.post(reverse('pomlog_share_entries'),self.share_selectedentries_post_data)
        entry2=PomEntry.objects.get(id=2)
        self.assertTrue(user2 in entry2.sharedwith.all())
        response1=self.client.post(reverse('pomlog_unshare_entry',kwargs={'entryid':2,'userid':2}))
        self.assertRedirects(response1,reverse('pomlog_entry_archive_index'),status_code=302, target_status_code=200)
        self.assertTrue(user2 not in entry2.sharedwith.all())
