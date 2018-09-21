import uuid
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

class LfpTempAppt(models.Model):
    appt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    expire_time = models.DateTimeField(null=True)

    start_time = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    prof = models.CharField(max_length=255)
    class_code = models.CharField(max_length=255)
    email = models.EmailField()
    w_num = models.IntegerField()
    priority = models.IntegerField()
    creator = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
