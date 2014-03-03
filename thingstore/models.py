from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.timezone import now
import calendar, string, random

# Create your models here.

class Thing(models.Model):
	name = models.CharField(max_length=255)
	location = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	owner = models.ForeignKey(User)
	
	def __unicode__(self):
		return self.name;
		
	def get_absolute_url(self):
		return reverse('thingstore.views.thing', args=[str(self.id)])

class Metric(models.Model):
	thing = models.ForeignKey(Thing, related_name='metrics')
	name = models.CharField(max_length=255)
	unit = models.CharField(max_length=64, blank=True)
	
	class Meta:
		unique_together = (("name","thing"),)
	
	def __unicode__(self):
		return self.name;
	
	""" Return most recent value for metric """
	@property
	def current_value(self):
		try:
			return Value.objects.filter(metric = self)[:1].get().value
		except Value.DoesNotExist:
			return None
	
	""" set current value by adding a new Value with current timestamp"""
	@current_value.setter
	def current_value(self, value):
		v = Value(metric = self, value = value)
		v.save()
	
	""" Return datetime of last update """
	@property
	def last_update(self):
		try:
			return Value.objects.filter(metric = self)[:1].get().timestamp
		except Value.DoesNotExist:
			return None

class Value(models.Model):
	metric = models.ForeignKey(Metric, related_name='values')
	value = models.FloatField()
	timestamp = models.DateTimeField(default=now)
	
	@property
	def js_time(self):
		return calendar.timegm(self.timestamp.timetuple())*1000
	
	class Meta:
		ordering = ['-timestamp']
	
class APIKey(models.Model):
	token = models.CharField(max_length=255, unique = True)
	user = models.ForeignKey(User, related_name='apikeys')

	@classmethod
	def create(cls, user):
		apikey = cls(user=user)
		apikey.token = ''.join(random.sample(string.lowercase+string.uppercase+string.digits,32))
		return apikey
	
