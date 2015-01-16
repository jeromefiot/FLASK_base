from flask import render_template, redirect, url_for, abort, flash, request
from flask.ext.login import login_required, current_user

from flask.ext.admin import Admin, BaseView, expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from sqlalchemy import or_
from flask.ext.admin.contrib.fileadmin import FileAdmin

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, ContactForm, AddPost
from .. import db, admin
from ..models import Role, User, Post
from ..decorators import admin_required


def login_invalid(nom):
# check user is not on other user page and not admin
    if current_user.username != nom and not current_user.is_administrator():
        return True


# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES PUBLIQUES
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

@main.route('/')
def index():
    billets = Post.query.filter_by(author_id='1').all()
    if len(billets)>0 :
        billets = billets.pop()
        if len(billets.content)>120:
            contenu=billets.content[:120]
        else:
            contenu=billets.content
    else:
        contenu="Test"

    return render_template('index.html', billet=billets, contenu=contenu)


@main.route('/blog', methods=['GET', 'POST'])
def blog():
    form = AddPost()
    if current_user.is_administrator() and form.validate_on_submit():
            post=Post(titre=form.titre.data,
                      content=form.content.data,
                      support='0',
                      author_id=current_user.id)
            db.session.add(post)
            return redirect(url_for('.blog'))
    billets = Post.query.order_by(Post.timestamp.desc()).filter(Post.support=='0').all()
    return render_template('blog.html', form=form, billets=billets)


@main.route('/contact')
def contact():
    form = ContactForm()
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


@main.route("/site-map")
def site_map():
    links = {"home":url_for('main.index')}
    return render_template('content.html', content=links)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# PAGES INSCRITS
# ---------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if login_invalid(current_user.username) :
        return redirect(url_for('auth.login'))
    else:
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
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('Profil mis a jour.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.telephone.data = user.telephone
    form.location.data = user.location
    form.codepostal.data = user.codepostal
    form.about_me.data = user.about_me
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


class PostModelView(ModelView):
    # Accessible only by admin
    @admin_required
    def is_accessible(self):
        return current_user.is_administrator()


admin.add_view(UserModelView(User, db.session))
admin.add_view(PostModelView(Post, db.session))

# pour la vue avec tous les arg, sinon Myview3
#admin.add_view(ModelView(User, db.session))
