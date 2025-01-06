import pytest


def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1


def test_is_instance():
    assert isinstance("this is a string", str)
    assert not isinstance(10, str)


def test_boolean():
    validated = True
    assert validated is True
    assert ("Hello" == "World") is False


def test_type():
    assert type("Hello") is str
    assert type("Word") is not int


def test_greater_less_than():
    assert 7 > 3
    assert not (4 > 10)


@pytest.fixture
def default_student():
    return Student("John", "Doe", "Biology", 4)


class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


def test_person_initialization(default_student):
    assert default_student.first_name == "John", "First name should be John"
    assert default_student.last_name == "Doe", "Lat name should be Doe"
    assert default_student.major == "Biology"
    assert default_student.years == 4
