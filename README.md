# Anti-Scam-165

This project aims to develop an AI-powered chatbot designed to combat fraud by integrating advanced Large Language Models (LLMs) with anti-scam information provided by the 165 anti-fraud hotline. The primary goal is to create a reliable and accessible tool that helps users identify potential scam content in messages they receive.

Users will be able to input suspicious text messages or snippets into the chatbot. The LLM, trained on a comprehensive dataset of known fraud tactics and legitimate information from the 165 hotline, will then analyze the input. It will assess various indicators, such as common scam keywords, unusual requests, urgent demands, and inconsistencies, to provide an informed assessment of whether the message is likely fraudulent.

Ultimately, this chatbot will serve as a crucial first line of defense, empowering individuals with the ability to quickly and easily verify the legitimacy of suspicious communications, thereby reducing their vulnerability to various forms of fraud.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy anti_scam_165

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd anti_scam_165
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd anti_scam_165
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd anti_scam_165
celery -A config.celery_app worker -B -l info
```

## Deployment

The following details how to deploy this application.
