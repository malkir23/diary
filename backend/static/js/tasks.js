const tasksUrl = "/api/u4u/tasks";
document.addEventListener("DOMContentLoaded", () => {
	const taskForm = document.getElementById("task-form");
	const taskTableBody = document.querySelector("#tasks-table tbody");
	const categorySelect = document.getElementById("task-category");

	// Fetch existing tasks
	async function fetchData() {
			const tasksResponse = await fetch(`${tasksUrl}/list`);

			const tasks = await tasksResponse.json();

			// Populate tasks table
			tasks.forEach(addTaskToTable);
	}

	// Add a task row to the table
	function addTaskToTable(task) {
			const row = document.createElement("tr");
			row.id = `task-row-${task.id}`;
			row.innerHTML = `
					<td class="task-title">${task.title}</td>
					<td class="task-description">${task.description}</td>
					<td class="task-status">${task.status}</td>
					<td class="task-type">${task.type}</td>
					<td class="task-category">${task.category.name}</td>
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
					title: taskForm["title"].value,
					description: taskForm["description"].value,
					status: taskForm["status"].value,
					type: taskForm["type"].value,
					category_id: parseInt(taskForm["category_id"].value),
			};

			const response = await fetch(tasksUrl, {
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

	// Edit a task (similar to the previous implementation)
	window.editTask = (taskId) => {
			// Inline editing logic here
	};

	// Delete a task
	window.deleteTask = async (taskId) => {
			const response = await fetch(`${tasksUrl}/${taskId}`, { method: "DELETE" });

			if (response.ok) {
					document.getElementById(`task-row-${taskId}`).remove();
			} else {
					alert("Error deleting task");
			}
	};

	fetchData();
});

