from django.contrib import admin

# Register your models here.

from .models import Quest, RandomQuest

admin.site.register(Quest)
admin.site.register(RandomQuest)
