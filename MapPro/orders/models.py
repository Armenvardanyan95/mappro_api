from django.db import models
from django.contrib.auth.models import User


class ColorMarker(models.Model):
    name = models.CharField(max_length=250)
    color = models.CharField(max_length=300)
    default = models.BooleanField(default=False)
    new = models.BooleanField(default=False)
    image = models.TextField(null=True)


class Order(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500, blank=True)
    address = models.CharField(max_length=500)
    mobile_phone = models.CharField(max_length=5000, blank=True)
    date = models.DateTimeField(blank=True, null=True)
    time_from = models.TimeField(blank=True, null=True)
    time_to = models.TimeField(blank=True, null=True)
    color_marker = models.ForeignKey(ColorMarker, null=True)
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    problem = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True)

    @property
    def get_user_details(self):
        return {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "id": self.user.id
        }

    @property
    def get_color_marker_details(self):
        return {
            "image": self.color_marker.image,
            "color": self.color_marker.color,
            "id": self.color_marker.id
        }

    @property
    def get_rank(self):
        return Order.objects.filter(pk__lte=self.pk).count()

    @property
    def get_not_archived_rank(self):
        return Order.objects.filter(pk__lte=self.pk, is_archived=False).count()



