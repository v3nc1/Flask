from flask import render_template,url_for, flash, redirect, request,abort
from blog.Forms import RegistrationForm, LoginForm, CurrencyForm, UpdateAccountForm, PostForm, ResetPasswordForm, RequestResetForm
from blog.model import User,Post
from blog import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from PIL import Image
import secrets, os


@app.route("/")
@app.route("/home")
def home():
    page=request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('index.html',posts=posts,title="Moj blog")

@app.route("/about")
def about():
    return render_template('about.html',title="About page")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_pass=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash('Accoun has been created! Procced to log in','success')

        return redirect(url_for('login'))
    return render_template('register.html',title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:

        flash('Alredy loged in!','success')
        return redirect(url_for('home',stat='Log out'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page=request.args.get('next')
            flash(user.username +' logged in succesfuly','success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Log in unsuccessful. Please check email and password','danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/exchange",methods=['GET','POST'])
def exchange():
    form=CurrencyForm()

   
   
    if form.validate_on_submit():
        val1=form.val1.data
        if form.val1.data==None:
            flash('No value','danger')
            return render_template('conversion.html',title='Exchange',value=val1, form=form)
        else:
            val2=val1*10
            flash('Didnt it','danger')

            return render_template('conversion.html',title='Exchange', value=val2, form=form)

    flash('Did it','danger')
    return render_template('conversion.html',title='Exchange', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):

    random_hex=secrets.token_hex(8) 
    _, f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex + f_ext
    picture_path=os.path.join(app.root_path,'static/profile_pics',picture_fn)
    
    output_size=(100,100)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)


    return picture_fn

@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('youre account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file=url_for('static',filename='profile_pics/'+ current_user.image_file)
    return render_template('account.html',title='Account', image_file=image_file, form=form)

@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():

    form=PostForm()

    if form.validate_on_submit():
        post=Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created','success')

        return redirect(url_for('home'))

    return render_template('create_post.html',title='New Post',legend='New Post',form=form)

@app.route("/post/<int:post_id>")
def post(post_id):
    post=Post.query.get_or_404(post_id)

    return render_template('post.html',title=post.title,post=post)

@app.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def update_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash('Post has been updated','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method=='GET':
        form.title.data=post.title
        form.content.data=post.content
    return render_template('create_post.html',title='Edit Post', legend='Edit Post',form=form)

@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'danger')
    return redirect(url_for('home'))


@app.route("/user_posts/<string:username>")
def user_posts(username):

    page=request.args.get('page',1,type=int)
    user=User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
    return render_template('user_posts.html',posts=posts,title="Moj blog", user=user)

def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Request', sender='noreply@blog.hr',recipients=[user.email])

    msg.body= f'''To reset your password, click on the link below this message:

{url_for('reset_token',token=token,_external=True)}

If you did not make this request, ignore this email.

'''
    mail.send(msg)

@app.route("/reset_password",methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Mail has been sent to you, check youre Inbox !', 'info')
        return redirect(url_for('login'))
    return render_template("reset_request.html",title="Reset Password", form=form)

@app.route("/reset_password/<token>",methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=User.verify_reset_token(token)

    if user is None:
        flash('Invalid token or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pass=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_pass
        db.session.commit()
        flash('Password has been updated! You are now able to log in','success')

        return redirect(url_for('login'))
    return render_template("reset_token.html",title="Reset Password", form=form)