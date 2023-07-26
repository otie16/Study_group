from django.contrib import admin

# Register your models here.
from .models import Room, Topic, Message

# Registering our room model with the admin panel
# So that it can be viewed in the admin panel
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)