const form = document.querySelector("#employee-form");
const rows = document.querySelector("#employee-rows");
const count = document.querySelector("#employee-count");
const statusMessage = document.querySelector("#status");
const emptyState = document.querySelector("#empty-state");
const searchInput = document.querySelector("#search");
const idInput = document.querySelector("#employee-id");
const saveButton = document.querySelector("#save-button");
const cancelEditButton = document.querySelector("#cancel-edit");
const formTitle = document.querySelector("#form-title");

let employees = [];
let editingId = null;

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const result = await response.json();

  if (!response.ok) {
    const validationErrors = result.errors
      ?.map((error) => `${error.field}: ${error.message}`)
      .join("; ");
    throw new Error(result.message || result.detail || validationErrors || `Request failed (${response.status})`);
  }

  return result;
}

function showStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function renderEmployees() {
  const query = searchInput.value.trim().toLowerCase();
  const visibleEmployees = employees.filter((employee) =>
    `${employee.name} ${employee.desig}`.toLowerCase().includes(query)
  );

  rows.replaceChildren();
  for (const employee of visibleEmployees) {
    const row = document.createElement("tr");
    const values = [employee.id, employee.name, employee.age, employee.salary, employee.desig];

    for (const value of values) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    }

    const actions = document.createElement("td");
    const actionGroup = document.createElement("div");
    actionGroup.className = "row-actions";

    const editButton = document.createElement("button");
    editButton.className = "action-button";
    editButton.type = "button";
    editButton.textContent = "Edit";
    editButton.addEventListener("click", () => beginEdit(employee));

    const deleteButton = document.createElement("button");
    deleteButton.className = "action-button delete-button";
    deleteButton.type = "button";
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", () => deleteEmployee(employee));

    actionGroup.append(editButton, deleteButton);
    actions.append(actionGroup);
    row.append(actions);
    rows.append(row);
  }

  count.textContent = employees.length;
  emptyState.hidden = visibleEmployees.length > 0 || statusMessage.classList.contains("error");
}

async function loadEmployees() {
  showStatus("Loading employees…");
  try {
    employees = await request("/getAllEmployees");
    renderEmployees();
    showStatus("");
    return true;
  } catch (error) {
    employees = [];
    showStatus(`Could not load employees: ${error.message}`, true);
    renderEmployees();
    return false;
  }
}

function beginEdit(employee) {
  editingId = employee.id;
  form.elements.name.value = employee.name;
  form.elements.age.value = employee.age;
  form.elements.salary.value = employee.salary;
  form.elements.desig.value = employee.desig;
  idInput.value = employee.id;
  idInput.disabled = true;
  formTitle.textContent = `Edit employee #${employee.id}`;
  saveButton.textContent = "Save changes";
  cancelEditButton.hidden = false;
  form.elements.name.focus();
}

function resetForm() {
  editingId = null;
  form.reset();
  idInput.disabled = false;
  formTitle.textContent = "Add an employee";
  saveButton.textContent = "Add employee";
  cancelEditButton.hidden = true;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;

  const formData = new FormData(form);
  const employee = {
    name: formData.get("name").trim(),
    age: Number(formData.get("age")),
    salary: Number(formData.get("salary")),
    desig: formData.get("desig").trim(),
  };
  const isEditing = editingId !== null;
  const url = isEditing ? `/updateEmployee/${editingId}` : "/addEmployee";

  if (!isEditing) employee.id = Number(formData.get("id"));

  saveButton.disabled = true;
  try {
    const result = await request(url, {
      method: isEditing ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(employee),
    });
    resetForm();
    if (await loadEmployees()) {
      showStatus(result.message || (isEditing ? "Employee updated." : "Employee added."));
    } else {
      showStatus("Employee saved, but the list could not be refreshed.", true);
    }
  } catch (error) {
    showStatus(`Could not save employee: ${error.message}`, true);
  } finally {
    saveButton.disabled = false;
  }
});

async function deleteEmployee(employee) {
  if (!window.confirm(`Delete ${employee.name} (ID ${employee.id})?`)) return;

  try {
    const result = await request(`/deleteEmployee/${employee.id}`, { method: "DELETE" });
    if (await loadEmployees()) {
      showStatus(result.message || "Employee deleted.");
    } else {
      showStatus("Employee deleted, but the list could not be refreshed.", true);
    }
  } catch (error) {
    showStatus(`Could not delete employee: ${error.message}`, true);
  }
}

cancelEditButton.addEventListener("click", resetForm);
searchInput.addEventListener("input", renderEmployees);
loadEmployees();
