from flask import flash, redirect, url_for, render_template, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from crr.forms import RegistrationForm, LoginForm, UpdateAccountForm, TicketForm, TicketUpdateForm, TicketAssignForm, RequestResetForm, ResetPasswordForm
from crr.models import User, Ticket
from crr import app, db, bcrypt, mail
from flask_mail import Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

@app.route("/")
@app.route("/index")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route("/home")
def home():
    if current_user.userrole == "User":
        userid = current_user.id
        tickets = Ticket.query.filter_by(user_id = userid)
        return render_template('home.html', tickets = tickets)
    if current_user.userrole == "Agent":
        userid = current_user.id
        tickets = Ticket.query.filter_by(agent_id = userid)
        return render_template('home.html', tickets = tickets)
    if current_user.userrole == "Admin":
        tickets = Ticket.query.all()
        return render_template('home.html', tickets = tickets)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, userrole = form.userrole.data , email=form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now login!','success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login was Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login' , form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file= image_file, form=form)

@app.route("/ticket/new", methods = ['GET', 'POST'])
@login_required
def new_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(title = form.title.data, status = 'Unassigned', agent_id = '404' ,content = form.content.data, author = current_user)
        db.session.add(ticket)
        db.session.commit()
        flash('Your ticket has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('new_ticket.html', title = 'New Ticket', form = form, legend ='New Ticket')

@app.route("/ticket/<int:ticket_id>")
def ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('ticket.html', title = ticket.title, ticket = ticket)

@app.route("/ticket/<int:ticket_id>/assign", methods = ['GET', 'POST'])
@login_required
def assign_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    user = User.query.get_or_404(ticket.user_id)
    if current_user.userrole != 'Admin':
        abort(403)
    status_data = [('Assigned', 'Assigned'), ('Under_review', 'Under_review'), ('Complete', 'Complete')]
    available_agent = User.query.filter_by(userrole='Agent')
    agent_list = [(i.id, i.username) for i in available_agent]
    form = TicketAssignForm()
    form.agent_id.choices = agent_list
    form.status.choices = status_data
    if form.validate_on_submit():
        ticket.title = ticket.title
        ticket.status = form.status.data
        ticket.agent_id = form.agent_id.data
        ticket.content = ticket.content
        ticket_status_email(ticket, user)
        db.session.commit()
        flash('The agent was assigned successfully!', 'success')
        return redirect(url_for('ticket', ticket_id = ticket.id ))
    elif request.method == 'GET':
        form.title.data = ticket.title
        form.content.data = ticket.content
    return render_template('update_ticket.html', title = 'Assign Agent', 
                            form = form, legend ='Assign Agent')   

def ticket_status_email(ticket, user):
    message = Mail(
    from_email='ilamvazhuthi.j@gmail.com',
    to_emails= user.email,
    subject = 'Ticket Status Update',
    html_content='<p>The status of your ticket has been updated to<br>{}<br>This is an automated messeage.<br><br><br>For any queries contact our customer support</p>'.format(ticket.status))
    try:
        sg = SendGridAPIClient("")
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

@app.route("/ticket/<int:ticket_id>/update", methods = ['GET', 'POST'])
@login_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    user = User.query.get_or_404(ticket.user_id)
    if current_user.userrole == 'User' :
        abort(403)
    status_data = [('Assigned', 'Assigned'), ('Under_review', 'Under_review'), ('Complete', 'Complete')]
    available_agent = User.query.filter_by(userrole='Agent')
    agent_list = [(i.id, i.username) for i in available_agent]
    form = TicketUpdateForm()
    form.agent_id.choices = agent_list
    form.status.choices = status_data
    if form.validate_on_submit():
        ticket.title = form.title.data
        ticket.status = form.status.data
        ticket.agent_id = ticket.agent_id
        ticket.content = form.content.data
        ticket_status_email(ticket, user)
        db.session.commit()
        flash('The ticket was updated successfully!', 'success')
        return redirect(url_for('ticket', ticket_id = ticket.id ))
    elif request.method == 'GET':
        form.title.data = ticket.title
        form.content.data = ticket.content
    return render_template('update_ticket.html', title = 'Update Agent', 
                            form = form, legend ='Update Ticket')



@app.route("/ticket/<int:ticket_id>/delete", methods = ['GET', 'POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if (current_user.userrole == 'User'):
        abort(403)
    db.session.delete(ticket)
    db.session.commit()
    flash('Your ticket has been deleted!', 'success')
    return redirect(url_for('home'))
 
def send_reset_email(user):
    token = user.get_reset_token()
    message = Mail(
    from_email='ilamvazhuthi.j@gmail.com',
    to_emails= user.email,
    subject='Password Reset Request',
    html_content=f'''To reset your password, visit the following link:
    {url_for('reset_token', token = token, _external = True)}

    If you did not make this request then simply ignore ths email and no changes will be made 
    ''')
    try:
        sg = SendGridAPIClient("")
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

@app.route('/reset_password', methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)
    
@app.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now login!','success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)

