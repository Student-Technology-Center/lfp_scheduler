from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserData(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	accessToken = models.TextField(null=True)
	refreshToken = models.TextField(null=True)
	accessExpireTime = models.DateTimeField(null=True)
	calendarId = models.TextField(null=True)

''' TODO: Fix instance saving issues (line 19)
@receiver(post_save, sender=User)
def saveUserData(sender, instance, created, **kwargs):
	if created:
		UserData.objects.create(user=instance)
	else:
		instance.userdata.save()
'''
