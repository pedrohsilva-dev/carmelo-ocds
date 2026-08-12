"""Template tags de navegação: destaca (active) o item atual da sidebar."""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active_on(context, *url_names):
    """Retorna 'active' quando a URL atual corresponde a um dos `url_names`.

    Uso: {% active_on 'list_member' 'show_member' 'update_member' %}
    """
    request = context.get("request")
    if request is None:
        return ""

    current = getattr(request.resolver_match, "url_name", None)
    if current in url_names:
        return "active"

    return ""
