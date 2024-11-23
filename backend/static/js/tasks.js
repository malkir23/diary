document.addEventListener("DOMContentLoaded", () => {
	const taskForm = document.getElementById("task-form");
	const taskTableBody = document.querySelector("#tasks-table tbody");

	// Fetch existing tasks and populate the table
	async function fetchTasks() {
			const response = await fetch("/tasks/list");
			const tasks = await response.json();

			tasks.forEach(addTaskToTable);
	}

	// Add a task row to the table
	function addTaskToTable(task) {
			const row = document.createElement("tr");
			row.id = `task-row-${task.id}`;
			row.innerHTML = `
					<td class="task-name">${task.name}</td>
					<td class="task-type">${task.type}</td>
					<td class="task-category">${task.category}</td>
					<td>
							<button onclick="editTask(${task.id})">Edit</button>
							<button onclick="deleteTask(${task.id})">Delete</button>
					</td>
			`;
			taskTableBody.appendChild(row);
	}

	// Handle form submission for creating a new task
	taskForm.addEventListener("submit", async (event) => {
			event.preventDefault();

			const taskData = {
					name: taskForm["name"].value,
					type: taskForm["type"].value,
					category: taskForm["category"].value,
			};

			const response = await fetch("/tasks", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(taskData),
			});

			if (response.ok) {
					const newTask = await response.json();
					addTaskToTable(newTask);
					taskForm.reset();
			} else {
					alert("Error creating task");
			}
	});

	// Edit a task
	window.editTask = (taskId) => {
			const row = document.getElementById(`task-row-${taskId}`);
			const nameCell = row.querySelector(".task-name");
			const typeCell = row.querySelector(".task-type");
			const categoryCell = row.querySelector(".task-category");

			nameCell.innerHTML = `<input type="text" value="${nameCell.textContent}">`;
			typeCell.innerHTML = `<select>
					<option value="todo" ${typeCell.textContent === "todo" ? "selected" : ""}>Todo</option>
					<option value="in-progress" ${typeCell.textContent === "in-progress" ? "selected" : ""}>In Progress</option>
					<option value="done" ${typeCell.textContent === "done" ? "selected" : ""}>Done</option>
			</select>`;
			categoryCell.innerHTML = `<input type="text" value="${categoryCell.textContent}">`;

			const actionCell = row.querySelector("td:last-child");
			actionCell.innerHTML = `
					<button onclick="saveTask(${taskId})">Save</button>
					<button onclick="cancelEdit(${taskId})">Cancel</button>
			`;
	};

	// Save the edited task
	window.saveTask = async (taskId) => {
			const row = document.getElementById(`task-row-${taskId}`);
			const name = row.querySelector(".task-name input").value;
			const type = row.querySelector(".task-type select").value;
			const category = row.querySelector(".task-category input").value;

			const response = await fetch(`/tasks/${taskId}`, {
					method: "PUT",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ name, type, category }),
			});

			if (response.ok) {
					row.querySelector(".task-name").textContent = name;
					row.querySelector(".task-type").textContent = type;
					row.querySelector(".task-category").textContent = category;

					row.querySelector("td:last-child").innerHTML = `
							<button onclick="editTask(${taskId})">Edit</button>
							<button onclick="deleteTask(${taskId})">Delete</button>
					`;
			} else {
					alert("Error updating task");
			}
	};

	// Cancel edit
	window.cancelEdit = (taskId) => {
			fetchTasks();
	};

	// Delete a task
	window.deleteTask = async (taskId) => {
			const response = await fetch(`/tasks/${taskId}`, { method: "DELETE" });

			if (response.ok) {
					document.getElementById(`task-row-${taskId}`).remove();
			} else {
					alert("Error deleting task");
			}
	};

	fetchTasks();
});
