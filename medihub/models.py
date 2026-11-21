from django.db import models
from authentication.models import User


class APIRequestLog(models.Model):
    path        = models.CharField(max_length=500)
    method      = models.CharField(max_length=10)
    status_code = models.IntegerField(default=200)
    user        = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    ip          = models.GenericIPAddressField(null=True, blank=True)
    created     = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['created'])]

    def __str__(self):
        return f"{self.method} {self.path} {self.status_code}"
