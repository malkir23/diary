const tasks = document.querySelectorAll('.task');
const tables = document.querySelectorAll('.table');
const u4uURL = '/api/u4u';

tasks.forEach((task) => {
  task.addEventListener('dragstart', (event) => {
    event.dataTransfer.setData('text/plain', task.id);
    event.dataTransfer.setData('text/table', task.closest('.table').id);
  });
});

tables.forEach((table) => {
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

function updateTaskStatus(taskId, newStatus) {
  fetch(`${u4uURL}/tasks/${taskId}`, {
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


// modal
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('task-modal');
  const closeModal = document.getElementById('close-modal');
  const saveTaskButton = document.getElementById('save-task');
  const taskForm = document.getElementById('task-form');

  document.querySelectorAll('.task').forEach((taskElement) => {
      taskElement.addEventListener('click', () => {
          const taskId = taskElement.id.split('-')[1];

          // Fetch task details from API
          fetch(`${u4uURL}/tasks/${taskId}`)
              .then((response) => response.json())
              .then((task) => {
                  document.getElementById('task-title').value = task.title;
                  document.getElementById('task-description').value = task.description;
                  document.getElementById('task-status').value = task.status;
                  document.getElementById('task-result').value = task.result;
                  modal.dataset.taskId = task.id;
                  modal.classList.remove('hidden');
              })
              .catch((error) => console.error('Error fetching task:', error));
      });
  });

  closeModal.addEventListener('click', () => {
      modal.classList.add('hidden');
  });

  saveTaskButton.addEventListener('click', () => {
      const taskId = modal.dataset.taskId;
      const updatedTask = {
          title: document.getElementById('task-title').value,
          description: document.getElementById('task-description').value,
          status: document.getElementById('task-status').value,
          result: document.getElementById('task-result').value,
      };

      fetch(`${u4uURL}/tasks/${taskId}`, {
          method: 'PUT',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(updatedTask),
      })
          .then((response) => {
              if (!response.ok) throw new Error('Failed to save task');
              return response.json();
          })
          .then(() => {
              modal.classList.add('hidden');
              location.reload(); // Refresh the page to update tasks
          })
          .catch((error) => console.error('Error updating task:', error));
  });
});
