CREATE DATABASE IF NOT EXISTS Exams_Manager;
USE Exams_Manager;




CREATE TABLE Teachers (
 IdTeacher SERIAL  PRIMARY KEY ,
 Email VARCHAR(30) NOT NULL UNIQUE,
 Password VARCHAR(30) NOT NULL,
 Nome VARCHAR(30) NOT NULL,
 Cognome VARCHAR(30) NOT NULL,
 Telefono VARCHAR(30) NOT NULL
);

CREATE TABLE Students (
 IdStudent SERIAL  PRIMARY KEY,
 Email VARCHAR(30) NOT NULL UNIQUE,
 Password VARCHAR(30) NOT NULL,
 Nome VARCHAR(30) NOT NULL,
 Cognome VARCHAR(30) NOT NULL,
 Telefono INT NOT NULL,
 IdExam INT NOT NULL

);

CREATE TABLE IsEnrolled(
    IdStudent INTEGER,
    IdExam INTEGER,
    PRIMARY KEY (IdStudent,IdExam),
    DataRegistrazioneVoto TIMESTAMP,--stessa cosa qui ma può essere
    status BOOLEAN,
    FOREIGN KEY (IdStudent) REFERENCES Students(IdStudent),
    FOREIGN KEY (IdExam) REFERENCES Exams(IdExam)
);

CREATE TABLE Exams (
 IdExam SERIAL PRIMARY KEY ,
 NomeExam VARCHAR(30) NOT NULL,
 Descrizione VARCHAR(100),
 nProve INT NOT NULL,
 IdTeacher INT NOT NULL,
 FOREIGN KEY (IdTeacher) REFERENCES Teachers(IdTeacher) ON DELETE CASCADE
);


CREATE TYPE modalita AS ENUM ('Esame', 'Idoneità', 'Bonus');

CREATE TABLE Tests (
    IdTest SERIAL PRIMARY KEY,
    NomeTest VARCHAR(30) NOT NULL,
    Tipologia VARCHAR(30) NOT NULL, -- può essere qualsiasi cosa? si
    TipoValutazione modalita NOT NULL,-- verificare inserimento della valutazione
    IdResponsabile INT NOT NULL,
    IdExam INT NOT NULL,
    FOREIGN KEY (IdResponsabile) REFERENCES Teachers(IdTeacher)
    --CHECK (modalita!='Esame' OR modalita!='Idoneità' OR modalita !='Bonus')-- controllo se la modalità è corretta


);


CREATE TABLE ExamAppeals(
  IdAppeal SERIAL PRIMARY KEY,
  DataEsame TIMESTAMP NOT NULL,
  IdTest INT NOT NULL,
  FOREIGN KEY (IdTest) REFERENCES Tests(IdTest) ON DELETE CASCADE
);


CREATE TABLE Sustains(
    IdStudent INTEGER,
    IdAppeal INTEGER,
    Valutazione FLOAT NOT NULL CHECK (Valutazione > 0 AND Valutazione < 32), --check sul tipo di valutazione
    Idoneo BOOLEAN DEFAULT FALSE NOT NULL, -- da togliere
    isBonus BOOLEAN DEFAULT FALSE NOT NULL, -- da togliere
    PRIMARY KEY(IdStudent,IdAppeal),
    FOREIGN KEY (IdStudent) REFERENCES Students(IdStudent) ON DELETE CASCADE,
    FOREIGN KEY (IdAppeal) REFERENCES ExamAppeals(IdAppeal) ON DELETE CASCADE

    --controllare quali campi sono necessari

);

--date per la registrazione del voto(inizio e scadenza)









