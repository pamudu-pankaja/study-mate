const books = [
    "Physics_Grade10",
    "Biology_Grade11",
    "Chemistry_Grade9",
    "History Grade10",
    "Buddhism_Grade8",
    "Buddhism Grade9",
    "Buddhism Grade7",
    "Buddhism Grade10",
    "Buddhism Grade 12"
];

const nameSpaceinput = document.getElementById("index");
const dropdown = document.getElementById("dropdown");

nameSpaceinput.addEventListener("input", () => {
    const value = nameSpaceinput.value.toLowerCase();
    dropdown.innerHTML = "";
    const filtered = books.filter(book => book.toLowerCase().includes(value));
    if (filtered.length && value !== "") {
    dropdown.style.display = "block";
    filtered.forEach(book => {
        const item = document.createElement("div");
        item.className = "dropdown-item";
        item.textContent = book;
        item.onclick = () => {
        nameSpaceinput.value = book;
        dropdown.style.display = "none";
        };
        dropdown.appendChild(item);
    });
    } else {
    dropdown.style.display = "none";
    }
});

document.addEventListener("click", (e) => {
    if (!e.target.closest(".dropdown-container")) {
    dropdown.style.display = "none";
    }
});