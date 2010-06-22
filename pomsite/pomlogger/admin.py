from django.contrib import admin
from pomlogger.models import PomEntry,PomCategory

class PomEntryAdmin(admin.ModelAdmin):
	pass
class PomCategoryAdmin(admin.ModelAdmin):	
	ordering=['name']

admin.site.register(PomEntry,PomEntryAdmin)
admin.site.register(PomCategory,PomCategoryAdmin)

