from flask.ext.wtf import Form

from wtforms import SelectField, StringField, PasswordField
from wtforms.validators import DataRequired
from wtforms import widgets

from .calminerva import SEASONS


class RequiredInput(widgets.Input):
    def __call__(self, *args, **kwargs):
        rv = super().__call__(*args, **kwargs)
        rv = rv[:-1] + ' required' + '>'
        return rv


class TextInput(widgets.TextInput, RequiredInput):
    pass


class PasswordInput(RequiredInput, widgets.PasswordInput):
    pass


class MinervaForm(Form):
    """Form for Minerva login.

    user/secret can either be the ID/PIN combination or the email/password.
    """
    user = StringField(
        'user',
        validators=[DataRequired()],
        description='SID / Email',
        widget=TextInput(),
    )
    secret = PasswordField(
        'secret',
        validators=[DataRequired()],
        description='PIN / Password',
        widget=PasswordInput(),
    )
    season = SelectField(
        'season',
        choices=[(x, x.capitalize()) for x in SEASONS],
        validators=[DataRequired()],
        description='Season',
    )
    # Dynamic field
    year = SelectField(
        'year',
        coerce=int,
        validators=[DataRequired()],
        description='Year',
    )