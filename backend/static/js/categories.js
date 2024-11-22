document.addEventListener("DOMContentLoaded", function () {
	const apiBase = "/categories";
	const categoriesList = document.getElementById("categories-list");
	const editCategoryId = document.getElementById("edit-category-id");

	// Fetch and display categories
	async function fetchCategories() {
			const response = await fetch(apiBase);
			const data = await response.json();
			categoriesList.innerHTML = "";
			editCategoryId.innerHTML = "";

			data.categories.forEach(category => {
					// Display in the list
					const li = document.createElement("li");
					li.textContent = category.name;

					// Add delete button
					const deleteButton = document.createElement("button");
					deleteButton.textContent = "Delete";
					deleteButton.style.marginLeft = "10px";
					deleteButton.addEventListener("click", async () => {
							if (confirm(`Are you sure you want to delete "${category.name}"?`)) {
									await fetch(`${apiBase}/${category.id}`, { method: "DELETE" });
									alert("Category deleted!");
									fetchCategories();
							}
					});

					li.appendChild(deleteButton);
					categoriesList.appendChild(li);

					// Populate the dropdown
					const option = document.createElement("option");
					option.value = category.id;
					option.textContent = category.name;
					editCategoryId.appendChild(option);
			});
	}

	// Create category
	document.getElementById("create-category-form").addEventListener("submit", async (e) => {
			e.preventDefault();
			const name = document.getElementById("new-category-name").value;
			const response = await fetch(apiBase, {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ name })
			});
			if (response.ok) {
					alert("Category created!");
					fetchCategories();
			} else {
					alert("Failed to create category.");
			}
	});

	// Update category
	document.getElementById("edit-category-form").addEventListener("submit", async (e) => {
			e.preventDefault();
			const id = editCategoryId.value;
			const name = document.getElementById("edit-category-name").value;
			const response = await fetch(`${apiBase}/${id}`, {
					method: "PUT",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ name })
			});
			if (response.ok) {
					alert("Category updated!");
					fetchCategories();
			} else {
					alert("Failed to update category.");
			}
	});

	// Initial fetch
	fetchCategories();
});
