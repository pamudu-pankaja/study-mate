const showIndex = document.getElementById("current-index");

function setIndex() {
  const indexName = document.getElementById("index").value;
  const button = document.getElementById("index-name-btn");
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
      ? `${url_prefix}/chat/${chatID}/index-name`
      : `${url_prefix}/chat/index-name`;

    fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ index_name: indexName }),
    })
      .then((res) => res.json())
      .then((data) => {

        if (data.status == "success") {
          showSuccess("Success", data.message)
          console.log(`Book name submitted : ${indexName}`);
          showIndex.textContent = indexName;
          showIndex.title= indexName;
        }

        if (data.status == "error") {
          showError("Faild", data.message)
          console.log(data.error_msg);
          showIndex.textContent = `TextBook Not Selected`;
          showIndex.title= indexName;
        }
      })

      .catch((error) => {
        showError("Failed", error)
        console.error("fetch error :", error);
        showIndex.textContent = `TextBook Not Selected`;
      })

      .finally(() => {
        button.disabled = false;
      });
  }
}

window.addEventListener("DOMContentLoaded", () => {
  let chatID = window.conversation_id;
  let endpoint = chatID
    ? `${url_prefix}/chat/${chatID}/index-name`
    : `${url_prefix}/chat/index-name`;

  fetch(endpoint)
    .then((res) => res.json())
    .then((data) => {
      const currentIndex = data.index_name || "TextBook Not Selected";
      console.log("Current book name:", currentIndex);
      showIndex.textContent = currentIndex;
    });
});
