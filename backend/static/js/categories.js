document.addEventListener("DOMContentLoaded", () => {
	// Add an event listener to handle form submission for adding a category
	// Function to delete a category
	const categoriesURL = '/api/u4u/categories'
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
							const response = await fetch(categoriesURL, {
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

// Function to delete a category
async function deleteCategory(categoryId) {
	if (!confirm("Are you sure you want to delete this category?")) return;

	try {
			const response = await fetch(`${categoriesURL}/${categoryId}`, {
					method: "DELETE",
			});

			if (!response.ok) {
					const error = await response.json();
					alert(`Error: ${error.detail}`);
					return;
			}

			alert("Category deleted successfully");
			location.reload(); // Refresh the page to update the table
	} catch (error) {
			console.error("Error deleting category:", error);
			alert("An error occurred while deleting the category.");
	}
}

// Function to edit a category
async function editCategory(categoryId) {
	const newName = prompt("Enter the new name for the category:");
	const newColor = prompt("Enter the new color for the category (e.g., #ff0000):");

	if (!newName || !newColor) {
			alert("Both name and color are required to update the category.");
			return;
	}

	try {
			const response = await fetch(`${categoriesURL}/${categoryId}`, {
					method: "PUT",
					headers: {
							"Content-Type": "application/json",
					},
					body: JSON.stringify({ name: newName, color: newColor }),
			});

			if (!response.ok) {
					const error = await response.json();
					alert(`Error: ${error.detail}`);
					return;
			}

			alert("Category updated successfully");
			location.reload(); // Refresh the page to update the table
	} catch (error) {
			console.error("Error updating category:", error);
			alert("An error occurred while updating the category.");
	}
}
