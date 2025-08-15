const yourBooksArray = [
  "Physics_Grade10",
  "Biology_Grade11",
  "Chemistry_Grade9",
  "History Grade10",
  "Buddhism_Grade8",
  "Buddhism Grade9",
  "Buddhism Grade7",
  "Buddhism Grade10",
  "Buddhism Grade 12",
];

const STORAGE_KEY = "user_added_books";

const savedBooks = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];

const books = [...yourBooksArray, ...savedBooks];

const nameSpaceInput = document.getElementById("index");
const deleteNameSpace = document.getElementById("namespace-delete");
const deleteDropdown = document.getElementById("dropdown-2")
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

deleteNameSpace.addEventListener("input", () => {
  const value = deleteNameSpace.value.trim();
  const lowerValue = value.toLowerCase();
  deleteDropdown.innerHTML = "";

  if (value === "") {
    deleteDropdown.style.display = "none";
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
      deleteNameSpace.value = book;
      deleteDropdown.style.display = "none";
    };
    deleteDropdown.appendChild(item);
  });

  const exactMatch = books.some(book => book.toLowerCase() === lowerValue);

  // if (!exactMatch) {
  //   const addItem = document.createElement("div");
  //   addItem.className = "dropdown-item add-new";
  //   addItem.style.fontWeight = "bold";
  //   addItem.style.display = "inline-flex";
  //   addItem.style.alignItems = "center";
  //   addItem.style.justifyContent = "center";
  //   // addItem.style.gap = "6px";
  //   // addItem.style.color = "#4caf50";

  //   const plusIcon = document.createElement("span");
  //   plusIcon.textContent = "+";
  //   plusIcon.style.fontWeight = "bold";
  //   plusIcon.style.fontSize = "16px";

  //   addItem.appendChild(plusIcon);
  //   addItem.appendChild(document.createTextNode(`Add book name "${value}"`));

  //   addItem.onclick = () => {
  //     deleteNameSpace.value = value;
  //     dropdown.style.display = "none";
  //     saveBook(value);
  //     console.log(`Saved new book: ${value}`);
  //   };

  //   dropdown.appendChild(addItem);
  // }
  
  deleteDropdown.style.display = (itemsToShow.length > 0 || !exactMatch) ? "block" : "none";
});

document.addEventListener("click", (e) => {
  if (!e.target.closest(".dropdown-container")) {
    dropdown.style.display = "none";
  }
});
