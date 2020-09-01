from datetime import date, datetime
from wtforms import DateField
from app import login, app
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_manager
from flask_login.utils import login_url as make_login_url
from functools import wraps


class NullableDateField(DateField):
    """A DateField that won't result in an error if blank"""

    def process_formdata(self, valuelist):
        """Processes data in field

        Args:
            valuelist: value in form field

        Returns:
            Processed data
        """
        if valuelist:
            date_str = ' '.join(valuelist).strip()
            if date_str == '':
                self.data = None
                return
            try:
                self.data = datetime.strptime(date_str, self.format).date()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date value'))


def login_required(role=[0, 1, 2, 3]):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login.unauthorized()
            if current_user.category not in role:
                return role_unauthorized()
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


@login.unauthorized_handler
def unauthorized():
    redirect_url = make_login_url(login.login_view, next_url=request.url)
    return redirect(redirect_url)


def role_unauthorized():
    abort(401)


@app.errorhandler(401)
def unauthorized_page(error):
    return render_template('unauthorized.html'), 401
