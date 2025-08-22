from django.contrib import admin

# Register your models here.

from .models import Reward, UserReward

admin.site.register(Reward)

admin.site.register(UserReward)