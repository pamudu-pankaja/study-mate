function setIndex(){
    const indexName = document.getElementById('index').value;
    const fallBackDisplay = document.getElementById('index-fallback-message');

    if (indexName.trim() == "" ) {
        fallBackDisplay.textContent="Please enter a valid index name !"
        fallBackDisplay.classList.add('visible')       
        return;
    }
    else{
        fallBackDisplay.classList.add('visible')
        fallBackDisplay.textContent="Index name successfully updated !"
        console.log(`Index submitted : ${indexName}`)
    }    
}



