from django.core.mail import send_mail

from transkribusWorkflow.settings import DEFAULT_FROM_EMAIL


def send_welcome_email(user_email, username, temp_password):
    subject = "Your TWF Account - Initial Login Details"
    message = (f"Welcome to TWF!\n "
               f"Your username is: {username}\n "
               f"Your temporary password is: {temp_password}. Please reset it upon login.")

    send_mail(subject, message, DEFAULT_FROM_EMAIL, [user_email])


def send_reset_email(user_email, username, temp_password):
    subject = "Your TWF Account - Password Reset"
    message = (f"Hello {username},\n "
               f"Your temporary password is: {temp_password}. Please reset it upon login.")

    send_mail(subject, message, DEFAULT_FROM_EMAIL, [user_email])