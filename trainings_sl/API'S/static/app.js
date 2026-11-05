const rowsElement = document.querySelector("#employee-rows");
const loadingElement = document.querySelector("#loading-state");
const emptyElement = document.querySelector("#empty-state");
const dialog = document.querySelector("#employee-dialog");
const form = document.querySelector("#employee-form");
const formError = document.querySelector("#form-error");
const searchInput = document.querySelector("#employee-search");

let employees = [];
let editingId = null;
let toastTimeout;

const avatarColors = [
  ["#eeeaff", "#7058c7"],
  ["#e8f5fb", "#3984a6"],
  ["#fff1e5", "#c48348"],
  ["#e7f5ee", "#458b69"],
  ["#fceaf0", "#b5617b"],
  ["#edf0ff", "#596db3"],
];

function formatSalary(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);
}

function getErrorMessage(data, fallback) {
  if (typeof data?.message === "string") return data.message;
  if (typeof data?.detail === "string") return data.detail;
  if (Array.isArray(data?.errors) && data.errors.length) {
    return data.errors.map((error) => `${error.field}: ${error.message}`).join("; ");
  }
  return fallback;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error("Could not reach the employee API. Check that the server is running.");
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = getErrorMessage(data, `Request failed (${response.status}).`);
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return data;
}

async function loadEmployees() {
  loadingElement.hidden = false;
  emptyElement.hidden = true;
  rowsElement.replaceChildren();

  try {
    const result = await request("/getAllEmployees");
    employees = Array.isArray(result) ? result : [];
    renderEmployees();
  } catch (error) {
    if (error.status === 404 && error.message === "No Employees Available") {
      employees = [];
      renderEmployees();
    } else {
      showToast(error.message, true);
      loadingElement.hidden = true;
      emptyElement.hidden = false;
      document.querySelector("#empty-title").textContent = "Could not load employees";
      document.querySelector("#empty-description").textContent = error.message;
      document.querySelector("#empty-add").hidden = true;
      updateSummary([]);
    }
  }
}

function initials(name) {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part.charAt(0))
    .join("")
    .toUpperCase();
}

function renderEmployees() {
  loadingElement.hidden = true;
  document.querySelector("#empty-title").textContent = "Your team starts here";
  document.querySelector("#empty-description").textContent =
    "Add your first employee to build your directory.";
  document.querySelector("#empty-add").hidden = false;
  updateSummary(employees);

  const query = searchInput.value.trim().toLocaleLowerCase();
  const filtered = employees.filter((employee) =>
    [employee.name, employee.desig, String(employee.id)]
      .some((value) => String(value).toLocaleLowerCase().includes(query)),
  );

  rowsElement.replaceChildren(...filtered.map(createEmployeeRow));
  emptyElement.hidden = filtered.length !== 0;
  document.querySelector("#results-label").textContent = query
    ? `Showing ${filtered.length} of ${employees.length} employees`
    : `Showing ${employees.length} ${employees.length === 1 ? "employee" : "employees"}`;
  document.querySelector("#employee-count").textContent = employees.length;
  document.querySelector("#nav-count").textContent = employees.length;
}

function createEmployeeRow(employee, index) {
  const row = document.createElement("tr");
  const [background, foreground] = avatarColors[index % avatarColors.length];
  row.innerHTML = `
    <td>
      <div class="employee-cell">
        <span class="employee-avatar" style="background:${background};color:${foreground}"></span>
        <span>
          <span class="employee-name"></span>
          <span class="employee-id"></span>
        </span>
      </div>
    </td>
    <td><span class="designation-pill"></span></td>
    <td><span class="age-label"></span></td>
    <td><span class="salary-label"></span></td>
    <td>
      <div class="row-actions">
        <button class="icon-button edit-button" type="button" aria-label="Edit employee"></button>
        <button class="icon-button delete-button" type="button" aria-label="Delete employee"></button>
      </div>
    </td>`;

  row.querySelector(".employee-avatar").textContent = initials(employee.name);
  row.querySelector(".employee-name").textContent = employee.name;
  row.querySelector(".employee-id").textContent = `ID ${employee.id}`;
  row.querySelector(".designation-pill").textContent = employee.desig;
  row.querySelector(".age-label").textContent = `${employee.age} yrs`;
  row.querySelector(".salary-label").textContent = formatSalary(employee.salary);
  row.querySelector(".edit-button").innerHTML =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14 5 5 5M4 20l4.3-.9L19 8.4a2.1 2.1 0 0 0-3-3L5.3 16.1 4 20Z"/></svg>';
  row.querySelector(".delete-button").innerHTML =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M10 11v6m4-6v6M5.5 7l1 13h11l1-13M9 7V4h6v3"/></svg>';
  row.querySelector(".edit-button").addEventListener("click", () => openDialog(employee));
  row.querySelector(".delete-button").addEventListener("click", () => deleteEmployee(employee));
  return row;
}

