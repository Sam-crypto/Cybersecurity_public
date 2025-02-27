# Progetto Basi di Dati mod.2 2023
# Componenti:   Pagotto Angelo(875829), Zemello Samuele (882735) e Berto Giovanni ()

# E' la pagina principale dove è presente l'applicazione flask.
# Questa pagina si occupa di:
# 	1. Mantenere la connessione con le altre pagine tramite la parte di blueprint di flask
# 	2. Gestire il login e la registrazione.

import bcrypt
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from flask import Flask, Blueprint, render_template, redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

from teacherExam import app_teacherExam
from teacherTest import app_teacherTest
from teacherValutation import app_teacherValutation

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

# creazione dell'engine
engine = create_engine('postgresql+pg8000://postgres:Angelo99@localhost:5432/Exams_Manager', echo=True)

# cripta password
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'ubersecret'

app.register_blueprint(app_teacherExam)
app.register_blueprint(app_teacherTest)
app.register_blueprint(app_teacherValutation)

# creazione della sessione
Session = sessionmaker(bind=engine)
session = Session()

Base = automap_base()
Base.prepare(engine, reflect=True)
# importa i dati della tabella del database
Students = Base.classes.Students
Teachers = Base.classes.Teachers


# definisce la struttura degli utenti del sistema
class User(UserMixin):
    # costruttore di classe
    def __init__(self, id, name, surname, email, pwd, active=True):
        self.id = id
        self.name = name
        self.surname = surname
        self.email = email
        self.pwd = pwd


# load_user ha il compito di trasformare un’identità in un’istanza della classe User
@login_manager.user_loader
def load_user(user_id):
    rs = session.query(Students).filter(Students.Email == (user_id))
    user = rs.first()
    if user is None:
        rs = session.query(Teachers).filter(Teachers.Email == (user_id))
        user = rs.first()
    return User(user.Id, user.Name, user.Surname, user.Email, user.Pwd)


# ritorna alla home principale
@app.route('/')
def index():
    return render_template('home.html')


# carica l'area privata degli studenti
@app.route('/studentArea')
@login_required
def studentArea():
    if current_user.is_authenticated:
        return render_template('studentArea.html', name=current_user.name, surname=current_user.surname)
    else:
        return redirect('/')


# carica l'area privata dei docenti
@app.route('/teacherArea')
@login_required
def teacherArea():
    if current_user.is_authenticated:
        return render_template('teacherArea.html', name=current_user.name, surname=current_user.surname)
    else:
        return redirect('/')


# salva nella sessione l'identità dell'utente tramite la funzione login_user() di flask-login
@app.route('/loginUser', methods=['GET', 'POST'])
def loginUser():
    # ottiene i dati dai form della pagina login.html
    emailForm = request.form["email"]
    pwdForm = request.form["pwd"]

    if request.method == 'POST':
        userPwd = session.query(Students.Pwd).filter(
            Students.Email == emailForm).first()  # ottiene un la password di un utente che ha l'email uguale a quella passata
        if userPwd is not None:  # verifica se esiste uno studente registrato con emailForm
            # lo studente è registrato
            # tramite la funzione di bycrypt (check_password_hash) verifichiamo se la password inserita è uguale a quella nel database
            # (la password passata viene cryptata tramite un hash è poi viene confrontata con la password del database)
            if bcrypt.check_password_hash(userPwd.Pwd, pwdForm):  # verifica se la password è corretta
                student = get_student_by_email(emailForm)
                login_user(student)
                return redirect('/studentArea')
            else:
                return render_template('login.html', error="invalidPwd", email=emailForm)
        else:
            userPwd = session.query(Teachers.Pwd).filter(Teachers.Email == emailForm).first()
            if userPwd is not None:  # verifica se esiste un docente registrato con emailForm
                # il docente è registrato
                # tramite la funzione di bycrypt (check_password_hash) verifichiamo se la password inserita è uguale a quella nel database
                # (la password passata viene cryptata tramite un hash è poi viene confrontata con la password del database)
                if bcrypt.check_password_hash(userPwd.Pwd, pwdForm):  # verifica se la password è corretta
                    teacher = get_teacher_by_email(emailForm)
                    login_user(teacher)
                    return redirect('/teacherArea')
                else:
                    return render_template('login.html', error="invalidPwd", email=emailForm)
            else:
                return render_template('login.html', error="notRegisteredUser", email=emailForm)
    else:
        return redirect('/')


# ricava le informazioni dello studente dalla email univoca
def get_student_by_email(email):
    user = session.query(Students).filter(Students.Email == email).first()
    return User(user.Email, user.Name, user.Surname, user.Email, user.Pwd)


# ricava le informazioni del docente dalla email univoca
def get_teacher_by_email(email):
    user = session.query(Teachers).filter(Teachers.Email == email).first()
    return User(user.Email, user.Name, user.Surname, user.Email, user.Pwd)


