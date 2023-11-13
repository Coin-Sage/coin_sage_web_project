from django.shortcuts import render

from django.shortcuts import render


def test(request):
    return render(request, 'home.html')  # Assuming you have a template named 'home.html'
