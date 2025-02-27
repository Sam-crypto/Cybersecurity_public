from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('postgresql+pg8000://postgres:Angelo99@localhost:5432/Exams_Manager', echo=True)

Base = declarative_base()


class Teachers(Base):
    __tablename__ = 'Teachers'

    # dichiarazione dei campi della tabella

    Id = Column(Integer, primary_key=True)
    Email = Column(String(30), nullable=False, unique=True)
    Pwd = Column(String, nullable=False)
    Name = Column(String(30), nullable=False)
    Surname = Column(String(30), nullable=False)
    Telephone = Column(String(30), nullable=False)
    Faculty = Column(String(30), nullable=False)

    # relazione con esami 1 a n
    Exams = relationship('Exams', back_populates="Teacher")
    # relazione con prove 1 a 1
    Test = relationship('Tests', uselist=False, back_populates="Responsabile")


class Sustains(Base):
    __tablename__ = 'Sustains'

    # dichiarazione dei campi della tabella
    Id = Column(Integer, primary_key=True)
    IdStudent = Column(Integer, ForeignKey('Students.Id'))
    IdAppeal = Column(Integer, ForeignKey('ExamAppeals.Id'))
    Valutation = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint('IdStudent', 'IdAppeal', name="student_sustain_uc"),)

    # relazione con studenti n a m
    Student = relationship('Students', back_populates="Tests")
    # relazione con appelli n a m
    Appeal = relationship('ExamAppeals', back_populates="Sustains")


class IsEnrolled(Base):
    __tablename__ = 'IsEnrolled'

    # dichiarazione dei campi della tabella
    Id = Column(Integer, primary_key=True)
    IdStudent = Column(Integer, ForeignKey('Students.Id'))
    IdExam = Column(Integer, ForeignKey('Exams.Id'))
    Valutation = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint('IdStudent', 'IdExam', name="student_uc"),)

    # relazione con esami n a m
    Exam = relationship('Exams', back_populates="Students")
    # relazione con studenti n a m
    Student = relationship('Students', back_populates="Exams")


class Students(Base):
    __tablename__ = 'Students'

    # dichiarazione dei campi della tabella

    Id = Column(Integer, primary_key=True)
    Email = Column(String, nullable=False)
    Matricola = Column(String(6), nullable=False, unique=True)
    Pwd = Column(String, nullable=False)
    Name = Column(String(30), nullable=False)
    Surname = Column(String(30), nullable=False)
    Telephone = Column(Integer, nullable=False)
    Faculty = Column(String(30), nullable=False)

    # relazione con prove n a m
    Tests = relationship('Tests', secondary=Sustains)
    # relazione con esami n a m
    Exams = relationship('Exams', secondary=IsEnrolled)


class Exams(Base):
    __tablename__ = 'Exams'

    # dichiarazione dei campi della tabella

    Id = Column(Integer, primary_key=True)
    ExamName = Column(String(30), nullable=False)
    Description = Column(String(100), nullable=False)
    nTest = Column(Integer, nullable=False)
    IdTeacher = Column(Integer, ForeignKey('Teachers.Id'))
    Faculty = Column(String(30), nullable=False)
    CFU = Column(Integer, nullable=False)
    Enrollments = Column(Integer, nullable=True)

    Teacher = relationship('Teachers', back_populates="Exams")
    Tests = relationship('Tests', back_populates="Exam")
    Students = relationship('Students', secondary=IsEnrolled)


class Tests(Base):
    __tablename__ = 'Tests'

    # dichiarazione dei campi della tabella

    Id = Column(Integer, primary_key=True)
    TestName = Column(String(30), nullable=False)
    Tipology = Column(String(30), nullable=False)
    ValType = Column(Enum('Esame', 'Idoneità', 'Bonus', name='modalità'), nullable=False)

    IdResponsabile = Column(Integer, ForeignKey('Teachers.Id'))
    IdExam = Column(Integer, ForeignKey('Exams.Id'))

    # relazione con docenti 1 a 1
    Responsabile = relationship('Teachers', back_populates="Test")
    # relazione con esami 1 a n
    Exam = relationship('Exams', back_populates="Tests")
    # relazione con studenti n a m
    Students = relationship('Students', secondary=Sustains)


class ExamAppeals(Base):
    __tablename__ = 'ExamAppeals'

    # dichiarazione dei campi della tabella

    Id = Column(Integer, primary_key=True)
    ExamData = Column(String, nullable=False)
    ValutationExpireData = Column(String, nullable=False)

    IdTest = Column(Integer, ForeignKey('Tests.Id'))
    # relazione con test 1 a n
    Test = relationship('Tests', back_populates="Appeals")


Base.metadata.create_all(engine)
