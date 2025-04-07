function showProfileModal(profileId) {
    $.ajax({
        url: `/profile/${profileId}/details/`,
        method: 'GET',
        success: function(data) {
            if (data.success) {
                var profile = data.profile;
                var profileDetailsHtml = `
                    <h2>${profile.first_name} ${profile.last_name}</h2>
                    <p>RUT: ${profile.rut}</p>
                    <p>Email: ${profile.email}</p>
                    <p>Phone: ${profile.phone}</p>
                    <p>Transportista: ${profile.transportista}</p>
                    <p>Status: ${profile.status}</p>
                `;
                document.getElementById('profileDetails').innerHTML = profileDetailsHtml;
                document.getElementById('profileModal').style.display = 'block';
            } else {
                alert(data.error);
            }
        },
        error: function() {
            alert('Error fetching profile details.');
        }
    });
}

function closeProfileModal() {
    document.getElementById('profileModal').style.display = 'none';
}