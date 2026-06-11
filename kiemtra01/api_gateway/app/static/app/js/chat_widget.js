(function() {
    const style = document.createElement('style');
    style.innerHTML = `
        #bookstore-chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 450px;
            background-color: #fff;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            z-index: 10000;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transform: scale(0);
            transform-origin: bottom right;
            transition: transform 0.3s ease;
        }

        #bookstore-chat-widget.open {
            transform: scale(1);
        }

        #bookstore-chat-header {
            background-color: #2F80ED;
            color: #fff;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
        }

        #bookstore-close-chat {
            cursor: pointer;
            font-size: 20px;
        }

        #bookstore-chat-messages {
            flex-grow: 1;
            padding: 15px;
            overflow-y: auto;
            background-color: #f9f9f9;
        }

        .chat-msg {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 8px;
            max-width: 80%;
            word-wrap: break-word;
        }

        .chat-msg.bot {
            background-color: #E1F0FF;
            color: #000;
            align-self: flex-start;
        }

        .chat-msg.user {
            background-color: #2F80ED;
            color: #fff;
            align-self: flex-end;
            margin-left: auto;
        }

        #bookstore-chat-input-area {
            display: flex;
            padding: 10px;
            border-top: 1px solid #ddd;
            background: #fff;
        }

        #bookstore-chat-input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 20px;
            outline: none;
        }

        #bookstore-chat-send {
            background-color: #2F80ED;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 50%;
            margin-left: 10px;
            cursor: pointer;
        }

        #bookstore-chat-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background-color: #2F80ED;
            color: white;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            z-index: 9999;
            transition: transform 0.2s;
        }

        #bookstore-chat-toggle:hover {
            transform: scale(1.1);
        }

        .typing-indicator {
            display: inline-block;
            width: 20px;
            text-align: center;
        }
        .typing-indicator::after {
            content: '...';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0%, 20% { color: transparent; text-shadow: .25em 0 0 transparent, .5em 0 0 transparent; }
            40% { color: black; text-shadow: .25em 0 0 transparent, .5em 0 0 transparent; }
            60% { text-shadow: .25em 0 0 black, .5em 0 0 transparent; }
            80%, 100% { text-shadow: .25em 0 0 black, .5em 0 0 black; }
        }
    `;
    document.head.appendChild(style);

    const toggleBtn = document.createElement('div');
    toggleBtn.id = 'bookstore-chat-toggle';
    toggleBtn.innerHTML = '💬';

    const widget = document.createElement('div');
    widget.id = 'bookstore-chat-widget';
    widget.innerHTML = `
        <div id="bookstore-chat-header">
            <span>Customer Support</span>
            <span id="bookstore-close-chat">&times;</span>
        </div>
        <div id="bookstore-chat-messages"></div>
        <div id="bookstore-chat-input-area">
            <input type="text" id="bookstore-chat-input" placeholder="Type your message...">
            <button id="bookstore-chat-send">➤</button>
        </div>
    `;

    document.body.appendChild(toggleBtn);
    document.body.appendChild(widget);

    const msgContainer = document.getElementById('bookstore-chat-messages');
    const input = document.getElementById('bookstore-chat-input');
    const sendBtn = document.getElementById('bookstore-chat-send');
    const closeBtn = document.getElementById('bookstore-close-chat');

    toggleBtn.onclick = () => {
        widget.classList.add('open');
        toggleBtn.style.display = 'none';
        input.focus();
    };

    closeBtn.onclick = () => {
        widget.classList.remove('open');
        setTimeout(() => toggleBtn.style.display = 'flex', 300);
    };

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `chat-msg ${sender}`;
        div.innerText = text;
        msgContainer.appendChild(div);
        msgContainer.scrollTop = msgContainer.scrollHeight;
        return div;
    }

    async function sendMessage(text) {
        if(!text.trim()) return;
        
        addMessage(text, 'user');
        input.value = '';

        const loadingMsg = addMessage('', 'bot');
        const typingSpan = document.createElement('span');
        typingSpan.className = 'typing-indicator';
        loadingMsg.appendChild(typingSpan);

        try {
            const res = await fetch('http://localhost:8080/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: 'user_live',
                    query: text
                })
            });

            const data = await res.json();
            msgContainer.removeChild(loadingMsg);
            
            if (data.status === 200) {
                addMessage(data.answer, 'bot');
                if(data.suggested_products && data.suggested_products.length > 0) {
                    addMessage("Ngoài ra, có thể bạn sẽ quan tâm đến một số sản phẩm dưới đây: " + data.suggested_products.join(', '), 'bot');
                }
            } else {
                addMessage("Oops, something went wrong.", 'bot');
            }
        } catch (error) {
            msgContainer.removeChild(loadingMsg);
            addMessage("Server is unreachable.", 'bot');
            console.error(error);
        }
    }

    sendBtn.onclick = () => sendMessage(input.value);
    input.onkeypress = (e) => { if(e.key === 'Enter') sendMessage(input.value); };

    window.triggerProductAction = async function(productId, action) {
        try {
            const res = await fetch('http://localhost:8080/api/signal/action/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ product_id: productId, action: action })
            });
            const data = await res.json();

            if (data.status === 200) {
                widget.classList.add('open');
                toggleBtn.style.display = 'none';
                
                addMessage(data.message, 'bot');
                if(data.predictions && data.predictions.length > 0) {
                    addMessage(data.predictions.join(', '), 'bot');
                }
            }
        } catch (e) {
            console.log("No agent response.");
        }
    }
})();
