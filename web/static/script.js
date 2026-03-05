const renderer = {
    link(href, title, text) {
        const link = marked.Renderer.prototype.link.call(this, href, title, text);

        return link.replace("<a", "<a target='_blank' rel='noreferrer'");
    },
};

marked.use({
    renderer,
});


const generateSessionId = () => {
    const timestamp = Date.now();
    const randomString = Math.random().toString(36).substring(2, 9);
    return `session_${timestamp}_${randomString}`;
};


const ChatApp = {
    elements: {
        chatForm: null,
        chatInput: null,
        chatBox: null,
    },

    sessionId: null,

    init() {
        this.elements.chatForm = document.getElementById("chat-form");
        this.elements.chatInput = document.getElementById("chat-input");
        this.elements.chatBox = document.getElementById("chat-box");

        this.sessionId = generateSessionId();
        console.log("새로운 세션 ID:", this.sessionId);

        this.elements.chatForm.addEventListener(
            "submit",
            this.handleFormSubmit.bind(this)
        );

    },

    async handleFormSubmit(e) {
        e.preventDefault();
        const message = this.elements.chatInput.value.trim();

        if(!message) {
            return;
        }

        this.appendMessage("user", message);
        this.elements.chatInput.value = "";

        const botMessageElement = this.createMessageElement("bot");
        await this.streamBotResponse(message, botMessageElement);
    },

    async streamBotResponse(message, botMessageElement) {
        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type" : "application/x-www-form-urlencoded"},
                body: new URLSearchParams({
                    message: message,
                    session_id: this.sessionId,
                }),
            });

            if(!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let content = "";

            while(true) {
                const{value, done} = await reader.read();

                if(done) break;

                content += decoder.decode(value, {stream: true});
                botMessageElement.innerHTML = marked.parse(content);
                this.scrollToBottom();
            }
        }catch(error) {
            console.error("스트리밍 중 오류 발생:", error);
            botMessageElement.innerHTML = "죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다.";
        }
    },


    createMessageElement(sender) {
        const messageElemenet = document.createElement("div");
        messageElemenet.classList.add("message", `${sender}-message`);
        this.elements.chatBox.appendChild(messageElemenet);
        this.scrollToBottom();
        return messageElemenet;
    },

    appendMessage(sender, text) {
        const messageElement = this.createMessageElement(sender);
        messageElement.innerHTML = marked.parse(text);
    },

    scrollToBottom() {
        this.elements.chatBox.scrollTop = this.elements.chatBox.scrollHeight;
    },

};

document.addEventListener("DOMContentLoaded", () => {
    ChatApp.init();
});

