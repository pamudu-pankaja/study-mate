const menuButton = document.querySelector(".menu-button");
const icon = menuButton.querySelector("i");
const sidebar = document.getElementById('rightSidebar');

function toggleSidebar(event) {
    if (!sidebar.classList.contains("hidden")) {
        hideSidebar(event.target);
    } else {
        showSidebar(event.target);
    }
    window.scrollTo(0, 0);
}

function showSidebar(target) {
    sidebar.classList.remove("hidden");
    icon.classList.add("rotated");
    menuButton.classList.toggle("rotated")
    document.body.style.overflow = "auto";
}

function hideSidebar(target) {
    sidebar.classList.add("hidden");
    icon.classList.remove("rotated");
    menuButton.classList.toggle("rotated")
    document.body.style.overflow = "hidden";
}

menuButton.addEventListener("click", toggleSidebar);

// document.body.addEventListener('click', function(event) {
//     if (event.target.matches('.conversation-title')) {
//         const menuButtonStyle = window.getComputedStyle(menuButton);
//         if (menuButtonStyle.display !== 'none') {
//             hideSidebar(menuButton);
//         }
//     }
// });


// function toggleRightSidebar() {
//   const sidebar = document.getElementById('rightSidebar');
//   sidebar.classList.toggle('hidden');
// }

// function closeRightSidebar() {
//   document.getElementById('rightSidebar').classList.add('hidden');
// }
