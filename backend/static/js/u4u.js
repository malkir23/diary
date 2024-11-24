const tasks = document.querySelectorAll('.task');
const tables = document.querySelectorAll('.table');
let draggedTask = null; // For mobile compatibility
let startColumn = null; // Track start column for validation

// Desktop Drag-and-Drop Events
tasks.forEach((task) => {
  // Start dragging
  task.addEventListener('dragstart', (event) => {
    event.dataTransfer.setData('text/plain', task.id);
    event.dataTransfer.setData('text/table', task.closest('.table').id);
    draggedTask = task;
    startColumn = task.closest('.column');
    task.classList.add('dragging');
  });

  // End dragging
  task.addEventListener('dragend', () => {
    draggedTask = null;
    startColumn = null;
    task.classList.remove('dragging');
  });
});

tables.forEach((table) => {
  // Allow dropping in valid areas
  table.addEventListener('dragover', (event) => {
    event.preventDefault();
    const targetColumn = event.target.closest('.column');
    if (targetColumn && targetColumn.parentNode.parentNode === table) {
      event.dataTransfer.dropEffect = 'move';
    } else {
      event.dataTransfer.dropEffect = 'none';
    }
  });

  // Handle drop event
  table.addEventListener('drop', (event) => {
    event.preventDefault();

    const draggedTaskId = event.dataTransfer.getData('text/plain');
    const tableId = event.dataTransfer.getData('text/table');
    const currentTableId = table.getAttribute('id');
    const draggedTaskElement = document.getElementById(draggedTaskId);

    if (!draggedTaskElement) {
      console.error('Dragged task element not found');
      return;
    }

    const targetColumn = event.target.closest('.column');
    if (!targetColumn) {
      console.error('Target column not found');
      return;
    }

    if (currentTableId === tableId) {
      targetColumn.appendChild(draggedTaskElement);

      // Extract the new status from the column's ID
      const newStatus = targetColumn.id
        .replace(`${currentTableId}-`, '')
        .replace('-', '_');

      updateTaskStatus(draggedTaskId.split('-')[1], newStatus); // Pass task ID without "task-" prefix
    }
  });
});

// Mobile Touch Events
tasks.forEach((task) => {
  task.addEventListener('touchstart', (event) => {
    draggedTask = task;
    startColumn = task.closest('.column');
    task.classList.add('dragging');
  });

  task.addEventListener('touchmove', (event) => {
    const touch = event.touches[0];
    const elementUnderTouch = document.elementFromPoint(touch.clientX, touch.clientY);

    tables.forEach((table) => {
      const targetColumn = elementUnderTouch?.closest('.column');
      if (targetColumn && targetColumn.parentNode.parentNode === table) {
        targetColumn.classList.add('highlight');
      } else {
        table.querySelectorAll('.column').forEach((column) =>
          column.classList.remove('highlight')
        );
      }
    });
  });

  task.addEventListener('touchend', (event) => {
    const touch = event.changedTouches[0];
    const elementUnderTouch = document.elementFromPoint(touch.clientX, touch.clientY);
    const targetColumn = elementUnderTouch?.closest('.column');

    tables.forEach((table) => {
      table.querySelectorAll('.column').forEach((column) =>
        column.classList.remove('highlight')
      );
    });

    if (targetColumn && draggedTask) {
      targetColumn.appendChild(draggedTask);

      // Extract the new status from the column's ID
      const newStatus = targetColumn.id
        .replace(`${table.id}-`, '')
        .replace('-', '_');

      updateTaskStatus(draggedTask.id.split('-')[1], newStatus);
    }

    draggedTask.classList.remove('dragging');
    draggedTask = null;
    startColumn = null;
  });
});

// Function to update task status in the database
function updateTaskStatus(taskId, newStatus) {
  fetch(`/api/u4u/tasks/${taskId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ status: newStatus }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then((data) => {
      console.log('Task updated successfully:', data);
    })
    .catch((error) => {
      console.error('Error updating task:', error);
    });
}
