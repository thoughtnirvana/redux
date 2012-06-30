from flask import render_template, redirect, url_for, flash, request
from config import db
import models
import forms

def post_index():
    object_list = models.Post.query.all()
    return render_template('post/index.slim', object_list=object_list)

def post_show(id):
    post = models.Post.query.get(id)
    return render_template('post/show.slim', post=post)

def post_new():
    form = forms.PostForm()
    if form.validate_on_submit():
        post = models.Post(form.title.data,
                    form.body.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post.index'))
    return render_template('post/new.slim', form=form)

def post_edit(id):
    post = models.Post.query.get(id)
    form = forms.PostForm(request.form, post)
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post.show', id=id))
    return render_template('post/edit.slim', form=form, post=post)

def post_delete(id):
    post = models.Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('post.index', id=id))
