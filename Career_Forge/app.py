from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
#from read import *
import os




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'CareerForge'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.app_context().push()



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

import csv



@app.route('/people')
def ranking():
    # Read data from the CSV file
    csv_file_path = "ranked_students.csv"
    ranked_students = []
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            ranked_students.append(row)
    
    # Render HTML template with ranked students data
    return render_template('ranking.html', ranked_students=ranked_students)




@app.route('/', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
    return render_template("signin.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signin'))

    return render_template("signup.html", form=form)
@app.route('/home')
@login_required
def home():
    return render_template('index.html')
# def people():
#     # Extract students from the Excel file
#     students = extract_students_from_excel('algosheetex1.xlsx')

#     if not students:
#         return "No student data found."
#     else:
#         # Define criteria weights
#         criteria_weights = {
#             'academic_grades': 0.4,
#             'advanced_courses': 0.15,
#             'research_publication': 0.15,
#             'awards_scholarship': 0.1,
#             'coding_competition': 0.1,
#             'contribution_projects': 0.05,
#             'internships': 0.05
#         }

#         # Build the decision tree
#         decision_tree = build_decision_tree(criteria_weights.keys(), criteria_weights)

#         # Rank the students
#         ranked_students = rank_students(students, decision_tree)

#         return render_template('people.html', ranked_students=ranked_students)



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('signin'))
 
if __name__ == "__main__":
    app.run(debug=True)