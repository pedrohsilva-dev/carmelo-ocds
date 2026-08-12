from django.shortcuts import render

# Create your views here.


def error400(request, exception):
    return render(request, "error_400.html", status=400)


def error403(request, exception):
    return render(request, "error_403.html", status=403)


def error404(request, exception):
    return render(request, "error_404.html", status=404)


def error500(request):
    return render(request, "error_500.html", status=500)
