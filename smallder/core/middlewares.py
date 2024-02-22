class Middleware:

    def __init__(self, spider):
        self.spider = spider

    def request_after(self, request):
        if request.callback.__name__ in ["list_html_parse", "list_json_parse"]:

            request = self.list_request_after(request)

        elif request.callback.__name__ in ["detail_html_parse", "detail_json_parse"]:

            request = self.detail_request_after(request)

        else:
            request = request

        return request

    def response_before(self, response):
        if response.request.callback.__name__ in ["list_html_parse", "list_json_parse"]:
            response = self.list_response_before(response)
        elif response.request.callback.__name__ in ["detail_html_parse", "detail_json_parse"]:
            response = self.detail_response_before(response)
        else:
            response = response
        return response

    def list_request_after(self, request):
        return request

    def detail_request_after(self, request):
        return request

    def list_response_before(self, response):
        return response

    def detail_response_before(self, response):
        return response
