const tasksUrl = "/api/u4u/tasks";
document.addEventListener("DOMContentLoaded", () => {
	const taskForm = document.getElementById("task-form");
	const taskTableBody = document.querySelector("#tasks-table tbody");

	function resetRow(row) {
		row.children[2].children[0].style.display = "inline-block";
		row.children[2].children[1].style.display = "none";
		row.children[2].children[2].style.display = "none";
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

// Enable editing for a task row
window.enableEdit = async (taskId) =>{
	const row = document.querySelector(`#task-row-${taskId}`);
	const nameInput = row.querySelector(".task-name input");
	const descriptionInput = row.querySelector(".task-description input");
	const statusInput = row.querySelector(".task-status input");
	const typeInput = row.querySelector(".task-type input");
	const categoryInput = row.querySelector(".task-category input");

	// Store the current values in data attributes in case of cancel
	nameInput.dataset.originalValue = nameInput.value;
	descriptionInput.dataset.originalValue = descriptionInput.value;
	statusInput.dataset.originalValue = statusInput.value;
	typeInput.dataset.originalValue = typeInput.value;
	categoryInput.dataset.originalValue = categoryInput.value;

	// Make cells editable
	nameInput.disabled = false;
	descriptionInput.disabled = false;
	statusInput.disabled = false;
	typeInput.disabled = false;
	categoryInput.disabled = false;

	// Show save and cancel buttons, hide edit button

	row.children[2].children[0].style.display = "none";
	row.children[2].children[1].style.display = "inline-block";
	row.children[2].children[2].style.display = "inline-block";
}

// Save the updated task
window.saveEdit = async (taskId) => {
	const row = document.querySelector(`#task-row-${taskId}`);
	const nameInput = row.querySelector(".task-name input");
	const descriptionInput = row.querySelector(".task-description input");
	const statusInput = row.querySelector(".task-status input");
	const typeInput = row.querySelector(".task-type input");
	const categoryInput = row.querySelector(".task-category input");


	const updatedName = nameInput.value.trim();
	const updatedDescription = descriptionInput.value.trim();
	const updatedStatus = statusInput.value.trim();
	const updatedType = typeInput.value.trim();
	const updatedCategory = categoryInput.value.trim();

	const requestBody = {
			title: updatedName,
			description: updatedDescription,
			status: updatedStatus,
			type: updatedType,
			category_id: updatedCategory,
	};

	try {
			const response = await fetch(`${tasksUrl}/${taskId}`, {
					method: "PUT",
					headers: {
							"Content-Type": "application/json",
					},
					body: JSON.stringify(requestBody),
			});

			if (!response.ok) {
					const error = await response.json();
					alert(`Error: ${error.detail}`);
					return;
			}

			alert("Task updated successfully!");

			row.querySelector(".task-name").textContent = updatedName;
			row.querySelector(".task-description").textContent = updatedColor;
			row.querySelector(".task-status").textContent = updatedStatus;
			row.querySelector(".task-type").textContent = updatedType;
			row.querySelector(".task-category").textContent = updatedCategory;

			resetRow(row);
	} catch (error) {
			console.error("Error updating task:", error);
			alert("An error occurred while updating the task.");
	}
}

	window.cancelEdit = async (taskId) =>  {
		const row = document.querySelector(`#task-row-${taskId}`);
		const nameInput = row.querySelector(".task-name input");
		const descriptionInput = row.querySelector(".task-description input");
		const statusInput = row.querySelector(".task-status input");
		const typeInput = row.querySelector(".task-type input");
		const categoryInput = row.querySelector(".task-category input");

		// Restore original values
		nameInput.value = nameInput.dataset.originalValue;
		descriptionInput.value = descriptionInput.dataset.originalValue;
		statusInput.value = statusInput.dataset.originalValue;
		typeInput.value = typeInput.dataset.originalValue;
		categoryInput.value = categoryInput.dataset.originalValue;

		resetRow(row);
	}

	// Delete a task
	window.deleteTask = async (taskId) => {
			const response = await fetch(`${tasksUrl}/${taskId}`, { method: "DELETE" });

			if (response.ok) {
					document.getElementById(`task-row-${taskId}`).remove();
			} else {
					alert("Error deleting task");
			}
	};
});

