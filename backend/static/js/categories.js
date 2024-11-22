document.addEventListener("DOMContentLoaded", () => {
	const addCategoryForm = document.getElementById("add-category-form");
	if (addCategoryForm) {
			addCategoryForm.addEventListener("submit", async (event) => {
					event.preventDefault();

					const formData = new FormData(addCategoryForm);
					const name = formData.get("name");
					const color = formData.get("color");

					if (!name || !color) {
							alert("Please provide both a name and a color.");
							return;
					}

					try {
							const response = await fetch("/categories", {
									method: "POST",
									headers: {
											"Content-Type": "application/json",
									},
									body: JSON.stringify({ name, color }),
							});

							if (!response.ok) {
									const error = await response.json();
									alert(`Error: ${error.detail}`);
									return;
							}

							alert("Category added successfully!");
							location.reload(); // Refresh to display the new category
					} catch (error) {
							console.error("Error adding category:", error);
							alert("An error occurred while adding the category.");
					}
			});
	}
});

// Enable editing for a category row
function enableEdit(categoryId) {
	const row = document.querySelector(`#category-row-${categoryId}`);
	const nameCell = row.querySelector(".category-name");
	const colorCell = row.querySelector(".category-color");

	// Store the current values in data attributes in case of cancel
	nameCell.dataset.originalValue = nameCell.textContent.trim();
	colorCell.dataset.originalValue = colorCell.textContent.trim();

	// Make cells editable
	nameCell.innerHTML = `<input type="text" value="${nameCell.textContent.trim()}" class="edit-input" />`;
	colorCell.innerHTML = `<input type="color" value="${colorCell.textContent.trim()}" class="edit-input" />`;

	// Show save and cancel buttons, hide edit button
	row.querySelector(".edit-button").style.display = "none";
	row.querySelector(".save-button").style.display = "inline-block";
	row.querySelector(".cancel-button").style.display = "inline-block";
}

// Save the updated category
async function saveEdit(categoryId) {
	const row = document.querySelector(`#category-row-${categoryId}`);
	const nameInput = row.querySelector(".category-name input");
	const colorInput = row.querySelector(".category-color input");

	const updatedName = nameInput.value.trim();
	const updatedColor = colorInput.value.trim();

	if (!updatedName || !updatedColor) {
			alert("Both name and color are required.");
			return;
	}

	try {
			const response = await fetch(`/categories/${categoryId}`, {
					method: "PUT",
					headers: {
							"Content-Type": "application/json",
					},
					body: JSON.stringify({ name: updatedName, color: updatedColor }),
			});

			if (!response.ok) {
					const error = await response.json();
					alert(`Error: ${error.detail}`);
					return;
			}

			alert("Category updated successfully!");

			// Update the row with new values and reset buttons
			row.querySelector(".category-name").textContent = updatedName;
			row.querySelector(".category-color").textContent = updatedColor;

			resetRow(row);
	} catch (error) {
			console.error("Error updating category:", error);
			alert("An error occurred while updating the category.");
	}
}

// Cancel editing and restore original values
function cancelEdit(categoryId) {
	const row = document.querySelector(`#category-row-${categoryId}`);
	const nameCell = row.querySelector(".category-name");
	const colorCell = row.querySelector(".category-color");

	// Restore original values
	nameCell.textContent = nameCell.dataset.originalValue;
	colorCell.textContent = colorCell.dataset.originalValue;

	resetRow(row);
}

// Reset row buttons after editing
function resetRow(row) {
	row.querySelector(".edit-button").style.display = "inline-block";
	row.querySelector(".save-button").style.display = "none";
	row.querySelector(".cancel-button").style.display = "none";
}
