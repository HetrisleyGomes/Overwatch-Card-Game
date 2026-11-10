// SOCKETS =================================================
socket.on("game_state", async (data) => {
    game_state = data.game_state;
    start_turn();
    player_1 = data.players.find(j => j.id == userId);
    player_2 = data.players.find(j => j.id != userId);

    if (game_state.phase == "fist_choose") {
        await draw_five_cards_animation(player_1);
    } else {
        await drawCard(player_1['hand'][4]);
    }
    gameFlow();
});

socket.on("battle_phase_one", async (data) => {
    game_state.phase = data.game_state_phase;
    disableCardSelection();
    start_turn();
    if (game_state['mode'] == 'pvp'){
        resetCrono();
    };
    await startBattleAnimation(data.selected_cards);
    await createEffectsBattleOne(data.result_values);
    await new Promise(resolve => setTimeout(resolve, 1000));
    gameFlow();
});

socket.on("battle_phase_two", async (data) => {
    game_state = data.game_state;
    player_1 = data.players.find(j => j.id == userId);
    player_2 = data.players.find(j => j.id != userId);
    const changes = data.changes
    start_turn();
    showBattleChange(
        hp1,
        changes[player_1.id]
    );
    showBattleChange(
        hp2,
        changes[player_2.id]
    );
    update_life();
    await check_continuous_effects(changes);
    gameFlow();
});

socket.on("end_turn", async (data) => {
    game_state = data.game_state;
    start_turn();
    await drop_cards_animation();
    gameFlow();
});

socket.on("enemy_disconnect", (data) => {
    alert(data.msg);
    fetch("/set-battle-result", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            result: "victory",
            winner: userId,
            sala: game_state.room_id
        })
    }).then(() => {
        window.location.href = "/battle/finally";
    });
});

socket.on("victory", async(data) => {
    await drop_cards_animation();
    id_winner = data.winner_id
    if (id_winner == userId) {
        fetch("/set-battle-result", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                result: "victory",
                winner: id_winner,
                sala: game_state.room_id
            })
        }).then(() => {
            window.location.href = "/battle/finally";
        });
    } else {
        fetch("/set-battle-result", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                result: "lose",
                winner: id_winner,
                sala: game_state.room_id
            })
        }).then(() => {
            window.location.href = "/battle/finally";
        });
    }

});
socket.on("empate", () => {
    fetch("/set-battle-result", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            result: "empate",
            sala: game_state.room_id
        })
    }).then(() => {
        window.location.href = "/battle/finally";
    });
});