function checkForMessages() {
  let endpointIndex = chatID
    ? `${url_prefix}/chat/${chatID}/mail`
    : `${url_prefix}/chat/mail`;

  fetch(endpointIndex , {method:"GET"})
    .then((res) => res.json())
    .then((data) => {
      const unseenMessages = data.filter((msg) => !msg.seen);

      // Update red dot
      const dot = document.getElementById("red-dot");
      dot.style.display = unseenMessages.length > 0 ? "block" : "none";

      // Update inbox UI
      const messageContainer = document.getElementById("index-messsages");
      messageContainer.innerHTML = ""; // Clear old messages

      data.forEach((msg) => {
        const messageItem = document.createElement("div");
        messageItem.className = "message-item";

        const topRow = document.createElement("div");
        topRow.className = "top-row";

        const sender = document.createElement("span");
        sender.className = "sender";
        sender.textContent = msg.sender;

        const timestamp = document.createElement("span");
        timestamp.className = "timestamp";
        timestamp.textContent = msg.time;

        topRow.appendChild(sender);
        topRow.appendChild(timestamp);

        const preview = document.createElement("div");
        preview.className = "preview";
        preview.textContent = msg.content;

        const deleteBtn = document.createElement("div");
        deleteBtn.className = "delete-btn";
        deleteBtn.innerHTML = `<i class="fa-solid fa-trash"></i>`;
        deleteBtn.addEventListener("click", () => {
          fetch(`${endpointIndex}/${msg.id}`, { method: "DELETE" }).then(() =>
            checkForMessages()
          );
        });

        messageItem.appendChild(topRow);
        messageItem.appendChild(preview);
        messageItem.appendChild(deleteBtn);

        messageContainer.appendChild(messageItem);
      });
    });
}

setInterval(checkForMessages, 5000);
