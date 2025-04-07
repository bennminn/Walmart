function showArrows(row) {
    var actions = row.querySelector(".actions");
    actions.style.display = actions.style.display === "none" ? "block" : "none";
}

function moveUp(button) {
    var row = button.closest("tr");
    var prevRow = row.previousElementSibling;
    if (prevRow && prevRow.tagName === "TR") {
        row.parentNode.insertBefore(row, prevRow);
    }
}

function moveDown(button) {
    var row = button.closest("tr");
    var nextRow = row.nextElementSibling;
    if (nextRow && nextRow.tagName === "TR") {
        row.parentNode.insertBefore(nextRow, row);
    }
}