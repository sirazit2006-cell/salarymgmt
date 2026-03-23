from pydantic import BaseModel, Field

class EmployeeBase(BaseModel):
    full_name: str = Field(..., example="John Doe")
    job_title: str = Field(..., example="Software Engineer")
    country: str = Field(..., example="India")
    salary: float = Field(..., gt=0)

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        orm_mode = True
