const PHASES = {
    PRE_GAME: "pre_game",
    DRAW: "draw",
    CHOOSE: "choose",
    BATTLE: "battle",
    RESULT: "result",
    END: "end"
};

const avatar1 = document.getElementById('avatar-1');
const avatar2 = document.getElementById('avatar-2');
const hp1 = document.getElementById('hp-p1');
const hp2 = document.getElementById('hp-p2');
const tooltip = document.getElementById("global-tooltip");
const fase = document.getElementById("phase-view");

function initializeTooltips() {
    document.addEventListener("mousemove", (e) => {
        const card = e.target.closest(".card");
        const hpbar1 = e.target.closest(".player-left");
        const hpbar2 = e.target.closest(".player-right");
        const ler_tooltip = e.target.closest(".ler_tooltip");
        if ((!card || !card.dataset.tooltip) && !hpbar1 && !hpbar2 && !ler_tooltip) {
            tooltip.classList.remove("show");
            return;
        } 
        
        if (card) {
            tooltip.innerHTML = card.dataset.tooltip.replace(/\n/g, "<br>");
        } else if (hpbar1) {
            tooltip.innerHTML = player_1['hp']+"/20";
        } else if (hpbar2) {
            tooltip.innerHTML = player_2['hp']+"/20";
        } else if (ler_tooltip) {
            tooltip.innerHTML = ler_tooltip.dataset.tooltip
        }
        
        tooltip.style.left = `${e.clientX + 16}px`;
        tooltip.style.top = `${e.clientY + 16}px`;
        tooltip.classList.add("show");
    });

    document.addEventListener("mouseleave", () => {
        tooltip.classList.remove("show");
    });
}

function configUserView() {
    avatar1.src = STATIC_URL + "player_icons/" + player_1.icone;
    avatar2.src = STATIC_URL + "player_icons/" + player_2.icone;

    hp1.style.width = `${(player_1.hp / 20) * 100}%`;
    hp2.style.width = `${(player_2.hp / 20) * 100}%`;
}

async function gameFlow() {
    console.log(game_state['phase'])
    if (game_state['phase'] == "pre_game") {
        await shuffle_animation();
        if (game_state.host == userId){
            socket.emit("fist_draw", {
                room_id: game_state.room_id
            });
        };
    } else if (game_state['phase'] == "choose" || game_state['phase'] == "fist_choose") {
        if (game_state['mode'] == 'pvp')                {
            startCrono();
        };
        enableCardSelection();
    } else if (game_state['phase'] == "battle" && game_state.host == userId) {
        socket.emit("combate_resolver", {
            room_id: game_state.room_id
        })
    } else if (game_state['phase'] == "battle_resolve" && game_state.host == userId) {
        socket.emit("end_turn", {
            room_id: game_state.room_id
        })
    } else if (game_state['phase'] == "draw" && game_state.host == userId) {
        socket.emit("draw", {
            room_id: game_state.room_id
        })
    }
}

function get_description(cardData){
    text = COMBAT_TIPS[cardData.classe]
    text = text + "\n"
    text = text + COMBAT_TIPS[cardData.subclasse]
    text = text + "."
    return text
}

function start_turn(){
    fase.innerText = "Turno " + game_state['round']
}

function update_life() {
    hp1.style.width = ((player_1.hp / 20) * 100) + "%";
    hp2.style.width = ((player_2.hp / 20) * 100) + "%";
}

// CARDS SELECTS ===============================
function enableCardSelection() {
    const cards = document.querySelectorAll(".card");
    cards.forEach(card => {
        card.onclick = () => {
            // evita múltiplos cliques
            if (game_state.phase !== "choose" && game_state.phase !== "fist_choose" && card.classList.contains('not-selected-card')) return;
            const cardId = card.dataset.id;

            // destaque visual
            document.querySelectorAll(".card").forEach(c => {
                c.classList.remove("selected");
            });
            card.classList.add("selected");

            if (game_state.mode == 'pvp'){
                stopCrono();
            };

            // enviar ao backend
            socket.emit("select_card", {
                room_id: game_state.room_id,
                card_id: cardId
            });
        };
    });
}

function disableCardSelection() {
    const cards = document.querySelectorAll(".card");

    cards.forEach(card => {
        card.onclick = null;
        card.classList.remove("selected");
    });
}

