from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from .models import NewsQuizData


class NewsQuizModelTests(TestCase):
    def setUp(self):
        self.valid_quiz = {
            'news_title': 'Test Quiz News Title',
            'news_description': 'This is a test description for the quiz news article.',
            'label': True
        }

    def test_create_valid_quiz(self):
        quiz = NewsQuizData.objects.create(**self.valid_quiz)
        self.assertEqual(quiz.news_title, self.valid_quiz['news_title'])
        self.assertTrue(quiz.label)

    def test_str_representation(self):
        quiz = NewsQuizData.objects.create(**self.valid_quiz)
        self.assertEqual(str(quiz), 'Test Quiz News Title')

    def test_get_random_news(self):
        # Create multiple quiz items
        quiz1 = NewsQuizData.objects.create(**self.valid_quiz)
        quiz2 = NewsQuizData.objects.create(
            news_title='Another Quiz Title',
            news_description='Another test description',
            label=False
        )
        
        # Test getting random news
        random_news = NewsQuizData.objects.get_random_news()
        self.assertIn(random_news, [quiz1, quiz2])

    def test_get_label_of_news(self):
        quiz = NewsQuizData.objects.create(**self.valid_quiz)
        retrieved_quiz = NewsQuizData.objects.get_label_of_news(quiz.id)
        self.assertEqual(retrieved_quiz.label, self.valid_quiz['label'])

    def test_get_nonexistent_label(self):
        result = NewsQuizData.objects.get_label_of_news(999)
        self.assertIsNone(result)

    def test_empty_database_random_news(self):
        self.assertIsNone(NewsQuizData.objects.get_random_news())

    def test_create_quiz_without_description(self):
        with self.assertRaises(ValidationError):
            quiz = NewsQuizData.objects.create(
                news_title='Title Only Quiz',
                label=True
            )
            quiz.full_clean()


class NewsQuizAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.quiz = NewsQuizData.objects.create(
            news_title='Test Quiz News',
            news_description='Test quiz description',
            label=True
        )

    def test_get_random_quiz(self):
        response = self.client.get('/api/v1/quiz/random/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertIn('news_title', response.data)
        self.assertIn('news_description', response.data)

    def test_submit_correct_answer(self):
        response = self.client.post(
            '/api/v1/quiz/answer/',
            {'id': self.quiz.id, 'answer': True},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['correct'])
        self.assertEqual(response.data['message'], 'Correct answer!')

    def test_submit_wrong_answer(self):
        response = self.client.post(
            '/api/v1/quiz/answer/',
            {'id': self.quiz.id, 'answer': False},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['correct'])
        self.assertEqual(response.data['message'], 'Wrong answer!')

    def test_submit_invalid_quiz_id(self):
        response = self.client.post(
            '/api/v1/quiz/answer/',
            {'id': 999, 'answer': True},
            format='json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Quiz not found')

    def test_submit_invalid_answer_format(self):
        response = self.client.post(
            '/api/v1/quiz/answer/',
            {'id': self.quiz.id, 'answer': 'invalid'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_submit_missing_fields(self):
        # Test missing ID
        response = self.client.post(
            '/api/v1/quiz/answer/',
            {'answer': True},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

        # Test missing answer
        response = self.client.post(
            '/api/v1/quiz/answer/',
            {'id': self.quiz.id},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_multiple_random_quizzes(self):
        # Create additional quiz items
        NewsQuizData.objects.create(
            news_title='Quiz 2',
            news_description='Description 2',
            label=False
        )
        NewsQuizData.objects.create(
            news_title='Quiz 3',
            news_description='Description 3',
            label=True
        )

        # Get multiple random quizzes and ensure they're not always the same
        responses = set()
        for _ in range(5):
            response = self.client.get('/api/v1/quiz/random/')
            responses.add(response.data['news_title'])
        
        # We should get at least 2 different quizzes in 5 attempts
        self.assertGreater(len(responses), 1)

    def test_empty_database_random_quiz(self):
        NewsQuizData.objects.all().delete()
        response = self.client.get('/api/v1/quiz/random/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'No quiz questions available')
