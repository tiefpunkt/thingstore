from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

# Create your models here.

class Thing(models.Model):
	name = models.CharField(max_length=255)
	location = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	owner = models.ForeignKey(User)
	
	def __unicode__(self):
		return self.name;

class Metric(models.Model):
	thing = models.ForeignKey(Thing, related_name='metrics')
	name = models.CharField(max_length=255)
	unit = models.CharField(max_length=64, blank=True)
	
	class Meta:
		unique_together = (("name","thing"),)
	
	def __unicode__(self):
		return self.name;
	
	@property
	def current_value(self):
		try:
			return Value.objects.filter(metric = self)[:1].get().value
		except Value.DoesNotExist:
			return None
	
	@current_value.setter
	def current_value(self, value):
		v = Value(metric = self, value = value)
		v.save()
	

class Value(models.Model):
	metric = models.ForeignKey(Metric)
	value = models.FloatField()
	timestamp = models.DateTimeField(default=datetime.utcnow())
	
	class Meta:
		ordering = ['-timestamp']
	
