
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

app = FastAPI()


# ==========================================
# STEP 1: GLOBAL EXCEPTION HANDLING
# ==========================================

class EmployeeException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code


@app.exception_handler(EmployeeException)
async def globalExceptionHandler(request: Request, exc: EmployeeException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )


# Global Validation Exception Handler
@app.exception_handler(RequestValidationError)
async def validationExceptionHandler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation Failed",
            "errors": [
                {
                    "field": ".".join(str(x) for x in error["loc"]),
                    "message": error["msg"]
                }
                for error in exc.errors()
            ]
        }
    )


# ==========================================
# STEP 2: EMPLOYEE CLASS WITH VALIDATION
# ==========================================

class Employee(BaseModel):

    id: int = Field(gt=0, description="ID must be greater than 0")

    name: str = Field(min_length=3, max_length=30,
                      description="Name must be 3 to 30 characters")

    age: int = Field(ge=18, le=60,
                     description="Age must be between 18 and 60")

    salary: float = Field(ge=25000,
                          description="Salary must be greater than or equal to 25000")

    desig: str = Field(min_length=3, max_length=30,
                       description="Designation must be 3 to 30 characters")


# ==========================================
# STEP 3: STORE EMPLOYEES IN LIST
# ==========================================

employees = []


# API 1: Home
@app.get("/")
def home():
    return {"message": "Welcome to Employee Management"}


# API 2: Add Employee
@app.post("/addEmployee", status_code=201)
def addEmployee(employee: Employee):

    for e in employees:
        if e.id == employee.id:
            raise EmployeeException("Employee ID Already Exists", 400)

    employees.append(employee)

    return {"message": "Employee Added Successfully"}


# API 3: Get All Employees
@app.get("/getAllEmployees")
def getAllEmployees():

    if len(employees) == 0:
        raise EmployeeException("No Employees Available", 404)

    return employees


# API 4: Get Employee By ID
@app.get("/employeeByID/{id}")
def getEmployeeByID(id: int):

    for e in employees:
        if e.id == id:
            return e

    raise EmployeeException("Employee Not Found", 404)


# API 5: Get Employee By Name
@app.get("/employeeByName/{name}")
def getEmployeeByName(name: str):

    for e in employees:
        if e.name.lower() == name.lower():
            return e

    raise EmployeeException("Employee Name Not Found", 404)


# API 6: Get Employees By Designation
@app.get("/employeeByDesignation/{desig}")
def getEmployeeByDesignation(desig: str):

    result = []

    for e in employees:
        if e.desig.lower() == desig.lower():
            result.append(e)

    if len(result) == 0:
        raise EmployeeException("Designation Not Found", 404)

    return result


# API 7: Update Employee
@app.put("/updateEmployee/{id}")
def updateEmployee(id: int, employee: Employee):

    for i in range(len(employees)):

        if employees[i].id == id:

            if employee.id != id:
                raise EmployeeException("Employee ID Cannot Be Changed", 400)

            employees[i] = employee

            return {"message": "Employee Updated Successfully"}

    raise EmployeeException("Employee Not Found", 404)


# API 8: Delete Employee
@app.delete("/deleteEmployee/{id}")
def deleteEmployee(id: int):

    for e in employees:

        if e.id == id:
            employees.remove(e)

            return {"message": "Employee Deleted Successfully"}

    raise EmployeeException("Employee Not Found", 404)


# API 9: Delete All Employees
@app.delete("/deleteAllEmployees")
def deleteAllEmployees():

    if len(employees) == 0:
        raise EmployeeException("No Employees Available", 404)

    employees.clear()

    return {"message": "All Employees Deleted Successfully"}
