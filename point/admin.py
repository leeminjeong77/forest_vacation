from django.contrib import admin

# Register your models here.

from .models import PointTransaction

admin.site.register(PointTransaction)