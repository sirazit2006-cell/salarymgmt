import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
import models, schemas, crud
from main import app, get_db
from database import Base

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False},poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# Test data
test_employee = {
    "full_name": "John Doe",
    "job_title": "Software Engineer",
    "country": "India",
    "salary": 50000.0
}

def test_create_employee(setup_database):
    response = client.post("/employees/", json=test_employee)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == test_employee["full_name"]
    assert data["job_title"] == test_employee["job_title"]
    assert data["country"] == test_employee["country"]
    assert data["salary"] == test_employee["salary"]
    assert "id" in data

def test_read_employees(setup_database):
    # First create an employee
    client.post("/employees/", json=test_employee)
    response = client.get("/employees/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["full_name"] == test_employee["full_name"]

def test_read_employee(setup_database):
    # Create employee and get its ID
    create_response = client.post("/employees/", json=test_employee)
    emp_id = create_response.json()["id"]

    response = client.get(f"/employees/{emp_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == emp_id
    assert data["full_name"] == test_employee["full_name"]

def test_read_employee_not_found(setup_database):
    response = client.get("/employees/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"

def test_update_employee(setup_database):
    # Create employee
    create_response = client.post("/employees/", json=test_employee)
    emp_id = create_response.json()["id"]

    update_data = {
        "full_name": "Jane Doe",
        "job_title": "Senior Engineer",
        "country": "USA",
        "salary": 60000.0
    }
    response = client.put(f"/employees/{emp_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["job_title"] == update_data["job_title"]
    assert data["country"] == update_data["country"]
    assert data["salary"] == update_data["salary"]

def test_update_employee_not_found(setup_database):
    update_data = {
        "full_name": "Jane Doe",
        "job_title": "Senior Engineer",
        "country": "USA",
        "salary": 60000.0
    }
    response = client.put("/employees/999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"

def test_delete_employee(setup_database):
    # Create employee
    create_response = client.post("/employees/", json=test_employee)
    emp_id = create_response.json()["id"]

    response = client.delete(f"/employees/{emp_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Employee deleted successfully"

    # Verify deletion
    get_response = client.get(f"/employees/{emp_id}")
    assert get_response.status_code == 404

def test_delete_employee_not_found(setup_database):
    response = client.delete("/employees/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"

def test_get_salary(setup_database):
    # Create employee
    create_response = client.post("/employees/", json=test_employee)
    emp_id = create_response.json()["id"]

    response = client.get(f"/employees/{emp_id}/salary")
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == emp_id
    assert data["gross_salary"] == test_employee["salary"]
    assert data["deduction"] == test_employee["salary"] * 0.10  # India deduction
    assert data["net_salary"] == test_employee["salary"] - data["deduction"]

def test_get_salary_not_found(setup_database):
    response = client.get("/employees/999/salary")
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"

def test_salary_stats_by_country(setup_database):
    # Create employees
    client.post("/employees/", json=test_employee)
    client.post("/employees/", json={
        "full_name": "Alice Smith",
        "job_title": "Manager",
        "country": "India",
        "salary": 70000.0
    })

    response = client.get("/metrics/country/India")
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "India"
    assert "min_salary" in data
    assert "max_salary" in data
    assert "avg_salary" in data

def test_salary_stats_by_country_not_found(setup_database):
    response = client.get("/metrics/country/NonExistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "No data found for this country"

def test_avg_salary_by_job(setup_database):
    # Create employees
    client.post("/employees/", json=test_employee)
    client.post("/employees/", json={
        "full_name": "Bob Johnson",
        "job_title": "Software Engineer",
        "country": "USA",
        "salary": 55000.0
    })

    response = client.get("/metrics/job/Software Engineer")
    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] == "Software Engineer"
    assert "avg_salary" in data

def test_avg_salary_by_job_not_found(setup_database):
    response = client.get("/metrics/job/NonExistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "No data found for this job title"