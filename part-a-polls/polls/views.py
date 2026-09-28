from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Choice, Question, Vote
from .forms import PollForm


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    paginate_by = 5

    def get_queryset(self):
        """
        Return the published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # check if the logged in user already voted on this question
        if self.request.user.is_authenticated:
            context["user_vote"] = Vote.objects.filter(user=self.request.user, question=self.object).first()
        return context


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if question.is_closed:
        return render(request, "polls/detail.html", {
            "question": question,
            "error_message": "This poll is closed.",
        })

    # one vote per user
    if Vote.objects.filter(user=request.user, question=question).exists():
        return render(request, "polls/detail.html", {
            "question": question,
            "error_message": "You have already voted on this poll.",
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        Vote.objects.create(user=request.user, question=question, choice=selected_choice)
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            question = Question.objects.create(
                question_text=form.cleaned_data['question_text'],
                pub_date=timezone.now(),
                owner=request.user,
            )
            # only save the choices that were filled in
            for field in ['choice1', 'choice2', 'choice3', 'choice4', 'choice5']:
                if form.cleaned_data[field]:
                    Choice.objects.create(question=question, choice_text=form.cleaned_data[field])
            messages.success(request, 'Your poll was created!')
            return redirect('polls:detail', pk=question.id)
    else:
        form = PollForm()
    return render(request, 'polls/create_poll.html', {'form': form})


@login_required
def my_polls(request):
    questions = Question.objects.filter(owner=request.user).order_by('-pub_date')
    return render(request, 'polls/my_polls.html', {'questions': questions})


@login_required
def close_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.owner != request.user:
        return HttpResponseForbidden("You can only close your own polls")
    question.is_closed = True
    question.save()
    messages.success(request, 'Poll closed.')
    return redirect('polls:my_polls')


@login_required
def reopen_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.owner != request.user:
        return HttpResponseForbidden("You can only reopen your own polls")
    question.is_closed = False
    question.save()
    messages.success(request, 'Poll reopened.')
    return redirect('polls:my_polls')


@login_required
def delete_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.owner != request.user:
        return HttpResponseForbidden("You can only delete your own polls")

    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Poll deleted.')
        return redirect('polls:my_polls')

    return render(request, 'polls/delete_poll.html', {'question': question})