function updateSummary(list) {
  const count = list.length;
  const averageAge = count
    ? Math.round(list.reduce((total, employee) => total + Number(employee.age), 0) / count)
    : 0;
  const designations = new Set(list.map((employee) => employee.desig.toLocaleLowerCase())).size;
  const payroll = list.reduce((total, employee) => total + Number(employee.salary), 0);

  document.querySelector("#total-employees").textContent = count;
  document.querySelector("#total-designations").textContent = designations;
  document.querySelector("#average-age").textContent = count ? `${averageAge} yrs` : "—";
  document.querySelector("#total-salary").textContent = formatSalary(payroll);
}

function openDialog(employee = null) {
  editingId = employee ? employee.id : null;
  form.reset();
  formError.hidden = true;
  document.querySelector("#dialog-title").textContent = employee ? "Edit employee" : "Add employee";
  document.querySelector("#dialog-description").textContent = employee
    ? "Update this employee's details."
    : "Enter the employee's details below.";
  document.querySelector("#save-employee").textContent = employee ? "Save changes" : "Add employee";

  const idInput = document.querySelector("#employee-id");
  idInput.disabled = Boolean(employee);
  idInput.value = employee?.id ?? "";
  document.querySelector("#employee-name").value = employee?.name ?? "";
  document.querySelector("#employee-age").value = employee?.age ?? "";
  document.querySelector("#employee-salary").value = employee?.salary ?? "";
  document.querySelector("#employee-designation").value = employee?.desig ?? "";
  dialog.showModal();
  (employee ? document.querySelector("#employee-name") : idInput).focus();
}

function showToast(message, isError = false) {
  const region = document.querySelector("#toast-region");
  const toast = document.createElement("div");
  toast.className = `toast${isError ? " error" : ""}`;
  toast.textContent = message;
  region.replaceChildren(toast);
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.remove(), 3800);
}

function displayFormError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

function validateForm(data) {
  if (!editingId && (!Number.isInteger(data.id) || data.id <= 0)) {
    return "Employee ID must be a positive whole number.";
  }
  if (data.name.length < 3 || data.name.length > 30) {
    return "Name must be between 3 and 30 characters.";
  }
  if (!Number.isInteger(data.age) || data.age < 18 || data.age > 60) {
    return "Age must be a whole number between 18 and 60.";
  }
  if (!Number.isFinite(data.salary) || data.salary < 25000) {
    return "Salary must be at least $25,000.";
  }
  if (data.desig.length < 3 || data.desig.length > 30) {
    return "Designation must be between 3 and 30 characters.";
  }
  return "";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.hidden = true;

  const data = {
    id: editingId ?? Number(document.querySelector("#employee-id").value),
    name: document.querySelector("#employee-name").value.trim(),
    age: Number(document.querySelector("#employee-age").value),
    salary: Number(document.querySelector("#employee-salary").value),
    desig: document.querySelector("#employee-designation").value.trim(),
  };
  const validationMessage = validateForm(data);
  if (validationMessage) {
    displayFormError(validationMessage);
    return;
  }

  const saveButton = document.querySelector("#save-employee");
  saveButton.disabled = true;
  saveButton.textContent = "Saving...";
  try {
    const isEditing = editingId !== null;
    const path = isEditing ? `/updateEmployee/${editingId}` : "/addEmployee";
    const result = await request(path, {
      method: isEditing ? "PUT" : "POST",
      body: JSON.stringify(data),
    });
    dialog.close();
    showToast(result?.message ?? (isEditing ? "Employee updated." : "Employee added."));
    await loadEmployees();
  } catch (error) {
    displayFormError(error.message);
  } finally {
    saveButton.disabled = false;
    saveButton.textContent = editingId !== null ? "Save changes" : "Add employee";
  }
});

async function deleteEmployee(employee) {
  if (!window.confirm(`Delete ${employee.name} from the employee directory?`)) return;
  try {
    const result = await request(`/deleteEmployee/${employee.id}`, { method: "DELETE" });
    showToast(result?.message ?? "Employee deleted.");
    await loadEmployees();
  } catch (error) {
    showToast(error.message, true);
  }
}

document.querySelector("#add-employee").addEventListener("click", () => openDialog());
document.querySelector("#empty-add").addEventListener("click", () => openDialog());
document.querySelectorAll(".close-dialog").forEach((button) => {
  button.addEventListener("click", () => dialog.close());
});
searchInput.addEventListener("input", renderEmployees);
document.addEventListener("keydown", (event) => {
  if (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
    event.preventDefault();
    searchInput.focus();
  }
});

loadEmployees();