# rimuove dalla sessione l'identità dell'utente tramite la funzione logout_user() di flask-login
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# Crea un nuovo studente e lo aggiunge al database ottenendo le informazioni dalla pagina studentRegistration.html.
# La email dello studente deve essere univoca, se esiste già uno studente registrato con quella email lo studente non viene creato.
@app.route('/registration/newStudent', methods=['GET', 'POST'])
def newStudent():
    nameForm = request.form["name"]
    surnameForm = request.form["surname"]
    emailForm = request.form["email"]
    telephoneForm = request.form["telephone"]
    facultyForm = request.form["faculty"]
    matricolaForm = request.form["matricola"]
    pwdForm = request.form["pwd"]
    checkPwdForm = request.form["pwd2"]

    if request.method == 'POST':
        existStudent = session.query(Students.Id).filter(Students.Email == emailForm).first()  # ottiene un l'id di un utente che ha l'email uguale a quella passata
        if existStudent is None:  # verifica se non esiste alcuno studente registrato con la email emailForm
            if facultyForm == 'Informatica' or facultyForm == 'Scienze ambientali' or facultyForm == 'Umanistica':  # controllo se la facoltà inserita è corretta

                if pwdForm == checkPwdForm:  # controllo se la password e la conferma sono uguali
                    # Crea lo studente
                    newStudent = Students(Name=nameForm, Matricola=matricolaForm, Surname=surnameForm, Email=emailForm, Telephone=telephoneForm, Faculty=facultyForm,
                                          Pwd=bcrypt.generate_password_hash(pwdForm).decode('utf-8'))  # generate_password_hash(pwdForm): genera un hash della password utilizzando bcrypt
                    session.add(newStudent)  # aggiunge lo studente al database
                    session.commit()  # conferma le modifiche
                    return redirect('/')
                else:
                    return render_template('studentRegistration.html', error="pwd", name=nameForm, surname=surnameForm,
                                           telephone=telephoneForm, email=emailForm, pwd1=pwdForm)
            else:
                return render_template('studentRegistration.html',error="faculty",name=nameForm, surname=surnameForm,
                                           telephone=telephoneForm, email=emailForm, pwd1=pwdForm)
        else:
            return render_template('studentRegistration.html', error="email", name=nameForm, surname=surnameForm,
                                   telephone=telephoneForm, email=emailForm, pwd1=pwdForm,
                                   pwd2=checkPwdForm)
    else:
        return redirect('/registration/newStudent')



# Crea un nuovo docente e lo aggiunge al database ottenendo le informazioni dalla pagina teacherRegistration.html.
# La email del docente e la matricola non devono essere mai stati utilizzata prima per registrarsi.
# I primi 6 caratteri della email devono corrispondere alla matricola.
@app.route('/registration/newTeacher', methods=['GET', 'POST'])
def newTeacher():
    nameForm = request.form["name"]
    surnameForm = request.form["surname"]
    emailForm = request.form["email"]
    telephoneForm = request.form["telephone"]
    facultyForm = request.form["faculty"]
    pwdForm = request.form["pwd"]
    checkPwdForm = request.form["pwd2"]

    if request.method == 'POST':
            usedEmail = session.query(Teachers.Id).filter(Teachers.Email == emailForm).first()
            if usedEmail is None:  # controlla se emailForm è usata da qualche docente
                    #existTeacher = session.query(Teachers.Id).filter(Teachers.Email == emailForm).first()  # ottiene un l'id di un docente che ha l'email uguale a quella passata
                    #if existTeacher is None:  # verifica se non esiste nessun docente con la mail usata per registrarsi
                    if facultyForm=='Informatica' or facultyForm=='Scienze ambientali' or facultyForm=='Umanistica': #controllo se la facoltà inserita è corretta
                        if pwdForm == checkPwdForm: # controllo se la password e la conferma sono uguali
                            # Crea il docente
                            newTeacher = Teachers(Name=nameForm, Surname=surnameForm, Email=emailForm, Faculty=facultyForm,
                                                  Telephone=telephoneForm,
                                                  Pwd=bcrypt.generate_password_hash(pwdForm).decode('utf-8'))  # generate_password_hash(pwdForm): genera un hash della password utilizzando bcrypt
                            session.add(newTeacher) # aggiunge il docente al database
                            session.commit() # conferma le modifiche
                            return redirect('/')
                        else:
                            return render_template('teacherRegistration.html', error="pwd", name=nameForm, surname=surnameForm, faculty=facultyForm,
                                                   telephone=telephoneForm, email=emailForm, pwd1=pwdForm)
                    else:
                        return render_template('teacherRegistration.html', error="faculty", name=nameForm, surname=surnameForm,telephone=telephoneForm, faculty=facultyForm, email=emailForm, pwd1=pwdForm, pwd2=checkPwdForm)
            else:
                return render_template('teacherRegistration.html', error="email", name=nameForm, surname=surnameForm,
                                       telephone=telephoneForm, faculty=facultyForm ,email=emailForm, pwd1=pwdForm, pwd2=checkPwdForm)

    else:
        return redirect('/registration/newTeacher')

#mostro le info del docente attualmente loggato
@app.route('/showTeacherInfo',methods=['GET', 'POST'])
def showTeacherInfo():
    if current_user.is_authenticated:
        teachers = session.query(Teachers).filter(Teachers.Id == current_user.id).first()
        teacherInfo = session.query(Teachers.Name, Teachers.Surname, Teachers.Telephone, Teachers.Email).filter(and_(Teachers.Id == current_user.id)).first()
        return render_template('teacherInfoAcc.html', teacher=teachers, teacherInfo=teacherInfo)
    else:
        redirect('/')

#aggiorno le info del docente quando vuole aggiornare i suoi dati
@app.route('/updateTeacherInfo',methods=['GET', 'POST'])
def updateTeacherInfo():
    nameForm = request.form["name"]
    surnameForm = request.form["surname"]
    emailForm = request.form["email"]
    telephoneForm = request.form["telephone"]
    if current_user.is_authenticated:
        session.query(Teachers).filter(and_(Teachers.Id == current_user.id)).update(
            {Teachers.Name: nameForm, Teachers.Surname: surnameForm, Teachers.Telephone: telephoneForm, Teachers.Email: emailForm})
        session.commit()
        return render_template('teacherArea.html', name=nameForm, surname=surnameForm)
    else:
        redirect('/')

@app.route('/registrationStudent')
def registrationStudent():
    return render_template('studentRegistration.html')


@app.route('/registrationTeacher')
def registrationTeacher():
    return render_template('teacherRegistration.html')


@app.route('/login')
def login():
    return render_template('login.html')