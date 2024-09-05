var client_id = Date.now()
document.querySelector("#ws-id").textContent = client_id;
var ws = new WebSocket(`ws://localhost:80/api/video/ws/${client_id}`);
ws.onmessage = function(event) {
    var messages = document.getElementById('messages')
    var message = document.createElement('li')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)
};
function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}

const player = videojs("videoPlayer");

// Seek button and input field
const seekButton = document.getElementById("seekButton");
const seekTimeInput = document.getElementById("seekTime");

// Event listener for the seek button
seekButton.addEventListener("click", () => {
    const seekTime = parseFloat(seekTimeInput.value);
    if (!isNaN(seekTime)) {
        // Seek to the desired time
        player.currentTime(seekTime);
    }
});