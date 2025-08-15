const input = document.getElementById("file_input");
const display = document.getElementById("file_name");
const button = document.getElementById("file-upload-btn");

input.addEventListener("change", () => {
  const file = input.files[0];
  const max_size = 20 * 1024 * 1024; //Maximum file size 20MB

  if (!file) {
    return;
  }

  if (file.type !== "application/pdf") {
    showWarning("Invalid File Type","Only PDF files are allowed")
    input.value = "";
    display.textContent = "No file chosen";
    return;
  }

  if (file.size >= max_size) {
    showWarning("Invalid File Size", "File size must be under 20MB")
    input.value = "";
    display.textContent = "No file chosen";
    return;
  }

  display.textContent = ` ${file.name} `;
  display.title = file.name;
});

async function uploadFile() {
  let startPage = document.getElementById("starting-page").value;

  if (startPage == null && startPage < 0 ){
    startPage = 0
  }

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
    showError("Book Name Empty" , "Please set a valid Book Name to import file")
    console.log("Index name is missing , file uploading is aborting");
    return;
  }

  if(index_name == allBooks)

  if (!file) {
    showWarning("No File","Please upload a file to be imported")
    input.value = "";
    display.textContent = "No file chosen";
    return;
  }

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

    if (data.status == "processing") {
      showSuccess("File is Processing",data.message)
      console.log(`file is processing in the background`);
    }

    if (data.status == "error" || !data) {
      showError("Faild to Import",data.message)
      console.log(data.error_msg || "Check the local server terminal");
    }
  } catch (error) {
    showError("Faild to Import", error)
    console.error("fetch error :", error);
  } finally {
    button.disabled = false;
  }
}

// window.addEventListener("DOMContentLoaded", () => {
//   let chatID = window.conversation_id;

//   let endpointStartPage = chatID
//     ? `${url_prefix}/chat/${chatID}/start-page`
//     : `${url_prefix}/chat/start-page`;

//   fetch(endpointStartPage)
//     .then((res) => res.json())
//     .then((data) => {
//       const currentPage = data.start_page;
//       console.log(data.startPage || 0);
//       showStartPage.textContent = currentPage;
//     });
// });

