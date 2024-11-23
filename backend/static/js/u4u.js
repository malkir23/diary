const tasks = document.querySelectorAll('.task');
const tables = document.querySelectorAll('.table');

tasks.forEach(task => {
    task.addEventListener('dragstart', (event) => {
        event.dataTransfer.setData('text/plain', task.id);
				event.dataTransfer.setData('text/table', task.closest('.table').id);
    });
});

tables.forEach(table => {
    table.addEventListener('dragover', (event) => {
        event.preventDefault();
        const targetColumn = event.target.closest('.column');
        if (targetColumn && targetColumn.parentNode.parentNode === table) {
            event.dataTransfer.dropEffect = 'move';
        } else {
            event.dataTransfer.dropEffect = 'none';
        }
    });

    table.addEventListener('drop', (event) => {
        event.preventDefault();

        const draggedTaskId = event.dataTransfer.getData('text/plain');
				const tableId = event.dataTransfer.getData('text/table');
				const currentTableId = table.getAttribute('id');
        const draggedTaskElement = document.getElementById(draggedTaskId);
        if (!draggedTaskElement) {
            console.error("Dragged task element not found");
            return;
        }

        const targetColumn = event.target.closest('.column');
        if (!targetColumn) {
            console.error("Target column not found");
            return;
        }
				console.log(draggedTaskElement);

				console.log(targetColumn);
				console.log(table);



        if (currentTableId === tableId) {
            targetColumn.appendChild(draggedTaskElement);

            // Extract the new status from the column's ID
            const newStatus = targetColumn.id.replace(`${currentTableId}-`, '').replace('-', '_');
						console.log(newStatus);

            updateTaskStatus(draggedTaskId.split('-')[1], newStatus); // Pass task ID without "task-" prefix
        }
    });
});

function updateTaskStatus(taskId, newStatus) {
	console.log(taskId, newStatus);

    fetch(`/api/u4u/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Task updated successfully:', data);
    })
    .catch(error => {
        console.error('Error updating task:', error);
    });
}
