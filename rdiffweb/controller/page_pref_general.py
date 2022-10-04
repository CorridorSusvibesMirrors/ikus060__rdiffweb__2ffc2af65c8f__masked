# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Default preference page to show general user information.
"""

import cherrypy
from wtforms.fields import HiddenField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.model import UserObject
from rdiffweb.tools.i18n import gettext_lazy as _




class UserProfileForm(CherryForm):
    action = HiddenField(default='set_profile_info')
    username = StringField(_('Username'), render_kw={'readonly': True})
    fullname = StringField(
        _('Fullname'),
        validators=[
            Optional(),
            Length(max=256, message=_('Fullname too long.')),
            Regexp(UserObject.PATTERN_FULLNAME, message=_('Must not contain any special characters.')),
        ],
    )
    email = EmailField(
        _('Email'),
        validators=[
            DataRequired(),
            Length(max=256, message=_("Email too long.")),
            Regexp(UserObject.PATTERN_EMAIL, message=_("Must be a valid email address.")),
        ],
    )
    set_profile_info = SubmitField(_('Save changes'))

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.action.data == 'set_profile_info'

    def populate_obj(self, user):
        user.fullname = self.fullname.data
        user.email = self.email.data
        user.add()








class PagePrefsGeneral(Controller):
    """
    Plugin to change user profile.
    """

    @cherrypy.expose
    def default(self, **kwargs):
        # Process the parameters.
        profile_form = UserProfileForm(obj=self.app.currentuser)
        if profile_form.is_submitted():
            if profile_form.validate():
                profile_form.populate_obj(self.app.currentuser)
                flash(_("Profile updated successfully."), level='success')
            else:
                flash(profile_form.error_message, level='error')
        params = {
            'profile_form': profile_form,
        }
        return self._compile_template("prefs_general.html", **params)
