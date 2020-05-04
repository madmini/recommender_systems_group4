from django.shortcuts import render, redirect
from .recommender_helper import recommender_helper as rec

recommender = rec()
def index(request):

    if request.method=='POST':
        user_id=request.POST['user_id']
        recommendations=recommender.get_recommendations_with_data((int)(user_id))
        return render(request,'recommender/rec_index.html',{'user_id': user_id, 'data': recommendations.to_html(index=False, escape=False)})
    else:
        return redirect('/')

def home(request):
    return redirect('/')

