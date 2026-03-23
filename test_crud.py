import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import crud
import schemas
from database import Base


@pytest.fixture
def db_session(tmp_path):
    db_file = tmp_path / "test_crud.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_employee_persists_record(db_session):
    employee = schemas.EmployeeCreate(
        full_name="John Doe",
        job_title="Software Engineer",
        country="India",
        salary=50000.0,
    )

    created_employee = crud.create_employee(db_session, employee)

    assert created_employee.id is not None
    assert created_employee.full_name == "John Doe"

    fetched_employee = crud.get_employee(db_session, created_employee.id)
    assert fetched_employee is not None
    assert fetched_employee.job_title == "Software Engineer"


def test_update_employee_changes_existing_record(db_session):
    created_employee = crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="John Doe",
            job_title="Software Engineer",
            country="India",
            salary=50000.0,
        ),
    )

    updated_employee = crud.update_employee(
        db_session,
        created_employee.id,
        schemas.EmployeeUpdate(
            full_name="Jane Doe",
            job_title="Senior Engineer",
            country="USA",
            salary=65000.0,
        ),
    )

    assert updated_employee is not None
    assert updated_employee.full_name == "Jane Doe"
    assert updated_employee.country == "USA"
    assert updated_employee.salary == 65000.0


def test_calculate_salary_applies_country_deduction(db_session):
    created_employee = crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="Asha Patel",
            job_title="Analyst",
            country="India",
            salary=80000.0,
        ),
    )

    salary_details = crud.calculate_salary(db_session, created_employee.id)

    assert salary_details == {
        "employee_id": created_employee.id,
        "full_name": "Asha Patel",
        "country": "India",
        "gross_salary": 80000.0,
        "deduction": 8000.0,
        "net_salary": 72000.0,
    }


def test_get_employees_returns_all_records(db_session):
    crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="John Doe",
            job_title="Software Engineer",
            country="India",
            salary=50000.0,
        ),
    )
    crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="Jane Smith",
            job_title="Analyst",
            country="USA",
            salary=70000.0,
        ),
    )

    employees = crud.get_employees(db_session)

    assert len(employees) == 2
    assert {employee.full_name for employee in employees} == {"John Doe", "Jane Smith"}


def test_update_employee_returns_none_for_missing_record(db_session):
    updated_employee = crud.update_employee(
        db_session,
        999,
        schemas.EmployeeUpdate(
            full_name="Ghost Employee",
            job_title="Unknown",
            country="India",
            salary=1000.0,
        ),
    )

    assert updated_employee is None


def test_delete_employee_removes_existing_record(db_session):
    created_employee = crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="Delete Me",
            job_title="Tester",
            country="India",
            salary=45000.0,
        ),
    )

    deleted_employee = crud.delete_employee(db_session, created_employee.id)

    assert deleted_employee is not None
    assert deleted_employee.id == created_employee.id
    assert crud.get_employee(db_session, created_employee.id) is None


def test_delete_employee_returns_none_for_missing_record(db_session):
    deleted_employee = crud.delete_employee(db_session, 999)

    assert deleted_employee is None


def test_calculate_salary_uses_us_deduction_for_usa(db_session):
    created_employee = crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="Mia Carter",
            job_title="Manager",
            country="USA",
            salary=100000.0,
        ),
    )

    salary_details = crud.calculate_salary(db_session, created_employee.id)

    assert salary_details["deduction"] == 12000.0
    assert salary_details["net_salary"] == 88000.0


def test_calculate_salary_returns_none_for_missing_employee(db_session):
    assert crud.calculate_salary(db_session, 999) is None


def test_get_salary_stats_by_country_returns_aggregates(db_session):
    crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="Asha Patel",
            job_title="Analyst",
            country="India",
            salary=50000.0,
        ),
    )
    crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="Ravi Kumar",
            job_title="Manager",
            country="India",
            salary=70000.0,
        ),
    )

    stats = crud.get_salary_stats_by_country(db_session, "india")

    assert stats == {
        "country": "india",
        "min_salary": 50000.0,
        "max_salary": 70000.0,
        "avg_salary": 60000.0,
    }


def test_get_salary_stats_by_country_returns_none_when_no_matches(db_session):
    assert crud.get_salary_stats_by_country(db_session, "Canada") is None


def test_get_avg_salary_by_job_title_returns_average(db_session):
    crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="John Doe",
            job_title="Software Engineer",
            country="India",
            salary=50000.0,
        ),
    )
    crud.create_employee(
        db_session,
        schemas.EmployeeCreate(
            full_name="Jane Doe",
            job_title="Software Engineer",
            country="USA",
            salary=70000.0,
        ),
    )

    stats = crud.get_avg_salary_by_job_title(db_session, "software engineer")

    assert stats == {
        "job_title": "software engineer",
        "avg_salary": 60000.0,
    }


def test_get_avg_salary_by_job_title_returns_none_when_no_matches(db_session):
    assert crud.get_avg_salary_by_job_title(db_session, "Designer") is None
