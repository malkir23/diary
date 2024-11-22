document.addEventListener("DOMContentLoaded", () => {
	const tasks = document.querySelectorAll(".task");
	const taskLists = document.querySelectorAll(".task-list");

	tasks.forEach(task => {
			task.addEventListener("dragstart", handleDragStart);
			task.addEventListener("dragend", handleDragEnd);
	});

	taskLists.forEach(list => {
			list.addEventListener("dragover", handleDragOver);
			list.addEventListener("drop", handleDrop);
	});

	function handleDragStart(e) {
			e.dataTransfer.setData("text/plain", e.target.id);
			setTimeout(() => {
					e.target.classList.add("hidden");
			}, 0);
	}

	function handleDragEnd(e) {
			e.target.classList.remove("hidden");
	}

	function handleDragOver(e) {
			e.preventDefault();
	}

	function handleDrop(e) {
			e.preventDefault();
			const taskId = e.dataTransfer.getData("text/plain");
			const task = document.getElementById(taskId);
			e.target.appendChild(task);
	}
});