// ELEMENTOS VISUAIS ============================
function createCardElement(cardData) {
    const card = document.createElement("div");
    console.log(cardData)
    // classes da carta
    card.classList.add(
        "card",
        cardData.classe.toLowerCase(),
        cardData.raridade?.toLowerCase() || "comum"
    );
    if (cardData.foil){
        card.classList.add('foil')
    }
    card.dataset.id = cardData.carta_id;

    card.innerHTML = `
        <div class="card-nome">
            ${cardData.carta_nome}
        </div>

        <div class="card-img">
            <img src="${STATIC_URL}images/${cardData.carta_img}" alt="${cardData.carta_nome}">
        </div>

        <div class="card-texto">
            <span>${DICT_LANG[cardData.classe]}</span>
            <span>${DICT_LANG[cardData.subclasse]}</span>
        </div>
    `;
    card.dataset.tooltip = get_description(cardData);
    return card;
}

function createEffectElement(effectName, amount) {
    const effect = document.createElement("div");
    effect.classList.add("mini-effect");
    effect.innerHTML = `
        <div class="mini-effect-orb ${effectName}"></div>
        <span>${amount}x ${effectName}</span>
    `;

    return effect;
};

async function createEffectsBattleOne(effectsData) {
    const effectsP1 = document.getElementById("effects-p1");
    const effectsP2 = document.getElementById("effects-p2");

    // limpa efeitos antigos
    effectsP1.innerHTML = "";
    effectsP2.innerHTML = "";

    // pega ids recebidos
    const playerIds = Object.keys(effectsData);

    const player1Id = playerIds[0];
    const player2Id = playerIds[1];

    // define visão do jogador
    const myEffects =
        userId == player1Id
            ? effectsData[player1Id]
            : effectsData[player2Id];

    const enemyEffects =
        userId == player1Id
            ? effectsData[player2Id]
            : effectsData[player1Id];

    // remove efeitos zerados
    const myEffectsArray = Object.entries(myEffects)
        .filter(([_, amount]) => amount > 0);

    const enemyEffectsArray = Object.entries(enemyEffects)
        .filter(([_, amount]) => amount > 0);

    // pega maior quantidade
    const maxEffects = Math.max(
        myEffectsArray.length,
        enemyEffectsArray.length
    );

    // renderiza em ondas
    for (let i = 0; i < maxEffects; i++) {
        const tooltip_list = ['ataque futuro', 'revitalizar', 'descuido', 'debilitar']
        // PLAYER
        if (myEffectsArray[i]) {
            const [effectName, amount] = myEffectsArray[i];
            const effectElement = createEffectElement(effectName, amount);

            if (tooltip_list.includes(effectName)){
                effectElement.classList.add("ler_tooltip");
                effectElement.dataset.tooltip = COMBAT_TIPS[effectName];
            }
            effectsP1.appendChild(effectElement);
        }

        // OPONENTE
        if (enemyEffectsArray[i]) {
            const [effectName, amount] = enemyEffectsArray[i];
            const effectElement = createEffectElement(effectName, amount);

            if (tooltip_list.includes(effectName)){
                effectElement.classList.add("ler_tooltip");
                effectElement.dataset.tooltip = COMBAT_TIPS[effectName];
            }
            effectsP2.appendChild(effectElement);
        }

        await new Promise(resolve => setTimeout(resolve, 500));
    }
};

async function check_continuous_effects(changes) {
    const changeData = changes[player_1.id];
    if (Object.values(changeData['battle_continuous']).some(valor => valor > 0)) {
        const effects = changeData['battle_continuous'];
        const area_div = document.getElementById('cont-slot-p1');

        for (let key in effects){
            if (effects[key] > 0){
                const effectElement = createEffectElement(key, effects[key]);
                effectElement.classList.add("ler_tooltip");
                effectElement.dataset.tooltip = COMBAT_TIPS[key]
                area_div.appendChild(effectElement)
            }
        }
    }
    const changeData2 = changes[player_2.id];
    if (Object.values(changeData2['battle_continuous']).some(valor => valor > 0)) {
        const effects = changeData2['battle_continuous'];
        const area_div = document.getElementById('cont-slot-p2');

        for (let key in effects){
            if (effects[key] > 0){
                const effectElement = createEffectElement(key, effects[key]);
                effectElement.classList.add("ler_tooltip");
                effectElement.dataset.tooltip = COMBAT_TIPS[key]
                area_div.appendChild(effectElement)
            }
        }
    }
}

// JOGO ==================
socket.emit("join_room", {
    room_id: game_state.room_id,
    user_id: player_1.id
});

initializeTooltips();
configUserView();
gameFlow();