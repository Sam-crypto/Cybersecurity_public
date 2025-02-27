# Progetto Basi di Dati mod.2 2023
# Componenti:   Pagotto Angelo(875829), Berto Giovanni (), Zemello Samuele (882735)

# Gestione degli esami del docente.
# Funzionalità:
# 	1. Aggiunta del proprio esame
# 	2. Mostrare gli esami aggiunti
# 	3. Cancellazione di un esame
#   4. Mostrare i voti di ciascun esame sostenuto
#   5. Mostrare quanti e quali studenti partecipano all' esame del giorno


from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from flask import Flask, Blueprint, render_template, redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date

# mantiene il collegamento con l'app principale mainPage
app_teacherExam = Blueprint('app_teacherExam', __name__)

# creazione dell'engine
engine = create_engine('postgresql+pg8000://postgres:Angelo99@localhost:5432/Exams_Manager', echo=True)

# creazione della sessione
Session = sessionmaker(bind=engine)
session = Session()

Base = automap_base()
Base.prepare(engine, reflect=True)

# importa i dati delle tabelle del database
Students = Base.classes.Students
Teachers = Base.classes.Teachers
Exams = Base.classes.Exams
isEnrolled = Base.classes.IsEnrolled
Test = Base.classes.Tests
Appeals = Base.classes.ExamAppeals




@app_teacherExam.route('/newExam', methods=['GET', 'POST'])
@login_required
def newExam():
    ExamForm = request.form["exam"]
    DescriptionForm = request.form["description"]
    nTestForm = int(request.form["nTest"])
    FacultyForm = request.form["num"]
    CFUForm = int(request.form["CFU"])
    if current_user.is_authenticated:
        if request.method == 'POST':
            # controllo sul titolo del corso
            usedTitle = session.query(Exams.Id).filter(Exams.ExamName == ExamForm).first()
            if usedTitle is None:  # controlla se titleForm è usata da qualche docente
                # titleForm non è usata da nessun docente
                # aggiungo il corso al database
                newExam = Exams(ExamName=ExamForm, Description=DescriptionForm, nTest=nTestForm,
                                    Faculty=FacultyForm, CFU=CFUForm,
                                    IdTeacher=current_user.id)
                session.add(newExam)  # aggiunge il corso al database
                session.commit()  # conferma le modifiche
                return render_template('teacherArea.html', name=current_user.name, surname=current_user.surname)
            else:
                return render_template('teacherExamRegistration.html', error="titolo", title=ExamForm,
                                       Description=DescriptionForm,
                                       nTest=nTestForm, Faculty=FacultyForm, CFU=CFUForm)
        else:
            return redirect('/newExam')
    else:
        return redirect('/')



@app_teacherExam.route('/showAllTeacherExam')
@login_required
def showAllTeacherExam():
    if current_user.is_authenticated:
        # Mostra tutti i corsi del docente corrente
        if current_user.is_authenticated:
            # Mostra tutti i corsi del docente corrente, includendo il numero di test creati per ciascun esame
            AllExams = session.query(Exams.Id,
                                     Exams.ExamName,
                                     Exams.Description,
                                     Exams.nTest,
                                     Exams.Faculty,
                                     Exams.CFU,
                                     Exams.Enrollments,
                                     Exams.IdTeacher,
                                     func.count(Test.Id).label('NumTestCreati')) \
                .outerjoin(Test, Test.IdExam == Exams.Id) \
                .filter(Exams.IdTeacher == current_user.id) \
                .group_by(Exams.Id,
                          Exams.ExamName,
                          Exams.Description,
                          Exams.nTest,
                          Exams.Faculty,
                          Exams.CFU,
                          Exams.Enrollments,
                          Exams.IdTeacher)

        # numero d'iscrizioni fatte per ciascun esame
        nEnrollmentsGroup = \
            session.query(func.count(isEnrolled.Id), isEnrolled.IdExam, Exams.nTest) \
                .join(Exams) \
                .group_by(isEnrolled.IdExam, Exams.Enrollments)
        enrolledExamId = session.query(isEnrolled.IdExam).distinct(isEnrolled.IdExam)
        neverEnrolledCourses = session.query(Exams.Id, Exams.Enrollments).filter(
            Exams.Id.notin_(enrolledExamId))
        # informazioni riguardo i docenti
        teachersInfo = session.query(Teachers.Id, Teachers.Name, Teachers.Surname)
        return render_template('teacherShowMyExams.html', teachersInfo=teachersInfo,
                               myCourses=AllExams, nEnrollmentsGroup=nEnrollmentsGroup,
                               neverEnrolledCourses=neverEnrolledCourses)
    else:
        return redirect('/')



# tengo o non tengo traccia delle prenotazioni dello studente relative all' esame?
@app_teacherExam.route('/unenrollExam', methods=['GET', 'POST'])
def unenrollExam():
    if current_user.is_authenticated:
        IdExamForm = int(request.form["IdExam"])

        # rimuovo l'occorrenza che identifica che lo studente segue quel corso
        session.query(isEnrolled).filter(and_(isEnrolled.IdExam == IdExamForm)).delete()
        session.query(Appeals).filter(Appeals.IdTest == Test.Id)
        session.query(Test.Id).filter(Test.IdExam == IdExamForm)
        session.query(Test).filter(and_(Test.IdExam == IdExamForm)).delete()
        session.query(Exams).filter(and_(Exams.Id == IdExamForm)).delete()
        session.commit()

        return render_template('teacherArea.html')
    else:
        return redirect('/')

# mostra tutti i test creati per un certo esame
@app_teacherExam.route('/showTeacherTests', methods=['GET', 'POST'])
def showTeacherTests():
    if current_user.is_authenticated:
        # Mostra tutti test dell'esame del docente corrente
        IdExamForm = int(request.form["IdExam"])


        tests = session.query(Test).filter(Test.IdExam == IdExamForm).order_by(Test.TestName)

        testInfo = session.query(Exams).filter(Exams.Id == IdExamForm)
        tests = session.query(Test).filter(Test.IdExam == IdExamForm).order_by(Test.TestName)

        # Recupera tutti gli id dei test associati all'esame
        test_ids = [test.Id for test in tests]
        AllAppealData = session.query(Appeals).filter(Appeals.IdTest == test_ids)
        # Recupera le date degli appelli per ciascun test
        AllExams = session.query(Exams.Id, Exams.nTest).filter(Test.IdExam == IdExamForm)
        return render_template('teacherShowMyTests.html', myTest=tests, myAppeal=AllAppealData, test=tests, exam=testInfo,myExam=AllExams)
    else:
        return redirect('/')

@app_teacherExam.route('/registrationExam')
def registrationExam():
    return render_template('teacherExamRegistration.html')

@app_teacherExam.route('/registrationTest')
def registrationTest():
    return render_template('teacherRegistrationTest.html')

