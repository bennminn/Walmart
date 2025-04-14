document.querySelectorAll('.block-btn').forEach(btn => {
	btn.addEventListener('click', () => alert('Consultar con supervisor para editar este campo'));
});

// Store state of the currently active edit (if any)
let activeEditState = null;

// Function to cancel any ongoing edit
function cancelActiveEdit() {
    if (activeEditState) {
        const { inputElement, pElement, originalValue, editButtonContainer, originalEditButton } = activeEditState;
        pElement.innerText = originalValue; // Restore original text
        inputElement.replaceWith(pElement); // Replace input with P
        editButtonContainer.innerHTML = ''; // Clear Save/Cancel buttons
        editButtonContainer.appendChild(originalEditButton); // Restore original Edit button
        activeEditState = null; // Clear state
    }
}

// Function to perform the update AJAX call
async function performUpdate(fieldId, newValue, inputElement, pElement, editButtonContainer, originalEditButton) {
    let rutElement = document.getElementById('Rut');
    if (!rutElement) {
        alert('Error: RUT element not found.');
        return false; // Indicate failure
    }
    let profileRut = rutElement.innerText.trim();
    console.warn("Attempting update for RUT:", profileRut);

    if (!profileRut) {
        alert('Error: Could not read RUT.');
        return false; // Indicate failure
    }

    try {
        console.warn("Fetching profile ID for RUT:", profileRut);
        const idResponse = await fetch(`/profile_rut_to_id/${profileRut}/`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });

        if (!idResponse.ok) {
            throw new Error(`Failed to fetch profile ID: ${idResponse.statusText}`);
        }

        const idData = await idResponse.json();
        console.warn("Profile ID response:", idData);

        if (idData.success && idData.profile_id) {
            const profileId = idData.profile_id;
            console.warn("Successfully got profile ID:", profileId);

            const data = { [fieldId]: newValue };
            console.warn(`Updating profile ID ${profileId} with data:`, data);
            console.warn('JSON being sent:', JSON.stringify(data)); // Add this line


            const updateResponse = await fetch(`/update_profile/${profileId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });

             if (!updateResponse.ok) {
                // Try to get more specific error from JSON response if possible
                let errorDetail = updateResponse.statusText;
                console.warn(`error updating: `, errorDetail);
                try {
                    const errorJson = await updateResponse.json();
                    // Use the first error message if available in standard Django format
                    if (errorJson.errors && typeof errorJson.errors === 'object') {
                       const firstKey = Object.keys(errorJson.errors)[0];
                       errorDetail = `${firstKey}: ${errorJson.errors[firstKey][0]}`;
                    } else {
                       errorDetail = errorJson.error || errorJson.errors || updateResponse.statusText;
                    }
                } catch (e) { /* Ignore if response wasn't JSON, stick with status text */ }
                msg = `Failed to update profile (${updateResponse.status}): ${errorDetail}`
                console.warn(msg)
                throw new Error(msg);
            }


            const updateData = await updateResponse.json();

            if (updateData.status === 'success') {
                console.warn("Update successful for profile ID:", profileId);
                pElement.innerText = newValue; // Update the text in the original P element
                return true; // Indicate success
            // In the performUpdate function, around line 91:
            } else {
                // Extract specific error message if backend provided one
                const errorMsg = updateData.errors || updateData.error || 'Unknown server error';
                console.warn('Error update data response:', JSON.stringify(updateData, null, 2));  // Add this line
                console.warn('Error message type:', typeof errorMsg);  // Add this line
                console.warn('Error message content:', errorMsg);  // Add this line
                alert('Error updating field: ' + (typeof errorMsg === 'object' ? JSON.stringify(errorMsg) : errorMsg));
                return false; // Indicate failure
            }
        } else {
            alert('Error getting profile ID: ' + (idData.error || 'Could not retrieve ID.'));
            return false; // Indicate failure
        }
    } catch (error) {
        console.error('Error during profile update:', error);
        alert(`An error occurred: ${error.message}`);
        return false; // Indicate failure
    }
}


document.querySelectorAll('.edit-btn').forEach(editBtn => {
    editBtn.addEventListener('click', function handleEditClick() {
        // If another edit is active, cancel it first
        if (activeEditState && activeEditState.originalEditButton !== this) {
            cancelActiveEdit();
        }

        // If THIS button's field is already being edited, do nothing
        if (activeEditState && activeEditState.originalEditButton === this) {
            return;
        }

        const originalEditButton = this; // Keep reference to the clicked button
        const editButtonContainer = this.parentElement;
        const valueContainer = editButtonContainer.previousElementSibling;
        const pElement = valueContainer.querySelector('p');

        if (!pElement) {
            console.error("Could not find 'p' element for button:", this);
            alert("Error: Could not find the field element to edit.");
            return;
        }

        const originalValue = pElement.innerText;
        let fieldId = pElement.id;

        console.warn(`field name: ${fieldId}`);

        if(fieldId == "Email"){
            fieldId = "email";
        } else if (fieldId == "Phone") {  // Also changed "Telefono" to "Phone" to match your HTML
            fieldId = "phone";
        }

        // Create input element
        const input = document.createElement('input');
        input.type = 'text';
        input.value = originalValue;
        input.className = 'form-control form-control-sm'; // Optional: Add Bootstrap styling

        // Create Save button (using simple text/icon)
        const saveBtn = document.createElement('button');
        saveBtn.innerHTML = '&#10004;'; // Checkmark icon
        saveBtn.title = 'Guardar';
        saveBtn.className = 'btn btn-sm btn-success mr-1'; // Optional: Bootstrap styling

        // Create Cancel button (using simple text/icon)
        const cancelBtn = document.createElement('button');
        cancelBtn.innerHTML = '&#10006;'; // X icon
        cancelBtn.title = 'Cancelar';
        cancelBtn.className = 'btn btn-sm btn-danger'; // Optional: Bootstrap styling

        // Replace P with Input
        pElement.replaceWith(input);
        input.focus(); // Focus the new input field
        input.select(); // Select the text

        console.log("Attempting to replace buttons in container:", editButtonContainer);


        // Replace Edit button with Save/Cancel buttons
        editButtonContainer.innerHTML = ''; // Clear the container
        editButtonContainer.appendChild(saveBtn);
        editButtonContainer.appendChild(cancelBtn);

        // Store state for potential cancellation or for the save action
        activeEditState = {
            inputElement: input,
            pElement: pElement,
            originalValue: originalValue,
            editButtonContainer: editButtonContainer,
            originalEditButton: originalEditButton // Store the original button
        };

        // Add listener for the Save button
        saveBtn.addEventListener('click', async () => {
            const newValue = input.value;
            // Disable buttons while saving
            saveBtn.disabled = true;
            cancelBtn.disabled = true;

            const success = await performUpdate(fieldId, newValue, input, pElement, editButtonContainer, originalEditButton);

            if (success) {
                // Update succeeded, restore UI
                input.replaceWith(pElement); // Replace input with updated P
                editButtonContainer.innerHTML = '';
                editButtonContainer.appendChild(originalEditButton);
                activeEditState = null; // Clear active state
            } else {
                // Update failed, re-enable buttons, leave input field
                saveBtn.disabled = false;
                cancelBtn.disabled = false;
                input.focus(); // Refocus input on error
            }
        });

        // Add listener for the Cancel button
        cancelBtn.addEventListener('click', () => {
            cancelActiveEdit(); // Use the cancel function
        });

        // Optional: Add Enter/Escape key handling for the input field
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                saveBtn.click(); // Trigger save on Enter
            } else if (e.key === 'Escape') {
                cancelBtn.click(); // Trigger cancel on Escape
            }
        });
    });
});