from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, AccountUpdateForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


"""posts = [
    {
        'author': 'Yahia',
        'title': 'DevOps',
        'content': 'Love DevOps',
        'date_posted': '20-04-2023'
    },
    {
        'author': 'Lamhafad',
        'title': 'AWS Cloud',
        'content': 'AWS certification',
        'date_posted': '20-04-2023'
    }
]
"""

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts, title='Home')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    # Since the user is logged in, if he tries to access the register route he's automatically redirected to the home page cuz he doesn't have to login or egister for a second time when his session is active.
    # True if the user is authenticated and Flase if not
    # the 'is_authenticated' property is provided by 'UserMixin' that we inherate from when creating our 'User' class
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # Add the user to the database currently
        db.session.add(user)
        # Save all the changes to our database
        db.session.commit()
        # flash messages to show for users after registration, 'success' represents the category(green color for success operations)
        flash('Account created seccussfully. Login now', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
# same way to solve the same problem for the register routes
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # Just after validating the form, we need to check if the credentials entered by the user exist in the database. As a reminder when someone register his password is hashed and stored in the database but not the actual password itself.
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # the 'if user' condition return none if we cant find the credentials submited in the form
            # the second condition check if the password submited in the form and the hashed version in the database are the same thanks to bcrypt class
            #the line below serves as a way to log in the user after checking the credentiels
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    # By clicking on logout in the navbar the user will be logged out then redirected to the home page and the register, login icons in the navbar shows up another time since there is no session authenticated
    logout_user()
    return redirect(url_for('home'))


@app.route("/account",methods=["GET", "POST"])
@login_required
# This decorator '@login_required' is used to deny access to  the account route if there is no user logged in
# In this case the user is redirected to an error page when a message is on the screen
# To make things more clear for the user (It make no sense to redirect to that page with that message ) we will use method to redirect the user to the home page (it's more asthetic for our webpage)
# This method is just a line of code we add in the __init__ .py file : login_manager.login_view = 'login' ::note that 'login' is the function name of the route
# I asked a question about : Why that line is not added here ? Simply because login_manager extension is imported in the __init__.py file :-)
# Additional feature: a message is shown after being redirected to the login page : 'Please login to access this page'. The message appears in the black color so to make it more clear we add a line of code in the __init__.py file saying : login_manager.login_message_category = 'info'
def account():
    # load the profile pic into image_file variable
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    form = AccountUpdateForm()
    if form.validate_on_submit():
        # Update 
        current_user.username = form.username.data
        current_user.email = form.email.data
        # Save updates
        db.session.commit()
        flash('Your account has been updated successfully','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        # This condition is executed when the user refresh the profile page. Once this page is refreshed the user's credentiels appears in the form 
        # Try to comment this block to see the difference
        # Another reason is to avoid every time message "sent another submission"
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', image_file = image_file,form = form)

# Create the new post route 
# Users have to be logged in to share their posts so we need to use the decorator 'Login_required'

@app.route('/post/new', methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, author = current_user) 
        db.session.add(post)
        db.session.commit()
        flash('Great! Your post has been created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title = "New Post", form = form, legend = 'Create a new post')


# Define a route to view full content of posts
# the route structure should be /post/post_id
# Since Post_id is defined as an integer then we can specify the type by changing 'int:<post_id>' in the next line  
@app.route('/post/<post_id>')
def post(post_id):
    # In this line we're importing post content from our Post DB
    # post = Post.query.get(post_id)
    # The "get_or_404" method can do the same function as "get" but if we can't find the passed id value in DB we return 404 page
    # without using 'get_or_404' method we are directed to flask error page
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)




# Update posts
# 'Login_required' decorator is required to update posts
@app.route('/post/<post_id>/update', methods=["GET", "POST"])
@login_required
def updatepost(post_id):
    # Maybe users try to update an inexistent post, to avoid that we use 'get_or_404'
    post = Post.query.get_or_404(post_id)
    # this is the form that will be filled to modify the post
    # Users can only modify their posts but no one posts, so we must check if the user who is trying to update the post is the same as the author of this post
    if current_user != post.author : 
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated!",'success')
        # As a reminder url_for point to the function 'post' and the post_id = post.id means that for the post function the argument is the value contained in post.id
        # url_for takes functions as an argument but not templates
        # You have to read the documentation about 'redirect'
        return redirect(url_for('post', post_id = post.id))
    # Fill the form with existent data
    elif request.method == 'GET':
        form.title.data = post.title 
        form.content.data = post.content 
    return render_template('create_post.html', form = form , legend = 'Update post' )



@app.route('/post/<post_id>/delete', methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author : 
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post was deleted successfully",'info')
    return redirect(url_for('home'))