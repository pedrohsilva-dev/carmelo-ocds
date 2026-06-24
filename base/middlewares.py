import json

from django.contrib.messages import get_messages


class HtmxMessagesMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.headers.get("HX-Request"):

            msgs = []

            for msg in get_messages(request):

                msgs.append(
                    {
                        "message": str(msg),
                        "tags": msg.tags,
                    }
                )

            if msgs:

                response["HX-Trigger"] = json.dumps({"django-messages": msgs})

        return response
