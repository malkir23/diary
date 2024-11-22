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

	let draggedTask = null;

	function handleDragStart(e) {
			draggedTask = e.target;
			setTimeout(() => {
					draggedTask.classList.add("hidden");
			}, 0);
	}

	function handleDragEnd() {
			draggedTask.classList.remove("hidden");
			draggedTask = null;
	}

	function handleDragOver(e) {
			e.preventDefault();
	}

	function handleDrop(e) {
			e.preventDefault();
			const targetList = e.target.closest(".task-list");
			if (targetList && targetList !== draggedTask.parentElement) {
					targetList.appendChild(draggedTask);
			}
	}
});