/**


CREATE TABLE Corsi (
 IdCorso SERIAL  PRIMARY KEY ,
 TitoloCorso VARCHAR(60) UNIQUE,
 Descrizione TEXT,
 IdInsegnante INTEGER NOT NULL,
 LimiteStudenti INTEGER NOT NULL,
 LezioniPerDiploma INTEGER NOT NULL DEFAULT 0 CHECK (LezioniPerDiploma >= 0),
 FOREIGN KEY (IdInsegnante) REFERENCES Insegnanti(IdInsegnante) ON DELETE CASCADE
);


CREATE TABLE Iscrizione_Corsi (
 IdStudente INTEGER,
 IdCorso INTEGER ,
 PRIMARY KEY(IdStudente, IdCorso),
 FOREIGN KEY (IdStudente) REFERENCES Studenti(IdStudente) ON DELETE CASCADE,
 FOREIGN KEY (IdCorso) REFERENCES Corsi(IdCorso) ON DELETE CASCADE
);

CREATE TYPE modalita AS ENUM ('Online', 'Presenza', 'Duale');

CREATE TABLE Lezioni(
 IdLezione SERIAL PRIMARY KEY ,
 IdCorso INTEGER NOT NULL,
 Token VARCHAR(30) NOT NULL UNIQUE,
 Descrizione TEXT NOT NULL,
 Data_Ora TIMESTAMP NOT NULL,
 IdAula INTEGER, --Può Essere null se solo se ModalitàLezione = Online
 ModalitaLezione modalita NOT NULL,
 FOREIGN KEY (IdCorso) REFERENCES Corsi(IdCorso) ON DELETE CASCADE,
 FOREIGN KEY (IdAula) REFERENCES Aule(IdAula),
 CHECK((ModalitaLezione <> 'Online' OR IdAula IS NULL) AND (NOT (ModalitaLezione <> 'Online' AND IdAula IS NULL)))
);

SET timezone = 'MET';

CREATE TABLE Presenze (
 IdStudente INTEGER NOT NULL,
 IdLezione INTEGER NOT NULL,
 InPresenza BOOLEAN DEFAULT FALSE NOT NULL,
 Conferma BOOLEAN DEFAULT FALSE NOT NULL,
 FOREIGN KEY (IdStudente) REFERENCES Studenti(IdStudente) ON DELETE CASCADE,
 FOREIGN KEY (IdLezione) REFERENCES Lezioni(IdLezione) ON DELETE CASCADE
 );

CREATE TABLE Impostazioni (
 IdImpostazione SERIAL PRIMARY KEY,
 NomeRegola VARCHAR(30),
 Valore INTEGER
 );

CREATE VIEW Lezioni_ConPrenotati AS
SELECT Lezioni.*, Aule.nomeaula,Aule.capienza,Aule.nomeedificio, COUNT(inpresenza) AS studenti_prenotati
FROM Lezioni LEFT JOIN Aule ON Lezioni.idaula=Aule.idaula
LEFT JOIN Presenze ON (Lezioni.idLezione = Presenze.idLezione AND inpresenza = TRUE)

GROUP BY Lezioni.idLezione,Aule.idaula;
 --RUOLI
 CREATE ROLE Studente;
 CREATE ROLE Insegnante;
 CREATE ROLE Amministratore;
--Studente:
 GRANT USAGE SELECT ON ALL SEQUENCES IN SCHEMA public to studente;

 GRANT SELECT
 ON Presenze, Iscrizione_Corsi, Corsi, Lezioni, Studenti, Aule, Lezioni_ConPrenotati, Impostazioni
 TO Studente;

 GRANT INSERT,UPDATE, DELETE
 ON Presenze, Iscrizione_Corsi
 TO Studente;
--Insegnante:
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to insegnante;
 GRANT SELECT
 ON Presenze, Iscrizione_Corsi, Corsi, Lezioni, Aule, Insegnanti, Lezioni_ConPrenotati, Impostazioni
 TO Insegnante;

 GRANT INSERT,UPDATE, DELETE
 ON Corsi,Lezioni
 TO Insegnante;

--Admin:
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to amministratore;
 GRANT ALL PRIVILEGES
 ON ALL TABLES IN SCHEMA public
 TO Amministratore;
 --------------------------------------------------------------
CREATE USER ConStudente WITH PASSWORD 'studente';
GRANT Studente TO ConStudente;
CREATE USER ConInsegnante WITH PASSWORD 'insegnante';
GRANT Insegnante TO ConInsegnante;
CREATE USER ConAmministratore WITH PASSWORD 'amministratore';
GRANT Amministratore TO ConAmministratore;

 INSERT INTO Studenti (Email,Password,Nome,Cognome,Matricola)
 VALUES ('prova@yopmail.com','1234', 'Mario', 'Rossi', 898744);

INSERT INTO Insegnanti (Email,Password,Nome,Cognome,Telefono, IsAdmin)
 VALUES ('prova2@cao.com','1234', 'Marco ', 'Bonaldo', '725',False);

INSERT INTO Insegnanti (Email,Password,Nome,Cognome,Telefono, IsAdmin)
 VALUES ('prova3@cao.com','1234', 'Simona', 'Rossi', '181',True);

 INSERT INTO Studenti (Email,Password,Nome,Cognome,Matricola)
 VALUES ('prova4@cao.com','1234', 'Luigi', 'Beppino', 848788);

INSERT INTO Aule (nomeaula,capienza,nomeedificio)
 VALUES ('Aula 1',1,'Edificio 1');
INSERT INTO Aule (nomeaula,capienza,nomeedificio)
 VALUES ('Aula 2',2,'Edificio 1');

 INSERT INTO Impostazioni (nomeregola,valore)
 VALUES ('MaxCorsiPerStudenti',1);

 INSERT INTO Impostazioni (nomeregola,valore)
 VALUES ('DurataLezione',90);


CREATE INDEX IndiceCorsi ON Corsi (IdCorso);
CREATE INDEX IndiceLezioni ON Lezioni (IdLezione);
CREATE INDEX IndiceInsegnanti ON Insegnanti (IdInsegnante);
CREATE INDEX IndiceStudenti ON Studenti (IdStudente);

-- Trigger per verificare che uno studente non si possa registrare ad una lezione di un corso a cui non è iscritto
CREATE FUNCTION noRegistrazioneSenzaIscrizioneCorso() RETURNS trigger AS $$
    DECLARE idcorsoDelCorso INTEGER;
    BEGIN
        idcorsoDelCorso:=(SELECT idCorso FROM Lezioni WHERE idLezione = New.idLezione);
        IF(NOT EXISTS(SELECT * FROM iscrizione_corsi WHERE idStudente = New.idStudente AND idCorso= idcorso )) THEN
            RAISE data_exception USING MESSAGE = 'Impossibile registrare la presenza ad un corso a cui non si è iscritti';
            RETURN NULL;
        END IF;
        RETURN New;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER noRegistrazioneSenzaIscrizioneCorso
BEFORE INSERT ON Presenze
FOR EACH ROW
EXECUTE FUNCTION noRegistrazioneSenzaIscrizioneCorso();

-- Trigger per verificare che non sia usata la stessa email su studenti e insegnanti
CREATE FUNCTION noEmailUgualeInsegnanti() RETURNS trigger AS $$
    BEGIN
        IF(EXISTS(SELECT * FROM Studenti WHERE email = New.email)) THEN
            RAISE data_exception USING MESSAGE = 'Email già registrata';
            RETURN NULL;
        END IF;
        RETURN New;
    END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER noEmailUgualeInsegnanti
BEFORE INSERT OR UPDATE ON Insegnanti
FOR EACH ROW
EXECUTE FUNCTION noEmailUgualeInsegnanti();

CREATE FUNCTION noEmailUgualeStudenti() RETURNS trigger AS $$
    BEGIN
        IF(EXISTS(SELECT * FROM Insegnanti WHERE email = New.email)) THEN
            RAISE data_exception USING MESSAGE = 'Email già registrata';
            RETURN NULL;
        END IF;
        RETURN New;
    END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER noEmailUgualeStudenti
BEFORE INSERT OR UPDATE ON Studenti
FOR EACH ROW
EXECUTE FUNCTION noEmailUgualeStudenti();

-- Trigger per verificare che non ci siano studenti in presenza oltre al limite di capienza dell'aula
-- e che non ci si possa prenotare quando la lezione è online
CREATE FUNCTION limitePrenotazioniPosti() RETURNS trigger AS $$
    DECLARE capienzaAula INTEGER;
    BEGIN
        IF(New.inPresenza = FALSE) THEN
            RETURN New;
        END IF;

        IF(EXISTS(SELECT * FROM Lezioni WHERE idLezione = New.idLezione AND modalitaLezione ='Online')) THEN
            RAISE data_exception USING MESSAGE = 'Prenotazione non consentita, perchè la lezione è online';
            RETURN NULL;
        END IF;

        capienzaAula:= (SELECT capienza FROM Lezioni JOIN Aule ON Lezioni.idAula=Aule.idAula WHERE IdLezione = New.idLezione);
        IF(capienzaAula <=(SELECT COUNT(*) FROM Presenze WHERE idLezione=New.idLezione AND inPresenza= TRUE AND idStudente <> New.idStudente)) THEN
            RAISE data_exception USING MESSAGE = 'Impossibile prenotare, posti esauriti';
            RETURN NULL;
        END IF;
        RETURN New;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER limitePrenotazioniPosti
BEFORE INSERT OR UPDATE ON Presenze
FOR EACH ROW
EXECUTE FUNCTION limitePrenotazioniPosti();

-- Trigger per gestire la sovrapposizione di lezioni sulla stessa aula:
CREATE FUNCTION auleGiaOccupata() RETURNS trigger AS $$
    DECLARE durataLezione INTEGER;
    BEGIN
        durataLezione:= (SELECT Valore FROM Impostazioni Where nomeregola='DurataLezione');
        IF(EXISTS(SELECT * FROM Lezioni WHERE (New.ModalitaLezione <> 'Online') AND idAula IS NOT NULL AND idAula = New.idAula AND DATE(data_ora) = DATE(New.data_ora) AND
                                ((New.data_ora::time >=data_ora::time AND New.data_ora::time -data_ora::time < durataLezione* interval '1 minutes') OR(New.data_ora::time <data_ora::time AND data_ora::time -New.data_ora::time < durataLezione* interval '1 minutes') )  )) THEN
            RAISE data_exception USING MESSAGE = 'Aula già occupata per la data-ora inserita';
            RETURN NULL;
        END IF;
        RETURN New;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auleGiaOccupata
BEFORE INSERT ON Lezioni
FOR EACH ROW
EXECUTE FUNCTION auleGiaOccupata();

-- Trigger per gestire il numero di corsi a cui uno studente si può iscrivere
CREATE FUNCTION maxCorsiIscrivibili() RETURNS trigger AS $$
    DECLARE limite INTEGER;
    BEGIN
        limite:= (SELECT Valore FROM Impostazioni Where nomeregola='MaxCorsiPerStudenti');
        IF(limite <= (SELECT COUNT(*) FROM iscrizione_corsi WHERE idStudente= New.idStudente)) THEN
            RAISE data_exception USING MESSAGE = ('Limite corsi iscrivibili raggiunto, il limite é di ' || limite);
            RETURN NULL;
        END IF;
        RETURN New;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER maxCorsiIscrivibili
BEFORE INSERT ON iscrizione_corsi
FOR EACH ROW
EXECUTE FUNCTION maxCorsiIscrivibili();

-- Trigger per gestire gli iscritti totali su un determinato corso
CREATE FUNCTION maxIscrittiPerCorso() RETURNS trigger AS $$
    BEGIN
        IF( EXISTS( SELECT COUNT(*) AS iscritti FROM iscrizione_corsi WHERE idCorso = New.idCorso HAVING COUNT(*) = (SELECT LimiteStudenti FROM Corsi WHERE idCorso = New.idCorso) )) THEN
            RAISE data_exception USING MESSAGE = 'Limite numero iscritti raggiunto nel corso';
            RETURN NULL;
        END IF;
        RETURN New;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER maxIscrittiPerCorso
BEFORE INSERT ON iscrizione_corsi
FOR EACH ROW
EXECUTE FUNCTION maxIscrittiPerCorso();

--Trigger per gestore il cambio limite di studenti iscritti in un corso
CREATE FUNCTION cambioLimiteIscritti() RETURNS trigger AS $$
    BEGIN
        IF( New.LimiteStudenti < ( SELECT COUNT(*) FROM Iscrizione_corsi WHERE idCorso = New.idCorso)) THEN
            RAISE data_exception USING MESSAGE = 'Limite Studenti non valido';
            RETURN NULL;
        END IF;
        RETURN New;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cambioLimiteIscritti
BEFORE UPDATE OF LimiteStudenti ON Corsi
FOR EACH ROW
EXECUTE FUNCTION cambioLimiteIscritti();
 */