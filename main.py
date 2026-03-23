from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, SessionLocal, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/employees/", response_model=schemas.EmployeeResponse)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db, employee)

@app.get("/employees/", response_model=list[schemas.EmployeeResponse])
def read_employees(db: Session = Depends(get_db)):
    return crud.get_employees(db)

@app.get("/employees/{emp_id}", response_model=schemas.EmployeeResponse)
def read_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = crud.get_employee(db, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.put("/employees/{emp_id}", response_model=schemas.EmployeeResponse)
def update_employee(emp_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    emp = crud.update_employee(db, emp_id, employee)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = crud.delete_employee(db, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


@app.get("/employees/{emp_id}/salary")
def get_salary(emp_id: int, db: Session = Depends(get_db)):
    result = crud.calculate_salary(db, emp_id)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result

# 1️⃣ Country Salary Stats
@app.get("/employees/salary/country/{country}")
def salary_stats_by_country(country: str, db: Session = Depends(get_db)):
    result = crud.get_salary_stats_by_country(db, country)
    if not result:
        raise HTTPException(status_code=404, detail="No data found for this country")
    return result


# 2️⃣ Job Title Avg Salary
@app.get("/employees/salary/job/{job_title}")
def avg_salary_by_job(job_title: str, db: Session = Depends(get_db)):
    result = crud.get_avg_salary_by_job_title(db, job_title)
    if not result:
        raise HTTPException(status_code=404, detail="No data found for this job title")
    return result