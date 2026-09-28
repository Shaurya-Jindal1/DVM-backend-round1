# DVM Backend Task 1 - Part A (Polls App)

This is the polls app from the official Django tutorial (parts 1-8) plus some extra features I added on top of it.

Made with Python 3.13 and Django 6.1.1

## How to run

```
python -m venv .venv
.venv\Scripts\activate        (on mac/linux: source .venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/polls/ in the browser. The admin page is at http://127.0.0.1:8000/admin/

## Tutorial parts

- Part 1-4: polls app with Question and Choice models, index/detail/results pages and voting (using generic views)
- Part 5: tests, and fixed the bug in `was_published_recently()`. Future questions don't show up on any page
- Part 6: added a stylesheet and background image
- Part 7: customized the admin (choices inline, list_display, filters, search, changed the admin header)
- Part 8: installed django-debug-toolbar (shows up on the right side of the page when running locally)

## Extra features I added

**User accounts**
- Sign up page at `/accounts/signup/`, login and logout use Django's built in auth views
- After signing up you get sent to the login page

**Voting**
- You have to be logged in to vote
- Each user can only vote once on a poll (I made a Vote model that stores who voted for what)
- The poll page shows which option you voted for if you already voted

**Creating polls**
- Logged in users can create their own polls at `/polls/create/`
- A poll needs a question and at least 2 choices (max 5)

**Managing your polls**
- The "My Polls" page shows all the polls you made
- You can close a poll (people can't vote on it anymore but results are still visible), reopen it or delete it
- Only the person who made the poll can close/reopen/delete it

**Pagination**
- The polls list shows 5 polls per page

## Tests

```
python manage.py test
```

Has the tests from the tutorial and some tests for the extra features (voting, creating polls, closing/deleting polls, sign up).
