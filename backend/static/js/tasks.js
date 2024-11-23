const tasksUrl = "/api/u4u/tasks";
document.addEventListener("DOMContentLoaded", () => {
	const taskForm = document.getElementById("task-form");
	const taskTableBody = document.querySelector("#tasks-table tbody");

	function resetRow(row) {
		row.children[5].children[0].style.display = "inline-block";
		row.children[5].children[1].style.display = "none";
		row.children[5].children[2].style.display = "none";
	}
	// Add a task row to the table
	function addTaskToTable(task) {

			const row = document.createElement("tr");
			row.id = `task-row-${task.id}`;
			row.innerHTML = `
					<td class="task-title"><input type="text" value="${task.title}" disabled></td>
					<td class="task-description"><textarea disabled>${task.description}</textarea></td>
					<td class="task-status">
						<select value="${task.status}" disabled>
							${Object.entries(JSON.parse(statuses)).map(([value, status]) =>
								`<option
									value="${value}"
									${value == task.status ? "selected" : ""}
								>
									${status}
								</option>`).join("")
							}
						</select>
					</td>
					<td class="task-type">
						<select value="${task.type}" disabled>
							${Object.entries(JSON.parse(types)).map(([value, type]) =>
								`<option
									value="${value}"
									${value == task.type ? "selected" : ""}
								>
									${type}
								</option>`).join("")
							}
						</select>

					</td>
					<td class="task-category">
							<select value="${task.category_id}" disabled>
							${JSON.parse(categories).map((category) => `
								<option
									value="${category.id}"
									${category.id == task.category_id ? "selected" : ""}
								>
									${category.name}
								</option>
							`)}
							</select>
					</td>
					<td>
							<button onclick="enableEdit(${task.id})">Edit</button>
							<button class="save-button" onclick="saveEdit(${task.id})" style="display: none;">Save</button>
							<button class="cancel-button" onclick="cancelEdit(${task.id})" style="display: none;">Cancel</button>
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
	const nameInput = row.querySelector(".task-title input");
	const descriptionInput = row.querySelector(".task-description textarea");
	const statusInput = row.querySelector(".task-status select");
	const typeInput = row.querySelector(".task-type select");
	const categoryInput = row.querySelector(".task-category select");

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

	row.children[5].children[0].style.display = "none";
	row.children[5].children[1].style.display = "inline-block";
	row.children[5].children[2].style.display = "inline-block";
}

// Save the updated task
window.saveEdit = async (taskId) => {
	const row = document.querySelector(`#task-row-${taskId}`);
	const nameInput = row.querySelector(".task-title input");
	const descriptionInput = row.querySelector(".task-description textarea");
	const statusInput = row.querySelector(".task-status select");
	const typeInput = row.querySelector(".task-type select");
	const categoryInput = row.querySelector(".task-category select");


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

			row.querySelector(".task-title input").value = updatedName;
			row.querySelector(".task-description textarea").value = updatedDescription;
			row.querySelector(".task-status select").value = updatedStatus;
			row.querySelector(".task-type select").value = updatedType;
			row.querySelector(".task-category select").value = updatedCategory;

			// Make cells disabled
			nameInput.disabled = true;
			descriptionInput.disabled = true;
			statusInput.disabled = true;
			typeInput.disabled = true;
			categoryInput.disabled = true;

			resetRow(row);
	} catch (error) {
			console.error("Error updating task:", error);
			alert("An error occurred while updating the task.");
	}
}

	window.cancelEdit = async (taskId) =>  {
		const row = document.querySelector(`#task-row-${taskId}`);
		const nameInput = row.querySelector(".task-title input");
		const descriptionInput = row.querySelector(".task-description textarea");
		const statusInput = row.querySelector(".task-status select");
		const typeInput = row.querySelector(".task-type select");
		const categoryInput = row.querySelector(".task-category select");

		// Restore original values
		nameInput.value = nameInput.dataset.originalValue;
		descriptionInput.value = descriptionInput.dataset.originalValue;
		statusInput.value = statusInput.dataset.originalValue;
		typeInput.value = typeInput.dataset.originalValue;
		categoryInput.value = categoryInput.dataset.originalValue;

		// Make cells disabled
		nameInput.disabled = true;
		descriptionInput.disabled = true;
		statusInput.disabled = true;
		typeInput.disabled = true;
		categoryInput.disabled = true;

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

