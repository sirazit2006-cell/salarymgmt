from pydantic import BaseModel, ConfigDict, Field,Decimal

class EmployeeBase(BaseModel):
    full_name: str = Field(..., json_schema_extra={"example": "John Doe"})
    job_title: str = Field(..., json_schema_extra={"example": "Software Engineer"})
    country: str = Field(..., json_schema_extra={"example": "India"})
    salary: Decimal = Field(..., gt=0)

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
