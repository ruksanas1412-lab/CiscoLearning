
const API_URL = "";

// Store currently displayed employees
let employees = [];
let editingId = null;


// ======================================
// 1. LOAD ALL EMPLOYEES
// ======================================

async function loadEmployees() {
    try {
        const response = await fetch(`${API_URL}/getAllEmployees`);

        if (!response.ok) {
            throw new Error("Unable to fetch employees");
        }

        employees = await response.json();

        displayEmployees(employees);
        updateStatistics(employees);

    } catch (error) {
        showToast(error.message);
        document.getElementById("employeeTable").innerHTML =
            `<tr><td colspan="6" class="empty-message">
                Failed to load employees
            </td></tr>`;
    }
}


// ======================================
// 2. DISPLAY EMPLOYEES
// ======================================

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function displayEmployees(data) {

    const table = document.getElementById("employeeTable");

    document.getElementById("employeeLabel").textContent =
        `${data.length} employees`;

    if (data.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="6" class="empty-message">
                    No employees found
                </td>
            </tr>`;
        return;
    }

    table.innerHTML = data.map(emp => `
        <tr>
            <td>${emp.id}</td>

            <td class="employee-name">
                ${escapeHTML(emp.name)}
            </td>

            <td>${emp.age}</td>

            <td>${escapeHTML(emp.desig)}</td>

            <td class="salary">
                ₹${Number(emp.salary).toLocaleString("en-IN")}
            </td>

            <td>
                <div class="action-buttons">

                    <button class="edit-btn"
                        onclick="editEmployee(${emp.id})">
                        Edit
                    </button>

                    <button class="delete-btn"
                        onclick="deleteEmployee(${emp.id})">
                        Delete
                    </button>

                </div>
            </td>
        </tr>
    `).join("");
}


// ======================================
// 3. UPDATE DASHBOARD STATISTICS
// ======================================

async function updateStatistics(data) {

    try {
        const response = await fetch(`${API_URL}/employeeCount`);
        const result = await response.json();

        document.getElementById("totalEmployees").textContent =
            result.totalEmployees;

    } catch (error) {
        document.getElementById("totalEmployees").textContent =
            data.length;
    }

    if (data.length === 0) {
        document.getElementById("averageSalary").textContent = "₹0";
        document.getElementById("highestSalary").textContent = "₹0";
        return;
    }

    const salaries = data.map(emp => Number(emp.salary));

    const totalSalary = salaries.reduce(
        (total, salary) => total + salary, 0
    );

    const average = totalSalary / salaries.length;
    const highest = Math.max(...salaries);

    document.getElementById("averageSalary").textContent =
        "₹" + Math.round(average).toLocaleString("en-IN");

    document.getElementById("highestSalary").textContent =
        "₹" + highest.toLocaleString("en-IN");
}


// ======================================
// 4. OPEN ADD EMPLOYEE MODAL
// ======================================

function openAddModal() {

    editingId = null;

    document.getElementById("employeeForm").reset();

    document.getElementById("modalTitle").textContent =
        "Add Employee";

    document.getElementById("saveBtn").textContent =
        "Add Employee";

    document.getElementById("idGroup").style.display = "block";

    document.getElementById("empId").disabled = false;

    document.getElementById("employeeModal").classList.add("show");
}


// ======================================
// 5. CLOSE MODAL
// ======================================

function closeModal() {

    document.getElementById("employeeModal").classList.remove("show");

    document.getElementById("employeeForm").reset();

    editingId = null;
}


// ======================================
// 6. ADD / UPDATE EMPLOYEE
// ======================================

document.getElementById("employeeForm").addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        const employee = {
            name: document.getElementById("empName").value.trim(),
            age: Number(document.getElementById("empAge").value),
            salary: Number(document.getElementById("empSalary").value),
            desig: document.getElementById("empDesig").value.trim()
        };

        let url;
        let method;

        if (editingId !== null) {

            url = `${API_URL}/updateEmployee/${editingId}`;
            method = "PUT";

        } else {

            employee.id = Number(
                document.getElementById("empId").value
            );

            url = `${API_URL}/addEmployee`;
            method = "POST";
        }

        const saveButton = document.getElementById("saveBtn");

        saveButton.disabled = true;
        saveButton.textContent = "Saving...";

        try {

            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(employee)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.message ||
                    result.detail ||
                    "Something went wrong"
                );
            }

            closeModal();

            showToast(
                editingId !== null
                    ? "Employee updated successfully!"
                    : "Employee added successfully!"
            );

            await loadEmployees();

        } catch (error) {

            showToast(error.message);

        } finally {

            saveButton.disabled = false;

            saveButton.textContent =
                editingId !== null ? "Update Employee" : "Add Employee";
        }
    }
);


// ======================================
// 7. EDIT EMPLOYEE
// ======================================

function editEmployee(id) {

    const emp = employees.find(employee => employee.id === id);

    if (!emp) {
        showToast("Employee not found");
        return;
    }

    editingId = id;

    document.getElementById("empId").value = emp.id;
    document.getElementById("empName").value = emp.name;
    document.getElementById("empAge").value = emp.age;
    document.getElementById("empSalary").value = emp.salary;
    document.getElementById("empDesig").value = emp.desig;

    document.getElementById("idGroup").style.display = "none";

    document.getElementById("modalTitle").textContent =
        "Edit Employee";

    document.getElementById("saveBtn").textContent =
        "Update Employee";

    document.getElementById("employeeModal").classList.add("show");
}


// ======================================
// 8. DELETE EMPLOYEE
// ======================================

async function deleteEmployee(id) {

    const confirmDelete = confirm(
        "Are you sure you want to delete this employee?"
    );

    if (!confirmDelete) return;

    try {

        const response = await fetch(
            `${API_URL}/deleteEmployee/${id}`,
            {
                method: "DELETE"
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.message || "Unable to delete employee"
            );
        }

        showToast("Employee deleted successfully!");

        await loadEmployees();

    } catch (error) {

        showToast(error.message);
    }
}


// ======================================
// 9. SEARCH EMPLOYEE BY NAME
// ======================================

document.getElementById("searchInput").addEventListener(
    "input",
    async function() {

        const name = this.value.trim();

        if (name === "") {
            displayEmployees(employees);
            return;
        }

        try {

            const response = await fetch(
                `${API_URL}/searchEmployees/${encodeURIComponent(name)}`
            );

            const result = await response.json();

            if (!response.ok) {
                throw new Error("Search failed");
            }

            displayEmployees(result);

        } catch (error) {

            showToast(error.message);
        }
    }
);


// ======================================
// 10. NOTIFICATION
// ======================================

let toastTimer;

function showToast(message) {

    const toast = document.getElementById("toast");

    toast.textContent = message;

    toast.classList.add("show");

    clearTimeout(toastTimer);

    toastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}


// ======================================
// 11. LOAD DATA WHEN PAGE OPENS
// ======================================

document.addEventListener("DOMContentLoaded", loadEmployees);
