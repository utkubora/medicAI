class Chatbox {
    constructor() {
        this.args = {
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.messages = [];
    }

    display() {
        const { chatBox, sendButton } = this.args;
            
        sendButton.addEventListener('click', () => this.onSendButton(chatBox))
    
        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox);
            }
        })
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');

        $('.send__button').attr('disabled',true)


        let text1 = $('#data').val();
        if (text1 === "") {
            return;
        }

        let msg1 = {name: "User", message: text1};
        this.messages.push(msg1);

        console.log("text1 : " + text1 )
        console.log("chatID : " +  $('#chatId').val() )
        
        // Assuming $SCRIPT_ROOT is properly defined in your HTML to point to your server
        fetch( $SCRIPT_ROOT + '/submit-disease', {
            method: 'POST',
            body: JSON.stringify({ data: text1, chatId: $('#chatId').val() }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => r.json())
        .then(r => {
            let msg2 = {name: "Bot", message: r.answer};
            this.messages.push(msg2);
            this.updateChatText(chatbox);
            textField.value = "";

            $('.send__button').attr('disabled',false)
            $('#data').val('')

        }).catch((error) => {
            console.error('Error:', error);
            // Fallback message in case of error
            let msg2 = {name: "Bot", message: "Sorry, I'm having trouble understanding you."};
            this.messages.push(msg2);
            this.updateChatText(chatbox);
            textField.value = "";

            $('.send__button').attr('disabled',false)
            $('#data').val('')
            
        });
    }

    updateChatText(chatbox) {
        var html = "";
        this.messages.slice().reverse().forEach(function(item) {
            let className = item.name === "Bot" ? "messages__item--visitor" : "messages__item--operator";
            html += `<div class='messages__item ${className}'>${item.message}</div>`;
        });

        //const chatmessage = chatbox.querySelector('.chatbox__messages');
        //chatmessage.innerHTML = html;

        $('.chatbox__messages').prepend(html)
    }
}

const chatbox = new Chatbox();
chatbox.display();
