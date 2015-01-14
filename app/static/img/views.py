from flask import render_template, redirect, url_for, abort, flash, request, current_app
from flask.ext.login import login_required, current_user

from flask.ext.admin import Admin, BaseView, expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin

from . import main
from ..email import send_email
from .forms import EditProfileForm, EditProfileAdminForm, AddClientForm, ContactForm
from .. import db, admin
from ..models import Role, User, Client, Document
from ..decorators import admin_required


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES PUBLIQUES
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    ###################################################
    # prevoir 2 mails : un pour admin et un pour envoyeur
    ###################################################
    
    if form.validate_on_submit():
        app = current_app._get_current_object()
        # envoi a l'admin
        send_email(app.config['FLASKY_ADMIN'], form.titre.data,
                       '/mail/contact',
                       envoyeur=form.nom.data,
                       mail=form.mail.data,
                       message=form.message.data,
                       depuis=app.config['FLASKY_MAIL_SUBJECT_PREFIX'])
        # envoi merci a l'envoyeur
        send_email(form.mail.data, 'Confirmation message',
                       '/mail/merci_contact')
        flash('Message bien envoye !')
        return redirect(url_for('main.index'))
    return render_template('contact.html', form=form)


@main.route('/credits')
def credits():
    return render_template('credits.html')


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES INSCRITS
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------


@main.route('/user/<username>')
@login_required
###################################################
# prevoir un login restricted a cet utilisateur only
###################################################
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    clients = Client.query.filter_by(user_id=user.id).all()
    return render_template('user.html', user=user, clients=clients)


@main.route('/user/clients/<username>')
@login_required
###################################################
# prevoir un login restricted a cet utilisateur only
###################################################
def clients_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    clients = Client.query.filter_by(user_id=user.id).all()
    return render_template('clients_user.html', user=user, clients=clients)


@main.route('/user/ajout_client/<username>', methods=['GET', 'POST'])
@login_required
###################################################
# prevoir un login restricted a cet utilisateur only
###################################################
def add_user(username):
    form = AddClientForm()
    user = User.query.filter_by(username=username).first_or_404()
    if form.validate_on_submit():
        client = Client(nom=form.nom.data,
                    entreprise=form.entreprise.data,
                    telephone = form.telephone.data,
                    mail = form.mail.data,
                    adresse = form.adresse.data,
                    codepostal = form.codepostal.data,
                    user_id=current_user.id)
        db.session.add(client)
        flash('Client ajoute.')
        return redirect(url_for('.clients_user', username=current_user.username))
    return render_template('add_user.html', user=user, form=form)



@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.telephone = form.telephone.data
        current_user.location = form.location.data
        current_user.codepostal = form.codepostal.data
        current_user.entreprise = form.entreprise.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.telephone.data = current_user.telephone
    form.location.data = current_user.location
    form.codepostal.data = current_user.codepostal
    form.entreprise.data = current_user.entreprise
    return render_template('edit_profile.html', form=form)

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES @ADMIN_REQUIRED
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.telephone = form.telephone.data
        user.location = form.location.data
        user.codepostal = form.codepostal.data
        user.entreprise = form.entreprise.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.telephone.data = user.telephone
    form.location.data = user.location
    form.codepostal.data = user.codepostal
    form.entreprise.data = user.entreprise
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/list_users/', methods=['GET', 'POST'])
@login_required
@admin_required
def list_users():
    user = User.query.all()
    if request.method == 'POST':
        flash("Suppression de id")
        
    return render_template('list_users.html', user=user)


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES ADMIN
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

class UserModelView(ModelView):
    
    # remove "password_hash"
    # http://flask-admin.readthedocs.org/en/latest/api/mod_model/#flask.ext.admin.model.BaseModelView)
    column_exclude_list = ('password_hash')
    
    # Accessible only by admin
    @admin_required
    def is_accessible(self):    
        return current_user.is_administrator()

class ClientModelView(ModelView):
    
    # Accessible only by admin
    @admin_required
    def is_accessible(self):    
        return current_user.is_administrator()

class DocumentModelView(ModelView):
    
    # Accessible only by admin
    @admin_required
    def is_accessible(self):    
        return current_user.is_administrator()
    
admin.add_view(UserModelView(User, db.session))
admin.add_view(ClientModelView(Client, db.session))
admin.add_view(DocumentModelView(Document, db.session))

# pour la vue avec tous les arg, sinon Myview3
#admin.add_view(ModelView(User, db.session))
