from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import NewsQuizData
from .serializers import NewsQuizSerializer, NewsQuizAnsweredSerializer


class NewsQuizViewSet(viewsets.ViewSet):
    """A viewset to handle quiz."""
    http_method_names = ('get', 'post')
    serializer_class = NewsQuizAnsweredSerializer

    def list(self, request):
        """Default list action that returns random quiz question"""
        news_for_quiz = NewsQuizData.objects.get_random_news()
        if not news_for_quiz:
            return Response({"error": "No quiz questions available"}, status=status.HTTP_404_NOT_FOUND)

        serializer = NewsQuizSerializer(news_for_quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get's and returns random news from model."""
        news_for_quiz = NewsQuizData.objects.get_random_news()
        if not news_for_quiz:
            return Response({"error": "No quiz questions available"}, status=status.HTTP_404_NOT_FOUND)

        serializer = NewsQuizSerializer(news_for_quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['post'])
    def answer(self, request):
        """Get's answer from user and checks whether the answer is correct or wrong."""
        serializer = NewsQuizAnsweredSerializer(data=request.data)

        if serializer.is_valid():
            news_id = serializer.validated_data['id']
            user_answer = serializer.validated_data['answer']
            real_answer = NewsQuizData.objects.get_label_of_news(news_id)
            
            if not real_answer:
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
                
            real_answer = real_answer.label
            if real_answer == 1:
                real_answer = True
            elif real_answer == 0:
                real_answer = False

            return Response({'result': real_answer == user_answer}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)