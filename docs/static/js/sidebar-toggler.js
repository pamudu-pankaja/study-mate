const menuButton_gear = document.querySelector(".menu-button-2"); // controls right sidebar
const menuButton_burger = document.querySelector(".menu-button-1"); // controls left sidebar
const icon_burger = menuButton_burger.querySelector("i");
const icon_gear = menuButton_gear.querySelector("i")

const sidebar_right = document.getElementById("rightSidebar");
const sidebar_left = document.querySelector(".sidebar"); // added . for class

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

// Show / Hide Right Sidebar
function showRightSidebar() {
    sidebar_right.classList.remove("hidden");
    icon_gear.classList.add("rotated");
    menuButton_gear.classList.add("rotated");
    document.body.style.overflow = "auto";
}

function hideRightSidebar() {
    sidebar_right.classList.add("hidden");
    icon_gear.classList.remove("rotated");
    menuButton_gear.classList.remove("rotated");
    document.body.style.overflow = "hidden";
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

// Button Click Events
menuButton_gear.addEventListener("click", toggleRightSidebar);
menuButton_burger.addEventListener("click", toggleLeftSidebar);

// Extra Logic: hide left sidebar if clicking on conversation
document.body.addEventListener("click", function (event) {
    if (event.target.matches(".conversation-title")) {
        const menuButtonStyle = window.getComputedStyle(menuButton_burger);
        if (menuButtonStyle.display !== "none") {
            hideLeftSidebar();
        }
    }
});
