function showProfileModal(profileId) {
    $.ajax({
        url: `/profile/${profileId}/details/`,
        method: 'GET',
        success: function(data) {
            if (data.success) {
                var profile = data.profile;
                console.log(`Información de profile disponible para el modal: ${JSON.stringify(profile)}`);
                var profileDetailsHtml = `
                    <h2>${profile.first_name} ${profile.last_name}</h2>
                    <p id="rut">RUT: ${profile.rut}</p>
                    <p>Email: ${profile.email}</p>
                    <p>Phone: ${profile.phone}</p>
                    <p>Transportista: ${profile.transportista}</p>
                    <p>Prioridad Zona Cero: ${profile.status}</p>
                    <p>Patente Tractocamión: ${profile.patente}</p>
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

