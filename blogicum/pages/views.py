from django.shortcuts import render


def csrf_failure(request, reason=''):
    """Страница 403."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Страница 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Страница 500."""
    return render(request, 'pages/500.html', status=500)
