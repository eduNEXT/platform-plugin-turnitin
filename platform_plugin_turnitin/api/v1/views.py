"""
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication


class PlagiarismView(APIView):
    """
    """

    authentication_classes = (SessionAuthentication,)


    def get(self, request, format=None):
        """
        """
        return Response({"status": "ok"})

    def post(self, request, format=None):
        """
        """
        return Response({"status": "ok"})
