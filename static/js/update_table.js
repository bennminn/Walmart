// Function to fetch new data
function fetchData() {
    console.log("fetching profiles");
    fetch('/fetch_profiles/')
        .then(response => response.json())
        .then(data => {
            updateTables(data.present_not_assigned, data.assigned);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { hour: '2-digit', minute: '2-digit', hour12: true };
    return date.toLocaleTimeString('en-US', options);
}

// Function to update the tables with new rows
function updateTables(presentNotAssignedProfiles, assignedProfiles) {
    console.log("update tables function");
    const presentNotAssignedTable = document.getElementById('present-not-assigned');
    const assignedTable = document.getElementById('assigned');

    // Clear existing rows
    presentNotAssignedTable.innerHTML = '';
    assignedTable.innerHTML = '';

    // Update present-not-assigned table
    console.log("evaluating arrays");
    if (Array.isArray(presentNotAssignedProfiles)) {
        presentNotAssignedProfiles.forEach(profile => {
            // Create a new row for the present-not-assigned table
            const newNotAssignedRow = document.createElement('tr');
            newNotAssignedRow.classList.add('not-assigned-profile-to-add', 'new-row');
            newNotAssignedRow.dataset.id = profile.id;
            newNotAssignedRow.setAttribute('onclick', 'showArrows(this)');
            newNotAssignedRow.innerHTML = `
                <td><button onclick="showProfileModal('${profile.id}')">+</button></td>
                <td>${profile.rut}</td>
                <td>${profile.first_name} ${profile.last_name}</td>
                <td>${profile.Transportista}</td>
                <td>${formatDate(profile.updated)}</td>
                <td>${profile.status}</td>
                <td class="actions" style="display: none;">
                    <button onclick="moveUp(this)">▲</button>
                    <button onclick="moveDown(this)">▼</button>
                </td>
            `;
            
            console.log('Agregando fila a NO asignado');
            newNotAssignedRow.childNodes.forEach((child, index) => {
                console.log(`Elemento ${index + 1}: ${child.outerHTML}`);
            });

            presentNotAssignedTable.appendChild(newNotAssignedRow);
        });
    } else {
        console.error("present_not_assigned is not an array:", presentNotAssignedProfiles);
    }

    // Update assigned table
    if (Array.isArray(assignedProfiles)) {
        assignedProfiles.forEach(profile => {
            // Create a new row for the assigned table
            const newAssignedRow = document.createElement('tr');
            newAssignedRow.classList.add('assigned-profile-to-add', 'new-row');
            newAssignedRow.dataset.id = profile.id;
            newAssignedRow.innerHTML = `
                <td>${profile.rut}</td>
                <td>${profile.first_name} ${profile.last_name}</td>
                <td>${profile.Transportista}</td>
                <td>${formatDate(profile.updated)}</td>
            `;


            console.log('Agregando fila a asignado');
            newAssignedRow.childNodes.forEach((child, index) => {
                if (child.nodeType === Node.ELEMENT_NODE) {
                    console.log(`Elemento ${index + 1}: ${child.outerHTML}`);
                } else {
                    console.log(`Elemento ${index + 1}: (Non-element node)`);
                }
            });


            assignedTable.appendChild(newAssignedRow);
        });
    } else {
        console.error("assigned is not an array:", assignedProfiles);
    }
}

// Polling interval to fetch new data every 10 seconds
// setInterval(fetchData, 7000);

// Initial fetch
fetchData();