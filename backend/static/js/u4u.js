const tasks = document.querySelectorAll('.task');
const tables = document.querySelectorAll('.table');

tasks.forEach(task => {
    task.addEventListener('dragstart', (event) => {
        event.dataTransfer.setData('text/plain', task.new_place);
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

        const newPlace = event.dataTransfer.getData('text/plain');
        const draggedTaskElement = document.getElementsByName(newPlace)[0];
				const draggedTaskId = draggedTaskElement.id;
        if (!draggedTaskElement) {
            console.error("Dragged task element not found");
            return;
        }

        const targetColumn = event.target.closest('.column');
        if (!targetColumn) {
            console.error("Target column not found");
            return;
        }
				console.log(draggedTaskId);

				console.log(targetColumn);
				console.log(table);



        if (targetColumn.parentNode.parentNode === table) {
            targetColumn.appendChild(draggedTaskElement);

            // Extract the new status from the column's ID
            const newStatus = targetColumn.id.split('-')[1];
						console.log(newStatus);

            updateTaskStatus(newPlace.split('-')[1], newStatus); // Pass task ID without "task-" prefix
        }
    });
});

function updateTaskStatus(taskId, newStatus) {
    fetch(`/api/u4u/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            newStatus: newStatus
        })
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
