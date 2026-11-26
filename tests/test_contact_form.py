import pytest
from django.core import mail
from wagtail.contrib.forms.models import FormSubmission

pytestmark = pytest.mark.django_db


def test_contact_form_renders_fields(client, seeded):
    html = client.get("/contact/").content.decode()
    for name in ("name", "email", "message"):
        assert f'name="{name}"' in html


def test_valid_submission_stores_and_emails(client, seeded):
    response = client.post(
        "/contact/",
        {"name": "Ada", "email": "ada@example.com", "message": "Hello there"},
    )
    assert response.status_code == 200
    assert "Thanks for your message!" in response.content.decode()

    submission = FormSubmission.objects.get(page=seeded["contact"])
    assert submission.get_data()["email"] == "ada@example.com"

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "New contact form submission"
    assert "Hello there" in mail.outbox[0].body


def test_invalid_submission_shows_errors(client, seeded):
    response = client.post("/contact/", {"name": "", "email": "not-an-email", "message": ""})
    assert response.status_code == 200
    assert 'role="alert"' in response.content.decode()
    assert not FormSubmission.objects.exists()
    assert len(mail.outbox) == 0
