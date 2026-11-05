
class EmployeeManagement:

    def __init__(self):
        self.employees = set()

    def add_employee(self, empid, name, salary):
        if empid <= 0:
            raise ValueError("Employee ID must be positive")

        if name.strip() == "":
            raise ValueError("Employee Name cannot be empty")

        if salary <= 0:
            raise ValueError("Salary must be greater than ZERO")

        for emp in self.employees:
            if emp[0] == empid:
                raise ValueError("Employee ID already exists")

        employee = (empid, name, salary)

        self.employees.add(employee)
        print("Employee Added Successfully!")

    def view_employees(self):
        if len(self.employees) == 0:
            print("No Employees Found!")
        else:
            for emp in self.employees:
                print(emp)

    def search_employee(self, empid):
        for emp in self.employees:
            if emp[0] == empid:
                print("Employee Found:", emp)
                return

        raise ValueError("Employee Not Found!")

    def update_salary(self, empid, salary):
        if salary <= 0:
            raise ValueError("Salary must be positive")

        for emp in self.employees:
            if emp[0] == empid:
                self.employees.remove(emp)

                updated_employee = (empid, emp[1], salary)
                self.employees.add(updated_employee)

                print("Salary Updated Successfully!")
                return

        raise ValueError("Employee Not Found!")

    def delete_employee(self, empid):
        for emp in self.employees:
            if emp[0] == empid:
                self.employees.remove(emp)
                print("Employee Deleted Successfully!")
                return

        raise ValueError("Employee Not Found!")


obj = EmployeeManagement()

while True:
    print("\n====== EMPLOYEE MENU ======")
    print("1. Add Employee")
    print("2. View Employees")
    print("3. Search Employee")
    print("4. Update Salary")
    print("5. Delete Employee")
    print("6. Exit")
    print("===========================")

    choice = input("Enter your choice: ")

    if choice == "6":
        print("Thank you!")
        break

    try:
        if choice == "1":
            empid = int(input("Enter Employee ID: "))
            name = input("Enter Employee Name: ")
            salary = float(input("Enter Salary: "))

            obj.add_employee(empid, name, salary)

        elif choice == "2":
            obj.view_employees()

        elif choice == "3":
            empid = int(input("Enter Employee ID: "))
            obj.search_employee(empid)

        elif choice == "4":
            empid = int(input("Enter Employee ID: "))
            salary = float(input("Enter New Salary: "))
            obj.update_salary(empid, salary)

        elif choice == "5":
            empid = int(input("Enter Employee ID: "))
            obj.delete_employee(empid)

        else:
            raise ValueError("Invalid Menu Choice!")

    except ValueError as error:
        print("Error:", error)

    except Exception as error:
        print("Unexpected Error:", error)

    else:
        print("Operation Completed Successfully!")

    finally:
        print("Employee Operation Attempt Completed!")
