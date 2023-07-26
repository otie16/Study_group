from django.forms import ModelForm
# from django import forms
from .models import Room, Message

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

# class MessageForm(ModelForm):
#     class Meta:
#         model = Message
#         fields = '__all__'