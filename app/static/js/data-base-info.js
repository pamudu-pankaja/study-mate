function setIndex(){
    const indexName = document.getElementById('index').value;

    if (indexName.trim() == "" ) {
        alert("Please enter a valid index name.");
        return;
    }
    else{
        console.log(`Index submitted : ${indexName}`)
    }    
}



