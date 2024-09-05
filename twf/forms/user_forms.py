"""Forms for the twf app."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Column, Row, Div


class LoginForm(AuthenticationForm):
    """Form for logging in users."""

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'username',
            'password',
            Div(
                Submit('submit', 'Login', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class ChangePasswordForm(PasswordChangeForm):
    """Form for changing the password of a user."""

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'old_password',
            'new_password1',
            'new_password2',
            Div(
                Submit('submit', 'Change Password', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class UserManagementForm(forms.Form):
    """Form for managing users."""

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('user', css_class='form-group col-6 mb-0'),
                Column('group', css_class='form-group col-6 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
