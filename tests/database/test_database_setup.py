import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from ucr_chatbot.database.database_setup import add_new_user, Users, engine
from sqlalchemy.orm import Session

def test_add_new_user():
  add_new_user("test@email.com", "John", "Doe", "testpassword1")
  with Session(engine) as session:
    result = session.query(Users).filter_by(email = "test@email.com").first()
    assert result is not None
    assert result.email == "test@email.com"
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.password == "testpassword1"
