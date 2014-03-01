from django.conf import settings
from django.contrib.auth.models import User, check_password
from thingstore.models import APIKey

class APIKeyBackend(object):

	def authenticate(self, apikey=None):
		try:
			apikey_obj = APIKey.objects.get(token = apikey)
		except APIKey.DoesNotExist:
			return None
		return apikey_obj.user


	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
