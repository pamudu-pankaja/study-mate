const input = document.getElementById("file_input");
const display = document.getElementById("file_name");
const fallBackDisplay = document.getElementById("file-fallback-message");
const fallBackDisplay_index = document.getElementById("index-fallback-message");
const button = document.getElementById("file-upload-btn");
const showStartPage = document.getElementById("start-page");




input.addEventListener("change", () => {
  const file = input.files[0];
  const max_size = 1 * 1024 * 1024;

  if (!file) {
    return;
  }

  if (file.type !== "application/pdf") {
    fallBackDisplay.textContent = "Only PDF file are allowed";
    fallBackDisplay.classList.add("visible");
    input.value = "";
    display.textContent = "No file chosen";
    return;
  }

  if (file.size >= max_size) {
    fallBackDisplay.textContent = "File must be under 1 MB";
    fallBackDisplay.classList.add("visible");
    input.value = "";
    display.textContent = "No file chosen";
    return;
  }

  // fallBackDisplay.textContent = "File added successfully";
  // fallBackDisplay.classList.remove("visible");
  // fallBackDisplay.classList.add("success");
  display.textContent = ` ${file.name} `;
  display.title = file.name;
});

async function uploadFile() {
  const startPage = document.getElementById("starting-page").value;
  // const index_name = document.getElementById("index").value;
  const file = input.files[0];
  const url_prefix = document
    .querySelector("body")
    .getAttribute("data-urlprefix");
  
  let chatID = window.conversation_id;

  let endpointIndex = chatID
    ? `${url_prefix}/chat/${chatID}/index-name`
    : `${url_prefix}/chat/index-name`;

  const res = await fetch(endpointIndex , { method:"GET"});
  const data = await res.json();
  const index_name = data.indexName;

  if (!index_name || index_name == '') {
    fallBackDisplay_index.classList.add("visible");
    fallBackDisplay_index.classList.remove("success");
    fallBackDisplay_index.textContent = "Please set a index name";
    console.log("Index name is missing , file uploading is aborting");
    return;
  }

  if (!file) {
    fallBackDisplay.textContent = "Please upload a file";
    fallBackDisplay.classList.add("visible");
    fallBackDisplay_index.classList.remove("success");
    input.value = "";
    display.textContent = "No file chosen";
    return;
  }

  fallBackDisplay.textContent = "Sending...";
  fallBackDisplay.classList.add("visible");
  fallBackDisplay.classList.remove("success");
  fallBackDisplay.style.color = "#DADADA";

  button.disabled = true;

  console.log(startPage);
  const formData = new FormData();
  formData.append("pdf", file);
  formData.append("startPage", startPage);
  formData.append("indexName", index_name);

  let endpointFile = chatID
    ? `${url_prefix}/chat/${chatID}/import-file`
    : `${url_prefix}/chat/import-file`;

  try {
    const res = await fetch(endpointFile, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    // If you are not me just dont get your head fucked up with these class names check the css file right side bar
    if (data.status == "success") {
      fallBackDisplay.classList.add("success");
      fallBackDisplay.classList.remove("visible");
      fallBackDisplay.textContent = data.message;
      console.log(`file added`);
    }

    if (data.status == "error" || !data) {
      fallBackDisplay.classList.add("visible");
      fallBackDisplay.classList.remove("success");
      fallBackDisplay.textContent = data.message;
      console.log(data.error_msg || "Check the local server terminal");
    }
  } catch (error) {
    fallBackDisplay.classList.add("visible");
    fallBackDisplay.classList.remove("success");
    fallBackDisplay.style.fontSize = "12px";
    fallBackDisplay.textContent = "[check console] Something went wrong";
    console.error("fetch error :", error);
  } finally {
    button.disabled = false;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  let endpointStartPage = chatID
    ? `${url_prefix}/chat/${chatID}/start-page`
    : `${url_prefix}/chat/start-page`;

  fetch(endpointStartPage)
    .then((res) => res.json())
    .then((data) => {
      const currentPage = data.start_page || "Start Page : Not set";
      console.log("Current Starting Page:", data.startPage || 0);
      showStartPage.textContent = currentPage;
    });
});

