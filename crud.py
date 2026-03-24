from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_emp = models.Employee(**employee.model_dump())
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

def get_employees(db: Session):
    return db.query(models.Employee).all()

def get_employee(db: Session, emp_id: int):
    return db.query(models.Employee).filter(models.Employee.id == emp_id).first()

def update_employee(db: Session, emp_id: int, employee: schemas.EmployeeUpdate):
    db_emp = get_employee(db, emp_id)
    if not db_emp:
        return None

    for key, value in employee.model_dump().items():
        setattr(db_emp, key, value)

    db.commit()
    db.refresh(db_emp)
    return db_emp

def delete_employee(db: Session, emp_id: int):
    db_emp = get_employee(db, emp_id)
    if not db_emp:
        return None

    db.delete(db_emp)
    db.commit()
    return db_emp

def calculate_salary(db: Session, emp_id: int):
    emp = get_employee(db, emp_id)
    if not emp:
        return None

    gross = emp.salary

    if emp.country.lower() == "india":
        deduction = gross * 0.10
    elif emp.country.lower() in ["united states", "usa"]:
        deduction = gross * 0.12
    else:
        deduction = 0

    net = gross - deduction

    return {
        "employee_id": emp.id,
        "full_name": emp.full_name,
        "country": emp.country,
        "gross": gross,
        "deduction": deduction,
        "net": net
    }


def get_salary_stats_by_country(db: Session, country: str):
    result = db.query(
        func.min(models.Employee.salary).label("min_salary"),
        func.max(models.Employee.salary).label("max_salary"),
        func.avg(models.Employee.salary).label("avg_salary")
    ).filter(models.Employee.country.ilike(country)).first()

    if result and result.min_salary is not None:
        return {
            "country": country,
            "min_salary": result.min_salary,
            "max_salary": result.max_salary,
            "avg_salary": round(result.avg_salary, 2)
        }
    return None


def get_avg_salary_by_job_title(db: Session, job_title: str):
    result = db.query(
        func.avg(models.Employee.salary).label("avg_salary")
    ).filter(models.Employee.job_title.ilike(job_title)).first()

    if result and result.avg_salary is not None:
        return {
            "job_title": job_title,
            "avg_salary": round(result.avg_salary, 2)
        }
    return None
