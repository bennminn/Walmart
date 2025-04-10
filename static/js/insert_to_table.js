function addProfileWithAnimation(profileHtml, tableId) {
    const tableBody = document.getElementById(tableId);
    const newRow = document.createElement('tr');
    newRow.classList.add('fade-in');
    newRow.innerHTML = profileHtml;
    tableBody.appendChild(newRow);

    // Wait for the animation to finish before adding the next profile
    newRow.addEventListener('animationend', () => {
        addNextProfile();
    });
}

function addNextProfile() {
    const notAssignedProfiles = document.querySelectorAll('.not-assigned-profile-to-add');
    const assignedProfiles = document.querySelectorAll('.assigned-profile-to-add');

    if (notAssignedProfiles.length > 0) {
        const profile = notAssignedProfiles[0];
        profile.classList.remove('not-assigned-profile-to-add');
        addProfileWithAnimation(profile.innerHTML, 'present-not-assigned');
        profile.remove();
    } else if (assignedProfiles.length > 0) {
        const profile = assignedProfiles[0];
        profile.classList.remove('assigned-profile-to-add');
        addProfileWithAnimation(profile.innerHTML, 'assigned');
        profile.remove();
    }
}

window.addEventListener('load', () => {
    addNextProfile();
});