const nameSpaceInput = document.getElementById("book");
const deleteNameSpace = document.getElementById("namespace-delete");
const deleteDropdown = document.getElementById("dropdown-2");
const dropdown = document.getElementById("dropdown");

let allBooks = [];

let chatID = window.conversation_id;
const API_BASE = chatID
  ? `${url_prefix}/chat/${chatID}/books`
  : `${url_prefix}/chat/books`;

async function fetchBooks() {
  try {
    const response = await fetch(`${API_BASE}/list`);
    if (!response.ok) showError("Faild to Fetch Books", "We faild to fetch the books from the server. Please consider reloading the site")

    const data = await response.json();
    allBooks = [...data.systemBooks, ...data.userBooks];
    console.log('Books loaded:', allBooks.length);
  } catch (error) {
    console.error('Error fetching books:', error);
    allBooks = [];
  }
}

async function saveBook(bookName) {
  try {
    const response = await fetch(`${API_BASE}/add`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ bookName: bookName.trim() })
    });

    if (!response.ok) showError('Book Not Saved', `Your book "${bookName}" has not been saved , Please Try again`);

    const result = await response.json();
    if (result.success) {
      if (!allBooks.includes(bookName)) {
        allBooks.push(bookName);
      }
      showSuccess("Book Saved", `Your book "${bookName}" has been saved successfully`)
      showInfo("Import New Files", "You can import new files for your book using Import PDF File section")
      console.log(`Book "${bookName}" saved successfully`);
      return true;
    }
    return false;
  } catch (error) {
    showError('Book Not Saved', `Error : ${error}`)
    console.error('Error saving book:', error);
    return false;
  }
}

async function deleteBook(bookName) {
  try {
    const response = await fetch(`${API_BASE}/delete`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ bookName: bookName.trim() })
    });

    if (!response.ok) showError("Faild to Delete", `Book "${bookName}" has been faild to delete please try again`);

    const result = await response.json();
    if (result.success) {
      const index = allBooks.indexOf(bookName);
      if (index > -1) {
        allBooks.splice(index, 1);
      }
      showSuccess("Book Deleted", `Book name "${bookName}" has been deleted successfully`)
      console.log(`Book "${bookName}" deleted successfully`);
      return true;
    } else {
      showWarning("Warning", `${result.message || "Cannot delete book"}`)
      console.warn(result.message || 'Cannot delete book');
      return false;
    }
  } catch (error) {
    showError('Failed to delete', `Error : ${error}`)
    console.error('Error deleting book:', error);
    return false;
  }
}

function createDropdown(inputElement, dropdownElement, showAddOption = false, showDeleteOption = false) {
  inputElement.addEventListener("input", () => {
    const value = inputElement.value.trim();
    const lowerValue = value.toLowerCase();
    dropdownElement.innerHTML = "";

    if (value === "") {
      dropdownElement.style.display = "none";
      return;
    }

    const filtered = allBooks.filter(book =>
      book.toLowerCase().includes(lowerValue)
    );
    const maxItems = 5;
    const itemsToShow = filtered.slice(0, maxItems);

    itemsToShow.forEach(book => {
      const item = document.createElement("div");
      item.className = "dropdown-item";
      item.textContent = book;
      item.onclick = () => {
        inputElement.value = book;
        dropdownElement.style.display = "none";
      };
      dropdownElement.appendChild(item);
    });

    const exactMatch = allBooks.some(book =>
      book.toLowerCase() === lowerValue
    );

    if (showAddOption && !exactMatch && value.length > 0) {
      const addItem = document.createElement("div");
      addItem.className = "dropdown-item add-new";
      addItem.style.fontWeight = "bold";
      addItem.style.display = "flex";
      addItem.style.alignItems = "center";
      addItem.style.gap = "6px";
      addItem.style.color = "#4caf50";

      const plusIcon = document.createElement("span");
      plusIcon.textContent = "+";
      plusIcon.style.fontWeight = "bold";
      plusIcon.style.fontSize = "16px";

      addItem.appendChild(plusIcon);
      addItem.appendChild(document.createTextNode(`Add book "${value}"`));

      addItem.onclick = async () => {
        const success = await saveBook(value);
        if (success) {
          inputElement.value = value;
          dropdownElement.style.display = "none";
        } else {
          showError('Book Not Saved', `Failed to save the book, Please Try again`);
        }
      };

      dropdownElement.appendChild(addItem);
    }

    dropdownElement.style.display =
      (itemsToShow.length > 0 || (showAddOption && !exactMatch && value.length > 0))
        ? "block" : "none";
  });
}

if (deleteNameSpace && deleteDropdown) {
  deleteNameSpace.addEventListener("input", () => {
    const value = deleteNameSpace.value.trim();
    const lowerValue = value.toLowerCase();
    deleteDropdown.innerHTML = "";

    if (value === "") {
      deleteDropdown.style.display = "none";
      return;
    }

    const filtered = allBooks.filter(book =>
      book.toLowerCase().includes(lowerValue)
    );
    const maxItems = 5;
    const itemsToShow = filtered.slice(0, maxItems);

    itemsToShow.forEach(book => {
      const item = document.createElement("div");
      item.className = "dropdown-item delete-item";
      item.textContent = book;

      item.onclick = (e) => {
        e.stopPropagation();
        deleteNameSpace.value = book;
        deleteDropdown.style.display = "none";
      };

      deleteDropdown.appendChild(item);
    });

    deleteDropdown.style.display = itemsToShow.length > 0 ? "block" : "none";
  });
}

if (nameSpaceInput && dropdown) {
  createDropdown(nameSpaceInput, dropdown, true, false);
}

const externalDeleteBtn = document.getElementById("book-delete-btn");
if (externalDeleteBtn) {
  externalDeleteBtn.onclick = async (e) => {
    e.preventDefault();
    const bookToDelete = deleteNameSpace.value.trim();

    if (!bookToDelete) {
      showWarning("Warning", "Please select a book to delete");
      return;
    }

    if (confirm(`Are you sure you want to delete "${bookToDelete}"?`)) {
      const success = await deleteBook(bookToDelete);
      if (success) {
        deleteNameSpace.value = "";
        deleteDropdown.style.display = "none";
      } else {
        console.log("Failed to delete book ,It might be a system book or an error occurred.");
      }
    }
  };
}

document.addEventListener("click", (e) => {
  if (!e.target.closest(".dropdown-container")) {
    if (dropdown) dropdown.style.display = "none";
    if (deleteDropdown) deleteDropdown.style.display = "none";
  }
});

// Load books on page load
window.addEventListener('load', fetchBooks);

window.bookManager = {
  fetchBooks,
  saveBook,
  deleteBook,
  getAllBooks: () => [...allBooks]
};