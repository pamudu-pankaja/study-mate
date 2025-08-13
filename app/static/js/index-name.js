const showIndex = document.getElementById("current-index");

function setIndex() {
  const indexName = document.getElementById("index").value;
  const fallBackDisplay = document.getElementById("index-fallback-message");
  const button = document.getElementById("index-name-btn");
  const url_prefix = document
    .querySelector("body")
    .getAttribute("data-urlprefix");

  if (indexName.trim() == "") {
    fallBackDisplay.textContent = "Please enter a valid index name";
    fallBackDisplay.classList.add("visible");
    return;
  } else {
    fallBackDisplay.textContent = "Sending...";
    fallBackDisplay.classList.add("visible");
    fallBackDisplay.classList.remove("success");
    fallBackDisplay.style.color = "#DADADA";

    button.disabled = true;

    let chatID = window.conversation_id;
    let endpoint = chatID
      ? `${url_prefix}/chat/${chatID}/index-name`
      : `${url_prefix}/chat/index-name`;

    setTimeout(() => {
      fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ index_name: indexName }),
      })
        .then((res) => res.json())
        .then((data) => {
          // If you are not me just dont get your head messed up with these class names check the css file right side bar

          if (data.status == "success") {
            fallBackDisplay.classList.add("success");
            fallBackDisplay.classList.remove("visible");
            fallBackDisplay.textContent = data.message;
            console.log(`Index submitted : ${indexName}`);
            showIndex.textContent = `Index Name : ${indexName}`;
          }

          if (data.status == "error") {
            fallBackDisplay.classList.add("visible");
            fallBackDisplay.classList.remove("success");
            fallBackDisplay.textContent = data.message;
            console.log(data.error_msg);
            showIndex.textContent = `Index Name : Not set`;
          }
        })

        .catch((error) => {
          fallBackDisplay.classList.add("visible");
          fallBackDisplay.classList.remove("success");
          fallBackDisplay.style.fontSize = "12px";
          fallBackDisplay.textContent = "[check console] Something went wrong";
          console.error("fetch error :", error);
          showIndex.textContent = `Index Name : Not set`;
        })

        .finally(() => {
          button.disabled = false;
        });
    }, 500);
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
      const currentIndex = data.index_name || "Index Name : Not set";
      console.log("Current index name:", currentIndex);
      showIndex.textContent = currentIndex;
    });
});
