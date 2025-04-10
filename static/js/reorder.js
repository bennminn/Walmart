document.addEventListener('DOMContentLoaded', function() {
    const presentNotAssignedTable = document.getElementById('present-not-assigned');

    presentNotAssignedTable.addEventListener('click', function(event) {
        const row = event.target.closest('tr');
        if (row && row.classList.contains('not-assigned-profile-to-add')) {
            showArrows(row);
        }
        //alert("accessing action");
    });
});

function showArrows(row) {
    var actions = row.querySelector(".actions");
    console.log("Actions element:", actions); // Log the actions element
    if (actions) {
        console.log("Current display:", actions.style.display); // Log current display property
        actions.style.display = actions.style.display === "none" ? "block" : "none";
        console.log("New display:", actions.style.display); // Log new display property
    } else {
        console.error("Actions element not found");
    }
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