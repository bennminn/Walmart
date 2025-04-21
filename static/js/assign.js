async function assignDriver() {
    let rutElement = profileDetails.querySelector('p:nth-of-type(1)');
    let rutText = rutElement.innerText;
    let profileRut = rutText.split(': ')[1];
    if (!profileRut) {
        console.log('No profile ID provided');
		alert('No profile ID provided');
    } else {
		try {
			let id_response = await $.ajax({
				type: 'GET',
				url: `/profile_rut_to_id/${profileRut}/`,
			})

			if (id_response.success) {
				let assigned_profile_id = id_response.profile_id;
				let csrftoken = getCookie('csrftoken');

				let profile_assign_update = await $.ajax({
					type: 'POST',
					url: `/update_profile_assignment/${assigned_profile_id}/`,
					data: {
						is_assigned: true
					},
					headers: {
                        'X-CSRFToken': csrftoken
                    }
				});

				if(profile_assign_update.success){
					window.location.href = '/';
				} else {
					console.log('Error in AJAX request:', profile_assign_update);
					alert('Error in AJAX request while updating profile assign field:', profile_assign_update.error || 'No specific error message provided');
				}					


			} else {
				console.log('Error in AJAX request:', id_response);
				alert('Error in AJAX request while obtaining id from rut::', id_response.error || 'No specific error message provided');
			}


		} catch (err){
			alert(`While updating assigned information found unexpected error:\n${err}`)
		}
	}
}

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

