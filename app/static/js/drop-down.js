const yourBooksArray = [
  "History Grade11",
  "History Grade10",
  "History Grade9"
];

const STORAGE_KEY = "user_added_books";

const savedBooks = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];

const books = [...yourBooksArray, ...savedBooks];

// Assuming you have your own books array somewhere else:
const nameSpaceInput = document.getElementById("index");
const dropdown = document.getElementById("dropdown");

function saveBook(newBook) {
  if (!books.includes(newBook)) {
    books.push(newBook);
    savedBooks.push(newBook);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(savedBooks));
  }
}

nameSpaceInput.addEventListener("input", () => {
  const value = nameSpaceInput.value.trim();
  const lowerValue = value.toLowerCase();
  dropdown.innerHTML = "";

  if (value === "") {
    dropdown.style.display = "none";
    return;
  }

  const filtered = books.filter(book => book.toLowerCase().includes(lowerValue));
  const maxItems = 5;
  const itemsToShow = filtered.slice(0, maxItems);

  itemsToShow.forEach(book => {
    const item = document.createElement("div");
    item.className = "dropdown-item";
    item.textContent = book;
    item.onclick = () => {
      nameSpaceInput.value = book;
      dropdown.style.display = "none";
    };
    dropdown.appendChild(item);
  });

  const exactMatch = books.some(book => book.toLowerCase() === lowerValue);

  if (!exactMatch) {
    const addItem = document.createElement("div");
    addItem.className = "dropdown-item add-new";
    addItem.style.fontWeight = "bold";
    addItem.style.display = "inline-flex";
    addItem.style.alignItems = "center";
    addItem.style.justifyContent = "center";
    // addItem.style.gap = "6px";
    // addItem.style.color = "#4caf50";

    const plusIcon = document.createElement("span");
    plusIcon.textContent = "+";
    plusIcon.style.fontWeight = "bold";
    plusIcon.style.fontSize = "16px";

    addItem.appendChild(plusIcon);
    addItem.appendChild(document.createTextNode(`Add book name "${value}"`));

    addItem.onclick = () => {
      nameSpaceInput.value = value;
      dropdown.style.display = "none";
      saveBook(value);
      console.log(`Saved new book: ${value}`);
    };

    dropdown.appendChild(addItem);
  }

  dropdown.style.display = (itemsToShow.length > 0 || !exactMatch) ? "block" : "none";
});

document.addEventListener("click", (e) => {
  if (!e.target.closest(".dropdown-container")) {
    dropdown.style.display = "none";
  }
});
