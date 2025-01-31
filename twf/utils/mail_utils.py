from django.core.mail import send_mail


def send_welcome_email(user_email, username, temp_password):
    subject = "Your TWF Account - Initial Login Details"
    message = (f"Welcome to TWF!\n "
               f"Your username is: {username}\n "
               f"Your temporary password is: {temp_password}. Please reset it upon login.")
    from_email = "no-reply@yourdomain.com"

    send_mail(subject, message, from_email, [user_email])

