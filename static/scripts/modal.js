function openModal() {
    document.getElementById("overlay").style.display = "grid";
    document.getElementById("modal").style.display = "grid";
    document.getElementById("overlay").style.justifyContent = "space-around";
    document.getElementById("modal").style.justifyContent = "space-around";
    document.getElementById("overlay").style.textAlign = "center";
    document.getElementById("modal").style.textAlign = "center";
}

function closeModal() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("modal").style.display = "none";
}

// Обработка нажатия на ссылку "Личный кабинет"
/*document.getElementById("toAccount").addEventListener("click", function(event) {
    event.preventDefault();
    openModal();
});*/
