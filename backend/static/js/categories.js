
const apiBase = "/api/u4u/categories";
async function fetchCategories() {
	const response = await fetch(`${apiBase}/list`);
	const data = await response.json();
	categoriesList.innerHTML = "";
	editCategoryId.innerHTML = "";

	data.forEach(category => {
			const li = document.createElement("li");
			li.innerHTML = `<span>${category.name}</span> <span style="color:${category.color}">●</span>`;

			const deleteButton = document.createElement("button");
			deleteButton.textContent = "Delete";
			deleteButton.addEventListener("click", async () => {
					if (confirm(`Are you sure you want to delete "${category.name}"?`)) {
							await fetch(`${apiBase}/${category.id}`, { method: "DELETE" });
							alert("Category deleted!");
							fetchCategories();
					}
			});

			li.appendChild(deleteButton);
			categoriesList.appendChild(li);

			const option = document.createElement("option");
			option.value = category.id;
			option.textContent = category.name;
			editCategoryId.appendChild(option);
	});
}

document.getElementById("create-category-form").addEventListener("submit", async (e) => {
	e.preventDefault();
	const name = document.getElementById("new-category-name").value;
	const color = document.getElementById("new-category-color").value;
	await fetch(apiBase, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ name, color })
	});
	alert("Category created!");
	fetchCategories();
});

document.getElementById("edit-category-form").addEventListener("submit", async (e) => {
	e.preventDefault();
	const id = editCategoryId.value;
	const name = document.getElementById("edit-category-name").value;
	const color = document.getElementById("edit-category-color").value;
	await fetch(`${apiBase}/${id}`, {
			method: "PUT",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ name, color })
	});
	alert("Category updated!");
	fetchCategories();
});

fetchCategories();
