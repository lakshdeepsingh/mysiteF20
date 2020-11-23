from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Topic, Course, Student, Order
from .forms import SearchForm, OrderForm, ReviewForm


# Create your views here.
def index(request):
    top_list = Topic.objects.all().order_by('id')[:10]
    return render(request, 'myapp/index.html', {'top_list': top_list})

def about(request):
    return render(request, 'myapp/about.html')

def detail(request, topic_id):
    topic=get_object_or_404(Topic,pk=topic_id)
    return render(request, 'myapp/detail.html', {'topic': topic})

def findcourses(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            length = form.cleaned_data['length']
            max_price = form.cleaned_data['max_price']
            courselist = Course.objects.filter(price__lte = max_price)
            if length:
                courselist = courselist.filter(topic__length = length)

            return render(request, 'myapp/results.html', {'courselist':courselist, 'name':name, 'length':length})
        else:
            return HttpResponse('Invalid data')
    else:
        form = SearchForm()
        return render(request, 'myapp/findcourses.html', {'form':form})


def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            courses = form.cleaned_data['courses']
            order = form.save()
            student = order.student
            # courses = order.courses
            status = order.order_status
            order.save()
            if status == 1:
                for c in order.courses.all():
                    student.registered_courses.add(c)
            return render(request, 'myapp/order_response.html', {'courses': courses, 'order':order})
        else:
            return render(request, 'myapp/place_order.html', {'form':form})

    else:
        form = OrderForm()
        return render(request, 'myapp/place_order.html', {'form':form})

def review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            if(rating < 1 or rating > 5):
                form.add_error('rating', 'You must enter a rating between 1 and 5!')
                return render(request, 'myapp/review.html', {'form': form})
            review = form.save()
            course=Course.objects.get(id=review.course.id)
            course.num_reviews+=1
            course.save()
            return redirect('myapp:index')
        else:
            return render(request, 'myapp/review.html', {'form': form})
    else:
        form = ReviewForm()
        return render(request, 'myapp/review.html', {'form': form})
