import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = User.followed_posts(current_user)
    return render_template("home.html", user=current_user, posts=posts)


def saveImg(file, fileName):
    if request.method == 'POST':
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fileName))


# Posts routes
@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        title = request.form.get('title')
        img = request.files['img']
        fileName = str(uuid.uuid1())+"_"+secure_filename(img.filename)
        saveImg(img, fileName)

        if not text:
            flash('Please enter something before posting.', category='error')
        else:
            post = Post(text=text, title=title,
                        fileName=fileName, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.profile', username=current_user.username))

    return render_template('create_post.html', user=current_user)


@views.route("/edit-post/<id>", methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()
    if request.method == "POST":
        post.text = request.form.get('text')
        post.title = request.form.get('title')
        post.img = request.files['img']
        if post.img:
            post.fileName = str(uuid.uuid1())+"_" + \
                secure_filename(post.img.filename)
            saveImg(post.img, post.fileName)
        post = Post(text=post.text, title=post.title,
                    fileName=post.fileName, author=current_user.id)
        db.session.commit()
        flash('Post Edited!', category='success')
        return redirect(url_for('views.profile', username=current_user.username))

    return render_template('edit_post.html', post=post)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif post:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.profile', username=current_user.username))


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash('Commented Successfully!', category='success')
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))


@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment Deleted!.', category='success')

    return redirect(url_for('views.home'))


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})


# User routes
@views.route("/search", methods=['POST'])
@login_required
def search():
    searched = request.form.get('searched')
    users = User.query.filter(User.username.like(searched+'%')).all()

    return render_template("search.html", searched=searched, users=users)


@views.route("/profile/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    nop = Post.query.filter(Post.author == User.id,
                            User.username == username).count()
    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("profile.html", user=user, nop=nop, posts=posts, username=username)


@views.route("<username>/followers")
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    return render_template("followers.html", user=user, username=username)


@views.route("<username>/followed")
@login_required
def followed(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    return render_template("followed.html", user=user, username=username)


@views.route('/follow/<username>', methods=['GET', 'POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username), category='error')
        return redirect(url_for('views.home'))
    if user == current_user:
        flash('You cannot follow yourself!', category='error')
        return redirect(url_for('views.profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username), category='success')
    return redirect(url_for('views.profile', username=username))


@views.route('/unfollow/<username>', methods=['GET', 'POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username), category='error')
        return redirect(url_for('views.home'))
    if user == current_user:
        flash('You cannot unfollow yourself!', category='error')
        return redirect(url_for('views.profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username), category='success')
    return redirect(url_for('views.profile', username=username))
