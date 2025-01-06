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

async function updateTaskStatus(taskId, newStatus) {
  await fetch(`${u4uURL}/tasks/${taskId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus }),
  });
}


// modal
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('task-modal');
  const closeModal = document.getElementById('close-modal');
  const saveTaskButton = document.getElementById('save-task');
  const cancelTaskButton = document.getElementById('cancel-task');
  const taskForm = document.getElementById('task-form');

  const taskElements = document.querySelectorAll('.task');
  const taskElementsMap = {};
  taskElements.forEach((taskElement) => {
      taskElementsMap[taskElement.id.split('-')[1]] = taskElement;
  });

  const taskDetailsCache = {};
  const fetchTaskDetails = (taskId) =>
    taskDetailsCache[taskId] ||
    (async () => {
      const response = await fetch(`${u4uURL}/tasks/${taskId}`);
      const task = await response.json();
      taskDetailsCache[taskId] = task;
      return task;
    })();
  document.body.addEventListener('click', (event) => {
    const taskId = event.target.closest('.task')?.id.split('-')[1];
    if (taskId && taskElementsMap[taskId]) {
      fetchTaskDetails(taskId).then((task) => {
        modal.dataset.taskId = task.id;
        const fields = ['title', 'description', 'status', 'result'];
        for (let index = 0; index < fields.length; index++) {
          const fieldName = fields[index];
          taskForm.children[fieldName].value = task[fieldName];

        }
        modal.classList.remove('hidden');
      });
    }
  });

  // Закриття модального вікна (кнопка "Закрити")
  cancelTaskButton.addEventListener('click', () => {
      modal.classList.add('hidden');
  });

  closeModal.addEventListener('click', () => {
      modal.classList.add('hidden');
  });

  saveTaskButton.addEventListener('click', async () => {
      const taskId = modal.dataset.taskId;
      const taskForm = document.getElementById('task-form');
      const formData = new FormData(taskForm);
      const updatedTask = {
          title: formData.get('title'),
          description: formData.get('description'),
          status: formData.get('status'),
          result: formData.get('result'),
      };

      try {
          const response = await fetch(`${u4uURL}/tasks/${taskId}`, {
              method: 'PUT',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(updatedTask),
          });

          if (!response.ok) throw new Error('Failed to save task');

          modal.classList.add('hidden');
          location.reload(); // Refresh the page to update tasks
      } catch (error) {
          console.error('Error updating task:', error);
      }
  });

});
