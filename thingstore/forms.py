from django.forms import ModelForm
from thingstore.models import Thing

class ThingForm(ModelForm):
	class Meta:
		model = Thing
		exclude = ['owner']
