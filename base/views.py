from django.shortcuts import render

# Create your views here.


def error400(request, exception):
    return render(request, "error_400.html")


def error403(request, exception):
    return render(request, "error_403.html")


def error404(request, exception):
    return render(request, "error_404.html")


def error500(request):
    return render(request, "error_500.html")
