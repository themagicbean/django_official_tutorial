# polls/views file

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse
from django.views import generic

from .models import Choice, Question

#revised generic views from bottom of official tutorial no.4

from django.utils import timezone

class IndexView(generic.ListView):
	
	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'
	# gives variable name to be used in template
	
	def get_queryset(self):
	#new version returns last 5 published questions
	#d/n include future published questions
		return Question.objects.filter(
			pub_date__lte=timezone.now() #lte = <=
		).order_by('-pub_date')[:5]
	
	""" old version pre-fix for date check:
	def get_queryset(self):
		return Question.objects.order_by('-pub_date')[:5]
	"""
		
		
class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html' # default would have been polls/Question_detail.html

	def get_queryset(self):
	#d/n include future pub'd questions
		return Question.objects.filter(
			pub_date__lte=timezone.now()
		)

		
class ResultsView(generic.DetailView):
	model = Question
	template_name = 'polls/results.html'

	# need to add get_queryset and test to prevent future choice viewing

""" old hard-codd views, replaced above
def index(request):
	latest_question_list = Question.objects.order_by('-pub_date')[:5]
	#template = loader.get_template('polls/index.html')
	# don't need that if use render
	context = {
		'latest_question_list': latest_question_list,
	}
	#return (HttpResponse(template.render(context, request))
	#better version (there is also a get_list_or_404 function)
	return render(request, 'polls/index.html', context)
	
def detail(request, question_id):
	# long version
	
	#try:
	#	question = Question.objects.get(pk=question_id)
	#except Question.DoesNotExist:
	#	raise Http404("Question does not exist.")
	#return render(request, 'polls/detail.html', {'question': question})
	
	# short version
	question = get_object_or_404(Question, pk=question_id)
	return render(request, 'polls/detail.html', {'question': question})
	
def results(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	return render(request, 'polls/results.html', {'question': question})
"""
	
# has race problem, see Avoiding race conditions using F()
# not modified when switched to generic views
def vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = question.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		return render(request, 'polls/detail.html', {
			'question': question,
			'error_message': "You didn't select a choice.",
		})
	else:
		selected_choice.votes += 1
		selected_choice.save()
		# always redirect after successful handling of post data
		# prevents double-processing of post data
		return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))