from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.models import Site

'''
class UserData(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	accessToken = models.TextField(null=True)
	refreshToken = models.TextField(null=True)
	accessExpireTime = models.DateTimeField(null=True)
	calendarId = models.TextField(null=True)
'''

class LfpData(models.Model):
	accessToken = models.TextField()
	refreshToken = models.TextField()
	accessExpireTime = models.DateTimeField()
	calendarId = models.TextField()
	email = models.EmailField()

	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		self.__class__.objects.exclude(id=self.id).delete()
		super(LfpData, self).save(*args, **kwargs);

	@classmethod
	def load(cls):
		try:
			return cls.objects.get()
		except cls.DoesNotExist:
			return cls()

''' TODO: Fix instance saving issues (line 19)
@receiver(post_save, sender=User)
def saveUserData(sender, instance, created, **kwargs):
	if created:
		UserData.objects.create(user=instance)
	else:
		instance.userdata.save()
'''
