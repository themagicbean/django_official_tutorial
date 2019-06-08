import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Question

# need to add results test (no view future Qs, like detail views)

def create_question(question_text, days):
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionDetailViewTests(TestCase):
	
	def test_future_question(self):
		# detail view of future Q returns 404
		future_question = create_question(question_text='Future question.', days=5)
		url = reverse('polls:detail', args=(future_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_past_question(self):
		#past Qs displayed
		past_question = create_question(question_text='Past Question.', days=-5)
		url = reverse('polls:detail', args=(past_question.id,))
		response = self.client.get(url)
		self.assertContains(response, past_question.question_text)
	
class QuestionIndexViewTests(TestCase):

	def test_no_questions(self):
	#message if no questions exist
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list', [])
		
	def test_past_question(self):
	# Qs with pub date in past are displayed on index
		create_question(question_text="Past question.", days=-30)
		response = self.client.get(reverse('polls:index')))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past question.>']
		)
		
	def test_future_question(self):
	# Qs w/ pub date in future are NOT displayed
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list', [])
			
	def test_future_question_and_past_question(self):
	# if both future and past Qs, only past are displayed
		create_question(question_text="Past question.", days=-30)
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past question.>']
		)

	def test_two_past_questions(self):
	# can display multiple questions.
		create_question(question_text="Past question 1.", days=-30)
		create_question(question_text="Past question 2.", days=-5)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class QuestionModelTests(TestCase):

	def test_was_published_recently_with_future_question(self):
	# returns false if question pub'd in the future
	
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		self.assertIs(future_question.was_published_recently(), False)
	
	def test_was_published_recently_with_old_question(self):
	# returns false for q if pubdate > 1 day old
	
		time = timezone.now() - datetime.timedelta(days=1, seconds=1)
		old_question = Question(pubdate=time)
		self.assertIS(old_question.was_published_recently(), False)
		
	def test_was_published_recently_with_recent_question(self):
	# returns True for q w/ pubdate w/in last day
	
		time = timezone.now() - datetime.timedelta(hours=23, minutes=59)
		recent_question = Question(pub_date=time)
		self.assertIs(recent_question.was_published_recently(), True)
	
	# should probably add check for Qs w/o Cs