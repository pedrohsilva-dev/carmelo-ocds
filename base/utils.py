from django.core.paginator import Paginator


def paginate(queryset, request, per_page=10, page_param="page"):
    """Página um queryset com base no parâmetro GET (padrão: `page`)."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get(page_param, 1)
    return paginator.get_page(page_number)
