const menuButton_gear = document.querySelector(".menu-button-2"); // controls right sidebar
const menuButton_burger = document.querySelector(".menu-button-1"); // controls left sidebar
const icon_burger = menuButton_burger.querySelector("i");
const icon_gear = menuButton_gear.querySelector("i");
const mail_btn = document.querySelector(".menu-button-3");
const mail_icon = document.querySelector(".fa-envelope")

const sidebar_right = document.getElementById("rightSidebar");
const sidebar_left = document.querySelector(".sidebar");
const mail_box = document.querySelector(".mail");
// const mail_box = document.getElementById("mail")// added . for class

// Toggle Functions
function toggleRightSidebar() {
  if (!sidebar_right.classList.contains("hidden")) {
    hideRightSidebar();
  } else {
    showRightSidebar();
  }
  window.scrollTo(0, 0);
}

function toggleLeftSidebar() {
  if (sidebar_left.classList.contains("shown")) {
    hideLeftSidebar();
  } else {
    showLeftSidebar();
  }
  window.scrollTo(0, 0);
}

function toggleMailBox(){
  if (!mail_box.classList.contains("hidden")){
    hideMailBox();
  } else {
    showMailBox();
  }
  window.scrollTo(0, 0);
}

// Show / Hide Right Sidebar
function showRightSidebar() {
  hideMailBox();
  mail_btn.classList.add("hide");
  document.querySelector(".error").classList.remove("visible");
  document.querySelector(".error").classList.remove("success");
  sidebar_right.classList.remove("hidden");
  icon_gear.classList.add("rotated");
  menuButton_gear.classList.add("rotated");
  document.body.style.overflow = "auto";
}

function hideRightSidebar() {
  mail_icon.classList.add("fa-envelope")
  mail_btn.classList.remove("hide");
  sidebar_right.classList.add("hidden");
  icon_gear.classList.remove("rotated");
  menuButton_gear.classList.remove("rotated");
  mail_btn.classList.remove("hide");
}

// Show / Hide Left Sidebar
function showLeftSidebar() {
  sidebar_left.classList.add("shown");
  menuButton_burger.classList.add("rotated");
  icon_burger.classList.add("rotated");
  document.body.style.overflow = "hidden";
}

function hideLeftSidebar() {
  sidebar_left.classList.remove("shown");
  icon_burger.classList.remove("rotated");
  menuButton_burger.classList.remove("rotated");
  document.body.style.overflow = "auto";
}

// Show / Hide Mail Box
function showMailBox() {
  mail_box.classList.remove("hidden");
  let chatID = window.conversation_id;
  let endpointIndex = chatID
    ? `${url_prefix}/chat/${chatID}/mail/mark-seen`
    : `${url_prefix}/chat/mail/mark-seen`;

  fetch(endpointIndex, { method: "POST" })
    .then(res => res.json())
    .then(() => {
      let messages = JSON.parse(localStorage.getItem('inboxMessages') || '[]');
      messages = messages.map(msg => ({ ...msg, seen: true }));
      localStorage.setItem('inboxMessages', JSON.stringify(messages));

      if (typeof renderMessages === "function") {
        renderMessages(messages);
      }
      const dot = document.getElementById("red-dot");
      if (dot) dot.style.display = "none";
    });
  dot.style.display = "none"
  mail_icon.classList.remove("fa-envelope")
  mail_icon.classList.add("fa-envelope-open");





}

function hideMailBox(){
  mail_icon.classList.add("fa-envelope")
  mail_icon.classList.remove("fa-envelope-open");
  mail_box.classList.add("hidden");

}

// Button Click Events
menuButton_gear.addEventListener("click", toggleRightSidebar);
menuButton_burger.addEventListener("click", toggleLeftSidebar);
mail_btn.addEventListener("click" , toggleMailBox)

// Extra Logic: hide left sidebar if clicking on conversation
document.body.addEventListener("click", function (event) {
  if (event.target.matches(".conversation-title")) {
    if (!sidebar_right.classList.contains("hidden")) {
      hideRightSidebar();
    }
    if (!mail_box.classList.contains("hidden")) {
      hideMailBox();
    }
  }
});
