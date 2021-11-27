function modalDisplay(){
    let ele = document.getElementsByClassName("Login-modal-background")[0];
    if(ele.style.display === "block"){
        ele.style.display = "none";
    }else{
        ele.style.display = "block";
    }
}