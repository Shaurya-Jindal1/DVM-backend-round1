import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Question, Choice, Vote


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )

    def test_pagination(self):
        for i in range(7):
            create_question(question_text="Question " + str(i), days=-1)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(len(response.context["latest_question_list"]), 5)
        response = self.client.get(reverse("polls:index") + "?page=2")
        self.assertEqual(len(response.context["latest_question_list"]), 2)


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class VoteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.question = create_question("Favourite colour?", days=-1)
        self.choice = Choice.objects.create(question=self.question, choice_text="Red")

    def test_have_to_login_to_vote(self):
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        self.assertEqual(response.status_code, 302)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 0)

    def test_vote(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        self.assertRedirects(response, reverse('polls:results', args=(self.question.id,)))
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 1)

    def test_cant_vote_twice(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        self.assertContains(response, "You have already voted on this poll.")
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 1)
        self.assertEqual(Vote.objects.count(), 1)

    def test_no_choice_selected(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {})
        self.assertContains(response, "You didn&#x27;t select a choice.")

    def test_cant_vote_on_closed_poll(self):
        self.question.is_closed = True
        self.question.save()
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        self.assertContains(response, "This poll is closed.")
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 0)


class CreatePollTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_required(self):
        response = self.client.get(reverse('polls:create_poll'))
        self.assertEqual(response.status_code, 302)

    def test_create_poll(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('polls:create_poll'), {
            'question_text': 'Tabs or spaces?',
            'choice1': 'Tabs',
            'choice2': 'Spaces',
            'choice3': '',
            'choice4': '',
            'choice5': '',
        })
        question = Question.objects.get(question_text='Tabs or spaces?')
        self.assertRedirects(response, reverse('polls:detail', args=(question.id,)))
        self.assertEqual(question.owner, self.user)
        self.assertEqual(question.choice_set.count(), 2)

    def test_need_two_choices(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('polls:create_poll'), {
            'question_text': 'Only one choice?',
            'choice1': 'Yes',
            'choice2': '',
        })
        self.assertEqual(Question.objects.count(), 0)


class OwnerTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.other = User.objects.create_user(username='other', password='testpass123')
        self.question = create_question("My poll", days=-1)
        self.question.owner = self.owner
        self.question.save()

    def test_owner_can_close_poll(self):
        self.client.login(username='owner', password='testpass123')
        self.client.get(reverse('polls:close_poll', args=(self.question.id,)))
        self.question.refresh_from_db()
        self.assertTrue(self.question.is_closed)

    def test_owner_can_reopen_poll(self):
        self.question.is_closed = True
        self.question.save()
        self.client.login(username='owner', password='testpass123')
        self.client.get(reverse('polls:reopen_poll', args=(self.question.id,)))
        self.question.refresh_from_db()
        self.assertFalse(self.question.is_closed)

    def test_other_user_cant_close_poll(self):
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('polls:close_poll', args=(self.question.id,)))
        self.assertEqual(response.status_code, 403)
        self.question.refresh_from_db()
        self.assertFalse(self.question.is_closed)

    def test_owner_can_delete_poll(self):
        self.client.login(username='owner', password='testpass123')
        self.client.post(reverse('polls:delete_poll', args=(self.question.id,)))
        self.assertEqual(Question.objects.count(), 0)

    def test_other_user_cant_delete_poll(self):
        self.client.login(username='other', password='testpass123')
        response = self.client.post(reverse('polls:delete_poll', args=(self.question.id,)))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Question.objects.count(), 1)

    def test_my_polls_only_shows_my_polls(self):
        create_question("Someone elses poll", days=-1)
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(reverse('polls:my_polls'))
        self.assertContains(response, "My poll")
        self.assertNotContains(response, "Someone elses poll")
