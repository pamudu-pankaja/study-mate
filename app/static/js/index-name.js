function setIndex(){
    const indexName = document.getElementById('index').value;
    const fallBackDisplay = document.getElementById('index-fallback-message');

    if (indexName.trim() == "" ) {
        fallBackDisplay.classList.add('visible')       
        return;
    }
    else{
        fallBackDisplay.classList.remove('visible')
        console.log(`Index submitted : ${indexName}`)
    }    
}



