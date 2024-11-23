// Приклад з використанням чистого JavaScript (без фреймворків)

const tasks = document.querySelectorAll('.task');
const tables = document.querySelectorAll('.table');

tasks.forEach(task => {
  task.addEventListener('dragstart', (event) => {
    event.dataTransfer.setData('text/plain', task.id);
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
    const targetColumn = event.target.closest('.column');
    const draggedTaskId = event.dataTransfer.getData('text/plain');
    const draggedTaskElement = document.getElementById(draggedTaskId);

    if (targetColumn && targetColumn.parentNode.parentNode === table) {
      targetColumn.appendChild(draggedTaskElement);

      // Оновити статус завдання на сервері
      const newStatus = targetColumn.id.split('-')[1];
      updateTaskStatus(draggedTaskId, newStatus);
    }
  });
});

function updateTaskStatus(taskId, newStatus) {
  // Замінити URL на ваш реальний URL сервера
  fetch('/api/update_task_status', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      taskId: taskId,
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
    // Оновити інтерфейс, якщо необхідно
  })
  .catch(error => {
    console.error('Error updating task:', error);
    // Показати користувачеві повідомлення про помилку
  });
}
