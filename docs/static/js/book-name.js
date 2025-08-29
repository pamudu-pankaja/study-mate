const showIndex = document.getElementById("current-index");

function setBook() {
  const indexName = document.getElementById("index").value;
  const button = document.getElementById("book-name-btn");
  const url_prefix = document
    .querySelector("body")
    .getAttribute("data-urlprefix");

  if (indexName.trim() == "") {
    showError("Invalid name", "Please enter a valid book name");
    return;
  } else {

    button.disabled = true;

    let chatID = window.conversation_id;
    let endpoint = chatID
      ? `${url_prefix}/chat/${chatID}/book-name`
      : `${url_prefix}/chat/book-name`;

    fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ book_name: indexName }),
    })
      .then((res) => res.json())
      .then((data) => {

        if (data.status == "success") {
          showSuccess("Success", data.message)
          console.log(`Book name submitted : ${indexName}`);
          showIndex.textContent = `Book Name : ${indexName}`;
        }

        if (data.status == "error") {
          showError("Faild", data.message)
          console.log(data.error_msg);
          showIndex.textContent = `Book Name : Not set`;
        }
      })

      .catch((error) => {
        showError("Failed", error)
        console.error("fetch error :", error);
        showIndex.textContent = `Book Name : Not set`;
      })

      .finally(() => {
        button.disabled = false;
      });
  }
}

window.addEventListener("DOMContentLoaded", () => {
  let chatID = window.conversation_id;
  let endpoint = chatID
    ? `${url_prefix}/chat/${chatID}/book-name`
    : `${url_prefix}/chat/book-name`;

  fetch(endpoint)
    .then((res) => res.json())
    .then((data) => {
      const currentIndex = data.book_name || "Book Name : Not set";
      console.log("Current index name:", currentIndex);
      showIndex.textContent = currentIndex;
    });
});
