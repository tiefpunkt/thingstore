from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from thingstore.models import Thing
from django.contrib.auth.models import User

def index(request):
	latest_things = Thing.objects.order_by('name')[:5]
	users = User.objects.order_by('-last_login')[:5]
	context = {'latest_things': latest_things, 'users': users}
	return render(request, 'thingstore/index.html', context)
	
def thing(request, thing_id):
	thing = get_object_or_404(Thing, pk=thing_id)
	return render(request, 'thingstore/thing.html', {'thing': thing})

def user(request, username):
	user = get_object_or_404(User, username__iexact=username)
	return render(request, 'thingstore/user.html', {'user': user})
