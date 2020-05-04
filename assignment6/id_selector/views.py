from django.shortcuts import render, redirect
from .forms import UserIdForm

def index(request):
   return render(request,'id_selector/index.html', {'user_id': ''})

def get_user_id(request):
    # keep the "index" path
    request.path = ''
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserIdForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            return render(request, 'id_selector/index.html', {'user_id':form.cleaned_data.get('user_id')})
    return render(request,'id_selector/index.html', {'user_id': '', 'errormsg':'Invalid User!'})

def recommend_movies(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserIdForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # Route to second page
            return redirect('recommender')
    return render(request,'id_selector/index.html', {'user_id': '', 'errormsg':'Error happened!'})
