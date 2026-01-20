
// 1. [VALUE DECLARATION] - 요소 선언
const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const inputContainer = document.getElementById('input-container');

// ---------------------------------------------------------

// 2. [MAIN LOOP] - 이벤트 리스너 (엔터키 반응 포함)
// 전송 버튼 클릭 시
sendButton.addEventListener('click', sendMessage);

// 입력창에서 엔터키 눌렀을 때 (수정된 부분)
userInput.addEventListener('keydown', (e) => {
    // e.key가 'Enter'이고, 전송 중이 아닐 때만 실행
    if (e.key === 'Enter' && !sendButton.disabled) {
        sendMessage();
    }
});

// ---------------------------------------------------------

// 3. [FUNCTION DECLARATION] - 실행 함수들
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage('user', message); // 화면에 내 글 표시
    userInput.value = '';        // 입력창 비우기
    
    setLoading(true);            // [인자: true - 로딩 시작]

    const reply = await askServer(message); // [인자: message - 사용자 질문]
    addMessage('ai', reply);      // 화면에 AI 답장 표시

    setLoading(false);           // [인자: false - 로딩 끝]
}

// 서버와 대화하는 함수
async function askServer(msg) {
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg })
        });
        const data = await response.json();
        return data.reply;
    } catch (e) {
        return "서버와 연결할 수 없습니다.";
    }
}

// 에러가 났던 setLoading 함수를 여기에 정의합니다.
function setLoading(isLoading) {
    if (isLoading) {
        sendButton.disabled = true;
        if(inputContainer) inputContainer.classList.add('loading');
    } else {
        sendButton.disabled = false;
        if(inputContainer) inputContainer.classList.remove('loading');
        userInput.focus();
    }
}

function addMessage(sender, text) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.innerHTML = `<div class="message-bubble">${text}</div>`;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
