from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

@app.get("/hello")
def home():
    return {"message": "Hello World"}

@app.get("/greet")
def greet():
    return{"Good morning"}

class Employee(BaseModel):
    id:int
    name:str
    age:int
    salary:float
    designation:str
employees=[]
@app.post("/addEmployees")
def add_employees(emps:Employee):
    employees.append(emps)
    return {"message:successfully added"}

@app.get("/getEmployees")
def get_employees():
    return employees

@app.get("/EmployeeById/{id}")
def get_employees_byId(id:int):
    for emp in employees:
        if emp.id==id:
            return emp
    return {"message:not found"}

@app.delete("/deleteById/{id}")
def del_employees_byId(id:int):
    for emp in employees:
        if emp.id==id:
            employees.remove(emp)
            return {"message:deleted successfully"}
    return {"message:deletion failed"}

@app.delete("/deleteAllEmployees")
def del_all_employees():
    employees.clear()
    return {"message:deleted successfully"}

@app.put("/updateEmployee/{id}")
def update_employee(id:int,updatedEmp:Employee):
    for emp in employees:
        if emp.id == id:
            emp.name=updatedEmp.name
            emp.age=updatedEmp.age
            emp.salary=updatedEmp.salary
            emp.designation=updatedEmp.designation
            return emp
    return {"message:employee not found"}

@app.get("/TotalEmployees")
def count_employees():
    return {"Total employees": len(employees)}

@app.get("/findByDesignation/{des}")
def getby_Designation(des:str):
    result=[]
    for emp in employees:
        if emp.designation.lower() == des.lower():
            result.append(emp)
    return result

@app.get("/greaterThanSalary/{sal}")
def get_salary_greaterThan(sal:float):
    result=[]
    for emp in employees:
        if emp.salary>sal:
            result.append(emp)
    return result

@app.get("/findByage/{age}")
def findBy_age(age:int):
    result=[]
    for emp in employees:
        if emp.age == age:
          result.append(emp)
    return result

@app.get("/totalSalary")
def total_slaries():
    total=0
    for emp in employees:
        total+=emp.salary
    return {"Total salary is":total}

@app.put("/updateSalary/{id}/{salary}")
def update_salary(id:int,salary:float):
    for emp in employees:
        if emp.id==id:
            emp.salary=salary
            return emp
    return {"message: cannot find"}

@app.get("/findByname/{name}")
def findBy_age(name:str):
    result=[]
    for emp in employees:
        if emp.name==name:
         result.append(emp)
    return result

        



