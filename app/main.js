const chatBox = document.querySelector(".chat-box");
const inputField = chatBox.querySelector("input[type='text']");
const sendButton = chatBox.querySelector("#sendButton");
const micButton = chatBox.querySelector("#micButton"); // make sure to add this element in your HTML
const chatBoxBody = chatBox.querySelector(".chat-box-body");

sendButton.addEventListener("click", sendMessage);
inputField.addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

let mediaRecorder;
let audioChunks = [];
let currentlyPlayingAudio = null;

inputField.addEventListener("input", function () {
  // Stop the currently playing audio (if any)
  if (currentlyPlayingAudio) {
    currentlyPlayingAudio.pause();
    currentlyPlayingAudio.currentTime = 0;
    currentlyPlayingAudio = null;
  }
});

micButton.addEventListener('click', () => {
  // Stop the currently playing audio (if any)
  if (currentlyPlayingAudio) {
    currentlyPlayingAudio.pause();
    currentlyPlayingAudio.currentTime = 0;
    currentlyPlayingAudio = null;
  }
  if (!mediaRecorder) {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        micButton.style.backgroundColor = "red"; // the mic button turns red when recording

        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
        });

        mediaRecorder.addEventListener("stop", () => {
          const audioData = new Blob(audioChunks, { type: 'audio/wav' });
          audioChunks = [];
          sendAudioMessage(audioData);
        });
      });
  } else {
    mediaRecorder.stop();
    mediaRecorder = null;

    micButton.style.backgroundColor = ""; // the mic button returns to its original color when not recording
  }
});

let dots;

function sendMessage() {
  const message = inputField.value;
  inputField.value = "";
  chatBoxBody.innerHTML += `<div class="message"><p>${message}</p></div>`;
  chatBoxBody.innerHTML += `<div id="loading" class="response loading">.</div>`;
  scrollToBottom();
  window.dotsGoingUp = true;
  dots = window.setInterval(function () {
    var wait = document.getElementById("loading");
    if (window.dotsGoingUp)
      wait.innerHTML += ".";
    else {
      wait.innerHTML = wait.innerHTML.substring(1, wait.innerHTML.length);
      if (wait.innerHTML.length < 2)
        window.dotsGoingUp = true;
    }
    if (wait.innerHTML.length > 3)
      window.dotsGoingUp = false;
  }, 250);

  fetch('http://localhost:3010/message', {
    method: 'POST',
    headers: {
      accept: 'application.json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  }).then(response => {
    return response.json();
  }).then(data => {
    document.getElementById("loading").remove();
    window.clearInterval(dots);
    const formattedResponse = data.message.replace(/\n/g, '<br>');
    chatBoxBody.innerHTML += `<div class="response"><p>${formattedResponse}</p></div>`;
    scrollToBottom();
  })
}

function sendAudioMessage(audioData) {
  const formData = new FormData();
  formData.append('file', audioData, 'message.wav');

  fetch('http://localhost:3010/transcribe_audio', {
    method: 'POST',
    body: formData
  }).then(response => response.json())
    .then(data => {
      chatBoxBody.innerHTML += `<div class="message"><p>${data.transcript}</p></div>`; // Display the transcript first
      scrollToBottom();

      // Add the loading div after the transcript
      chatBoxBody.innerHTML += `<div id="loading" class="response loading">.</div>`;
      scrollToBottom();
      window.dotsGoingUp = true;
      dots = window.setInterval(function () {
        var wait = document.getElementById("loading");
        if (window.dotsGoingUp)
          wait.innerHTML += ".";
        else {
          wait.innerHTML = wait.innerHTML.substring(1, wait.innerHTML.length);
          if (wait.innerHTML.length < 2)
            window.dotsGoingUp = true;
        }
        if (wait.innerHTML.length > 3)
          window.dotsGoingUp = false;
      }, 250);

      getBotResponse(data.transcript); // Get the bot response
    });
}

function getBotResponse(message) {
  fetch('http://localhost:3010/message', {
    method: 'POST',
    headers: {
      accept: 'application.json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  })
    .then(response => {
      return response.json();
    })
    .then(data => {
      document.getElementById("loading").remove();  // remove the loading div
      window.clearInterval(dots);  // clear the interval
      const formattedResponse = data.message.replace(/\n/g, '<br>');
      chatBoxBody.innerHTML += `<div class="response"><p>${formattedResponse}</p></div>`;
      // Add an HTML audio element to play the audio file
      const audioElement = document.createElement("audio");
      const timestamp = new Date().getTime();  // get a unique timestamp
      audioElement.src = `${data.audio}?t=${timestamp}`;  // append the timestamp as a query string
      chatBoxBody.appendChild(audioElement);
      audioElement.addEventListener('loadedmetadata', function () {
        audioElement.play();
      });

      // Assign the new audio element to currentlyPlayingAudio
      currentlyPlayingAudio = audioElement;

      // Clear the currentlyPlayingAudio variable when the audio finishes
      audioElement.addEventListener('ended', function () {
        currentlyPlayingAudio = null;
      });

      scrollToBottom();
    });
}


function playAudio(audio_id) {
  const audio = document.getElementById(audio_id);
  audio.play();
}

function scrollToBottom() {
  chatBoxBody.scrollTop = chatBoxBody.scrollHeight;
}
