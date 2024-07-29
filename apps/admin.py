from django.contrib import admin
from .models import Blogs,Tag,Comments,MailNotification,BlogView


admin.site.register(Blogs)
admin.site.register(Tag)
admin.site.register(Comments)
admin.site.register(MailNotification)
admin.site.register(BlogView)
