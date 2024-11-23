document.addEventListener("DOMContentLoaded", () => {
	const taskLists = document.querySelectorAll(".task-list");

	let draggedTask = null;

	taskLists.forEach((list) => {
			list.addEventListener("dragstart", (event) => {
					draggedTask = event.target;
					event.dataTransfer.effectAllowed = "move";
			});

			list.addEventListener("dragover", (event) => {
					event.preventDefault(); // Allow drop
					event.dataTransfer.dropEffect = "move";
			});

			list.addEventListener("drop", async (event) => {
					event.preventDefault();

					const targetList = event.currentTarget;

					// Ensure the task is dropped within the same table
					if (draggedTask && draggedTask.parentNode !== targetList) {
							const sourceTable = draggedTask.closest(".table");
							const targetTable = targetList.closest(".table");

							if (sourceTable.id === targetTable.id) {
									// Move the task
									targetList.appendChild(draggedTask);

									// Update task's status in the database
									const taskId = draggedTask.dataset.taskId;
									const newStatus = targetList.dataset.status;

									try {
											await updateTaskStatus(taskId, newStatus);
											alert(`Task status updated to: ${newStatus}`);
									} catch (error) {
											console.error("Error updating task status:", error);
											alert("Failed to update task status.");
									}
							} else {
									alert("Tasks can only be moved within the same table.");
							}
					}

					draggedTask = null;
			});
	});
});

// Update task status in the database
async function updateTaskStatus(taskId, newStatus) {
	const response = await fetch(`/api/u4u/tasks/${taskId}`, {
			method: "PUT",
			headers: {
					"Content-Type": "application/json",
			},
			body: JSON.stringify({ status: newStatus }),
	});

	if (!response.ok) {
			throw new Error(`Failed to update task status: ${response.status}`);
	}

	return response.json();
}
