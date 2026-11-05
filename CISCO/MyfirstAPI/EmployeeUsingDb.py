
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
import mysql.connector
import os
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# STEP 1: Create FastAPI Application
app = FastAPI(title="Employee Management API")

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# STEP 2: Load Database Configuration
load_dotenv()


# STEP 3: Database Connection
def get_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# STEP 4: Employee Validation
class EmployeeData(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    age: int = Field(ge=18, le=60)
    salary: float = Field(ge=25000)
    desig: str = Field(min_length=1, max_length=50)

    @field_validator("name", "desig")
    @classmethod
    def validate_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Cannot be blank")
        return value


class Employee(EmployeeData):
    id: int = Field(gt=0)


# STEP 5: Global Exception Handling
@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(map(str, e["loc"])),
            "message": e["msg"]
        }
        for e in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation Failed",
            "errors": errors
        }
    )


@app.exception_handler(mysql.connector.IntegrityError)
async def integrity_error(request: Request, exc):
    logger.error("Database integrity error: %s", exc)
    return JSONResponse(
        status_code=409,
        content={"message": "Employee ID already exists or data violates a database constraint"}
    )


@app.exception_handler(mysql.connector.Error)
async def database_error(request: Request, exc):
    print("MYSQL ERROR:", exc)

    return JSONResponse(
        status_code=500,
        content={
            "message": "Database operation failed",
            "error": str(exc)
        }
    )

@app.exception_handler(Exception)
async def general_error(request: Request, exc: Exception):
    logger.exception("Unexpected error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"}
    )


@app.get("/")
def home():
    return FileResponse("static/index.html")


# API 2: Add Employee
@app.post("/addEmployee", status_code=201)
def addEmployee(emp: Employee, conn=Depends(get_db)):
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO Employee (id, name, age, salary, desig)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (emp.id, emp.name, emp.age,emp.salary, emp.desig)
        cursor.execute(sql, values)
        conn.commit()
        return {"message": "Employee Added Successfully"}
    finally:
        cursor.close()      
        
        
# API 3: Get All Employees
@app.get("/getAllEmployees")
def getAllEmployees(conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Employee ORDER BY id")
        return cursor.fetchall()
    finally:
        cursor.close()
        
        
        
        
# API 4: Get Employee By ID
@app.get("/employeeByID/{id}")
def getEmployeeByID(id: int, conn=Depends(get_db)):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Employee WHERE id = %s",(id,))
        employee = cursor.fetchone()
        if employee is None:
            raise HTTPException(
                status_code=404,
                detail="Employee Not Found"
            )
        return employee
    finally:
        cursor.close()


# API 5: Update Employee
@app.put("/updateEmployee/{id}")
def updateEmployee(
    id: int,
    emp: EmployeeData,
    conn=Depends(get_db)
):

    cursor = conn.cursor()

    try:
        sql = """
        UPDATE Employee
        SET name=%s, age=%s, salary=%s, desig=%s
        WHERE id=%s
        """

        values = (
            emp.name, emp.age, emp.salary,
            emp.desig, id
        )

        cursor.execute(sql, values)

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Employee Not Found"
            )

        conn.commit()

        return {"message": "Employee Updated Successfully"}

    finally:
        cursor.close()


# API 6: Delete Employee
@app.delete("/deleteEmployee/{id}")
def deleteEmployee(id: int, conn=Depends(get_db)):

    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM Employee WHERE id = %s",
            (id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Employee Not Found"
            )

        conn.commit()

        return {"message": "Employee Deleted Successfully"}

    finally:
        cursor.close()


# API 7: Search Employees By Name
@app.get("/searchEmployees/{name}")
def searchEmployees(name: str, conn=Depends(get_db)):

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM Employee WHERE name LIKE %s",
            ("%" + name + "%",)
        )

        return cursor.fetchall()

    finally:
        cursor.close()


# API 8: Employee Count
@app.get("/employeeCount")
def employeeCount(conn=Depends(get_db)):

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM Employee")
        count = cursor.fetchone()[0]

        return {"totalEmployees": count}

    finally:
        cursor.close()

app.mount("/static", StaticFiles(directory="static"), name="static")