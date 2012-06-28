from flask import render_template, redirect, url_for, flash, request
from config import db
from .models import Post
from .forms import PostForm

def post_index():
    object_list = Post.query.all()
    return render_template('post/index.slim', object_list=object_list)

def post_show(id):
    post = Post.query.get(id)
    return render_template('post/show.slim', post=post)

def post_new():
    form = PostForm()
    if form.validate_on_submit():
        return redirect(url_for('post.index'))
    return render_template('post/new.slim', form=form)

def post_edit(id):
    post = Post.query.get(id)
    form = PostForm(request.form, post)
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post.show', id=id))
    return render_template('post/edit.slim', form=form, post=post)
