from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from core.api_response import APIResponse


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard DRF Pagination for Medihub APIs.
    Default page size: 20
    Max page size: 100
    Query param: ?page_size=X
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(APIResponse.success(
            message="Data retrieved successfully",
            title="results",
            data={
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        ))
