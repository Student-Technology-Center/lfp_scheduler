from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.models import Site

class LfpData(models.Model):
    accessToken = models.TextField(null=True)
    refreshToken = models.TextField(null=True)
    accessExpireTime = models.DateTimeField(null=True)
    calendarId = models.TextField(null=True)
    email = models.EmailField(null=True)

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(LfpData, self).save(*args, **kwargs);

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()
