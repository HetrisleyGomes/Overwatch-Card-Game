// TIMER ==============
let timerValue = 30;
let timerInterval = null;
let playerReady = false;
const timerElement = document.getElementById("timer");

function startCrono() {
    playerReady = false;
    timerValue = 30;

    timerElement.textContent = timerValue;
    clearInterval(timerInterval);

    timerInterval = setInterval(() => {
        timerValue--;
        timerElement.textContent = timerValue;
        if (timerValue <= 0) {
            clearInterval(timerInterval);
            socket.emit("time_out", {
                room_id: game_state.room_id,
                user_id: userId,
                has_selected: playerReady
            });
        }
    }, 1000);
}

function stopCrono() {
    console.log("sotpeed")
    playerReady = true;
}

function resetCrono() {
    clearInterval(timerInterval);
    timerValue = 30;
    playerReady = false;
    timerElement.textContent = "30";
}