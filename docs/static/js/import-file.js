const input = document.getElementById('file_input');
const display = document.getElementById('file_name');
const fallBackDisplay =document.getElementById("file-fallback-message");
const fallBackDisplay_index = document.getElementById('index-fallback-message');

input.addEventListener('change' ,() => {
    const file = input.files[0];
    const max_size = 1 * 1024 * 1024;
    
    if (!file) {
        return;
    }

    if (file.type !== 'application/pdf') {
        fallBackDisplay.textContent="Only PDF file are allowed";
        fallBackDisplay.classList.add("visible");
        input.value = '';
        display.textContent='No file chosen';
        return;
    }

    if (file.size >= max_size){
        fallBackDisplay.textContent="File must be under 1 MB";
        fallBackDisplay.classList.add("visible");
        input.value = '';
        display.textContent='No file chosen';
        return;
    }
    
    fallBackDisplay.textContent="File added successfully"
    fallBackDisplay.classList.remove('visible')
    fallBackDisplay.classList.add('success')
    display.textContent = ` ${file.name} `;
    display.title = file.name;
})