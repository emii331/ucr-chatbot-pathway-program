from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from tabulate import tabulate
import os
from dotenv import load_dotenv
import pandas as pd
from typing import List


Base = declarative_base()


class Users(Base):
    """Initializes the Users table with columns for email, first name, last name, and password"""

    __tablename__ = "Users"

    email = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)


class ParticipatesIn(Base):
    """Initializes the ParticipatesIn table with columns for student id, role, and course name"""

    __tablename__ = "ParticipatesIn"

    email = Column(String, ForeignKey("Users.email"), primary_key=True)
    course_id = Column(Integer, ForeignKey("Courses.course_id"), primary_key=True)
    role = Column(String)


class Courses(Base):
    """Initializes the Courses table with a column course name"""

    __tablename__ = "Courses"

    course_id = Column(Integer, primary_key=True)
    course_name = Column(String)


class Documents(Base):
    """Initializes the Documents table with columns for document id, file path, document type, and course id"""

    __tablename__ = "Documents"

    document_id = Column(Integer, primary_key=True)
    file_path = Column(String)
    document_type = Column(String)
    course_id = Column(Integer, ForeignKey("Courses.course_id"))


class Segments(Base):
    """Initializes the Segments table with columns for document id, file path, document type, and course id"""

    __tablename__ = "Segments"

    segment_id = Column(Integer, primary_key=True)
    text = Column(String)
    document_id = Column(Integer, ForeignKey("Documents.document_id"))


class Embeddings(Base):
    """Initializes the Embeddings table with columns for document id, file path, document type, and course id"""

    __tablename__ = "Embeddings"

    embedding_id = Column(Integer, primary_key=True)
    vector = Column(String)
    segment_id = Column(Integer, ForeignKey("Segments.segment_id"))


class Conversations(Base):
    """Initializes the Conversations table with columns for conversation id and initiator"""

    __tablename__ = "Conversations"

    conversation_id = Column(Integer, primary_key=True)
    initiator = Column(String, ForeignKey("Users.email"))


class Messages(Base):
    """Initializes the Messages table with columns for message id, body, timestamp, conversation id, and message type"""

    __tablename__ = "Messages"

    message_id = Column(Integer, primary_key=True)
    body = Column(String)
    timestamp = Column(String)
    conversation_id = Column(Integer, ForeignKey("Conversations.conversation_id"))
    type = Column(String)


"""Defines relationships between tables"""
Users.courses = relationship("ParticipatesIn", back_populates="user")
Users.conversations = relationship("Conversations", back_populates="user")
ParticipatesIn.user = relationship("Users", back_populates="courses")
ParticipatesIn.course = relationship("Courses", back_populates="users")
Courses.users = relationship("ParticipatesIn", back_populates="course")
Courses.documents = relationship("Documents", back_populates="course")
Documents.course = relationship("Courses", back_populates="documents")
Documents.segments = relationship("Segments", back_populates="document")
Segments.document = relationship("Documents", back_populates="segments")
Segments.embeddings = relationship("Embeddings", back_populates="segment")
Embeddings.segment = relationship("Segments", back_populates="embeddings")
Conversations.messages = relationship("Messages", back_populates="conversation")
Conversations.user = relationship("Users", back_populates="conversations")
Messages.conversation = relationship("Conversations", back_populates="messages")

load_dotenv()
user = os.getenv("PGUSER")
password = os.getenv("PGPASSWORD")
host = os.getenv("PGHOST")
port = os.getenv("PGPORT")
database = os.getenv("PGDATABASE")

engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


def add_new_user(
    email: str, first_name: str, last_name: str, password: str
):
    """Adds new user entry to Users table with the given parameters."""
    with Session(engine) as session:
        try:
            new_user = Users(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )

            session.add_all([new_user])
            session.commit()
            print("New user added successfully.\n")
        except IntegrityError as e:
            session.rollback()
            print("Error adding new user.\n")


def add_new_course(course_id: int, course_name: str):
    """Adds new course to the Courses table with the given parameters."""
    with Session(engine) as session:
        try:
            new_course = Courses(
                course_id=course_id,
                course_name=course_name,
            )

            session.add(new_course)
            session.commit()
            print("New course added successfully.\n")
        except IntegrityError as e:
            session.rollback()
            print("Error adding new course.\n")


def add_new_document(
    document_id: int, file_path: str, document_type: str, course_id: int
):
    """Adds new document to the Documents table with the given parameters."""
    with Session(engine) as session:
        try:
            new_document = Documents(
                document_id=document_id,
                file_path=file_path,
                document_type=document_type,
                course_id=course_id,
            )
            session.add(new_document)
            session.commit()
            print("Document added successfully.\n")
        except IntegrityError as e:
            session.rollback()
            print("Error adding document. Course id must exist.\n")

"""
def add_students_to_course(csv_path: str, course_id: int):
    Adds a list of students to the course specified by the course id parameter.
    :param csv_path: A path to a csv file containing a list of students to be added to the course, with their emails and names
    :param course_id: Course ID for the course the students should be added to
    
    student_list = pd.read_csv(csv_path)

    with Session(engine) as session:
        course = session.query(Courses).filter(Courses.course_id == course_id).first()
        if not course:
            print("Error adding student list. Course does not exist.\n")
            return
        for _, row in student_list.iterrows():
            row: pd.Series
            email = str(row["email"])
            first_name = str(row["first_name"])
            last_name = str(row["last_name"])

            user = session.query(Users).filter(Users.email == email).first()
            if not user:
                add_new_user(email, first_name, last_name, "")
                print(f"Added new user with email {email}.\n")
            else:
                print(f"User with email {email} already exists.\n")

            participation_status = (
                session.query(ParticipatesIn)
                .filter(
                    ParticipatesIn.email == email,
                    ParticipatesIn.course_id == course_id,
                    ParticipatesIn.role == "Student",
                )
                .first()
            )

            if not participation_status:
                new_participation = ParticipatesIn(
                    email=email, course_id=course_id, role="Student"
                )
                session.add(new_participation)
                print(f"{email} added to course.\n")
            else:
                print(f"{email} already in course.\n")

            session.commit()
"""

def print_table(table: type):
    with Session(engine) as session:
        all_entries: List[Users] = session.query(table).all()
        rows:List[List[str]] = []
        for row in all_entries:
            rows.append([row.email, row.first_name, row.last_name])
        print(tabulate(rows, headers="keys", tablefmt="psql"))


add_new_user("eclar022@ucr.edu", "Emily", "Clark", "mypassword")
print_table(Users)
add_new_course(10, "CS010A")
#add_students_to_course("test_student_list.csv", 10)
print_table(Users)
print_table(ParticipatesIn)
