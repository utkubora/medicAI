/*
document.getElementById('ask-form').addEventListener('submit', function(event) {
    event.preventDefault();
    var formData = new FormData(this);

    fetch('/submit-medicine', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        var responseDiv = document.getElementById('chat-history');
        var newElement = document.createElement('p');
        newElement.textContent = data.message + ': ' + data.data;
        responseDiv.appendChild(newElement);
    })
    .catch(error => console.error('Error:', error));
});
*/



$('#btn-submit').on('click', async function(){
    try{
        $('#btn-submit').attr('disabled',true)

        $('.chatbox__messages').prepend('<div class="messages__item messages__item--operator">' + $('#data').val() + '</div>');

        var formData = new FormData();
        formData.append('data', $('#data').val())
        formData.append('chatId', $('#chatId').val())

        var response = await fetch('/submit-medicine', {
            method: 'POST',
            body: formData,
            
        })

        if(response.ok){
            var result = await response.json();

            $('.chatbox__messages').prepend('<div class="messages__item messages__item--visitor">' + result.data + '</div>');
            $('#data').val("");
            $('#btn-submit').attr('disabled',false);
        }



    }catch (err){
        console.error('Error:', err);
        $('#data').val("");
        $('#btn-submit').attr('disabled',false);
    }
})