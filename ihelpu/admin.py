from django.contrib import admin
from ihelpu.models import Topic


class TopicAdmin(admin.ModelAdmin):
    pass

admin.site.register(Topic, TopicAdmin)
