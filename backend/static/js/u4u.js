// u4u.js

document.addEventListener('DOMContentLoaded', () => {
  const tables = document.querySelectorAll('.table');

  // Drag and Drop Functionality
  tables.forEach(table => {
    table.addEventListener('dragover', (event) => {
      event.preventDefault();
    });

    table.addEventListener('drop', (event) => {
      event.preventDefault();
      const targetColumn = event.target.closest('.column');
      const draggedTask = event.dataTransfer.getData('text/plain');
      const draggedTaskElement = document.getElementById(draggedTask);

      if (targetColumn) {
        targetColumn.appendChild(draggedTaskElement);

        // Update database here (using AJAX or Fetch API)
        const taskId = draggedTaskElement.dataset.taskId;
        const newStatus = targetColumn.id.split('-')[1];
        const newParentId = targetColumn.parentNode.parentNode.id;

        fetch(`/api/u4u/tasks/${taskId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            taskId: taskId,
            newStatus: newStatus,
            newParentId: newParentId
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
          // Handle success or error messages as needed
        })
        .catch(error => {
          console.error('Error updating task:', error);
          // Handle errors gracefully, e.g., display error message to user
        });
      }
    });

    table.querySelectorAll('.task').forEach(task => {
      task.addEventListener('dragstart', (event) => {
        event.dataTransfer.setData('text/plain', task.id);
      });
    });
  });
});
