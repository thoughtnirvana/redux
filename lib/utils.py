# vim: set fileencoding=utf-8 :
"""
Misc. utilities.
"""
import re, os

from flask import render_template

def set_trace():
    """
    Wrapper for ``pdb.set_trace``.
    """
    from config import app
    if not app.debug: return
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        import pdb
        pdb.set_trace()


def auto_version(endpoint, **values):
    """
    Auto versions static assets.
    """
    from flask import current_app as app
    from flask import url_for
    # Check if accessing static file.
    static_root = None
    if endpoint == 'static':
        static_root = app.static_folder
    if not static_root:
        m = re.match(r'(.+)\.static', endpoint)
        if m:
            try:
                static_root = app.blueprints[m.group(1)].static_folder
            except:
                pass
    # Get the timestamp of the file.
    if static_root:
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(static_root, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

def simple_form(form_type, template, success):
    def fn():
        form = form_type()
        if form.validate_on_submit():
            return success()
        return render_template(template, form=form)
    return fn
