from rest_framework.pagination import PageNumberPagination as drf_PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


class PageNumberPaginator(drf_PageNumberPagination):
    def get_last_link(self):
        url = self.request.build_absolute_uri()
        page_number = self.page.paginator.num_pages
        return replace_query_param(url, self.page_query_param, page_number)

    def get_first_link(self):
        url = self.request.build_absolute_uri()
        page_number = 1
        return replace_query_param(url, self.page_query_param, page_number)

    def get_paginated_response(self, data):
        return Response(
            {
                'count': self.page.paginator.count,
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'first': self.get_first_link(),
                'last': self.get_last_link(),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data,
            }
        )
