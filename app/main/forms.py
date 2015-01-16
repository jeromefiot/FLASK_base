from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, HiddenField
from wtforms.validators import Required, Length, Email, Regexp
from flask.ext.pagedown.fields import PageDownField
from wtforms import ValidationError
from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class ContactForm(Form):
    nom = StringField('Votre nom', validators=[Length(0, 64)])
    mail = StringField('E-mail', validators=[Length(1, 64), Email()])
    titre = StringField('Titre', validators=[Length(0, 128)])
    message = TextAreaField('Message')
    submit = SubmitField('Envoyer')


class AddPost(Form):
    titre = StringField('Titre', validators=[Length(0, 120)])
    content = PageDownField("Que souhaitez vous ecrire ?", validators=[Required()])
    submit = SubmitField('Publier')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    codepostal = StringField('Code postal', validators=[Length(0, 5)])
    telephone = StringField('Tel.', validators=[Length(0, 15)])
    entreprise = TextAreaField('Entreprise')
    submit = SubmitField('Envoyer')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    telephone = StringField('Tel.', validators=[Length(0, 15)])
    codepostal = StringField('Code postal', validators=[Length(0, 5)])
    entreprise = TextAreaField('Entreprise')
    submit = SubmitField('Envoyer')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Cet Email est pris...')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Cet nom d utilisateur est pris.')

