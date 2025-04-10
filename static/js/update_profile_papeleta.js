document.querySelectorAll('.block-btn').forEach(btn => {
	btn.addEventListener('click', () => alert('Consultar con supervisor para editar este campo'));
});

document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        let field = this.parentElement.previousElementSibling.querySelector('p');
        let input = document.createElement('input');
        input.value = field.innerText;
        field.replaceWith(input);

        input.addEventListener('blur', function() {
            let data = {};
            data[field.id] = input.value;

            fetch('/update_profile/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    input.replaceWith(field);
                    field.innerText = input.value;
                } else {
                    alert('Error updating field');
                }
            });
        });
    });
});