$('.btn-submit').on('change', async function(){
    try{
        var formData = new FormData();
        formData.append('userId', $(this).data('id'))
        formData.append('newRole', $(this).val())

        var response = await fetch('/submit-user', {
            method: 'POST',
            body: formData
        })

        if(response.ok){
            var result = await response.json();
        }

    }catch (err){
        console.error('Error:', err);
    }
})