// Allow drop action on the drop zone
function allowDrop(event) {
	event.preventDefault();
}

// Start dragging an element
function drag(event) {
	event.dataTransfer.setData("text", event.target.id);
}

// Handle drop action
function drop(event) {
	event.preventDefault();
	const taskId = event.dataTransfer.getData("text");
	const task = document.getElementById(taskId);
	event.target.appendChild(task);
}
