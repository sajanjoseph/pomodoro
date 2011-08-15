from django.contrib import admin
from pomlogger.models import PomEntry,PomCategory

class PomEntryAdmin(admin.ModelAdmin):
	ordering=['today']
class PomCategoryAdmin(admin.ModelAdmin):	
	ordering=['name']

admin.site.register(PomEntry,PomEntryAdmin)
admin.site.register(PomCategory,PomCategoryAdmin)

