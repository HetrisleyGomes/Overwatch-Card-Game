// ANIMAÇÕES ==============================================
function shuffle_animation() {
    return new Promise((resolve) => {
        const deck = document.getElementById("deck");

        // Remove caso já tenha
        deck.classList.remove("shuffling");

        // Força reflow pra reiniciar animação
        void deck.offsetWidth;

        // Adiciona animação
        deck.classList.add("shuffling");

        // Tempo da animação
        setTimeout(() => {
            deck.classList.remove("shuffling");
            resolve();
        }, 800);
    });
}

async function drawCard(cardData) {
    return new Promise((resolve) => {
        const deck = document.getElementById("deck");
        const hand = document.getElementById("hand");

        // posição do deck
        const deckRect = deck.getBoundingClientRect();

        // cria carta animada
        const animatedCard = createCardElement(cardData);
        animatedCard.classList.add("draw-card");

        // começa em cima do deck
        animatedCard.style.left = `${deckRect.left}px`;
        animatedCard.style.top = `${deckRect.top}px`;
        animatedCard.style.transform = "scale(0.3) rotate(-10deg)";
        animatedCard.style.opacity = "0";
        document.body.appendChild(animatedCard);

        // força render
        requestAnimationFrame(() => {
            // aparece
            animatedCard.style.opacity = "1";

            // posição alvo (final da mão)
            const handRect = hand.getBoundingClientRect();
            const cardIndex = hand.children.length;
            const targetX = handRect.left + (cardIndex * 240);
            const targetY = handRect.top;
            animatedCard.style.left = `${targetX}px`;
            animatedCard.style.top = `${targetY}px`;
            animatedCard.style.transform = "scale(1) rotate(0deg)";
        });

        // terminou animação
        setTimeout(() => {
            // adiciona carta real na mão
            const realCard = createCardElement(cardData);
            hand.appendChild(realCard);
            // remove temporária
            animatedCard.remove();
            resolve();
        }, 500);
    });
}

async function draw_five_cards_animation(player) {
    const hand = document.getElementById("hand");

    // limpa mão antes
    hand.innerHTML = "";
    for (const card of player.hand) {
        await drawCard(card);

        // pequeno delay entre compras
        await new Promise(resolve => setTimeout(resolve, 150));
    }
}

function animateCardToTarget(cardElement, targetElement) {
    return new Promise((resolve) => {
        const rectStart = cardElement.getBoundingClientRect();
        const rectTarget = targetElement.getBoundingClientRect();

        // clona a carta
        const animatedCard = cardElement.cloneNode(true);

        animatedCard.classList.add("draw-card");
        animatedCard.style.position = "fixed";
        animatedCard.style.left = `${rectStart.left}px`;
        animatedCard.style.top = `${rectStart.top}px`;
        animatedCard.style.width = `${rectStart.width}px`;
        animatedCard.style.height = `${rectStart.height}px`;
        animatedCard.style.zIndex = "9999";

        document.body.appendChild(animatedCard);

        // esconde original
        cardElement.style.visibility = "hidden";

        requestAnimationFrame(() => {
            animatedCard.style.transition = `
                left 0.5s ease,
                top 0.5s ease,
                transform 1s ease
            `;

            animatedCard.style.left = `${rectTarget.left}px`;
            animatedCard.style.top = `${rectTarget.top}px`;
            animatedCard.style.transform = "scale(1.05)";
        });

        setTimeout(() => {
            animatedCard.remove();
            resolve();
        }, 500);
    });
}

async function startBattleAnimation(battleData) {
    const player1Card = battleData[player_1.id];
    const player2Card = battleData[player_2.id];

    const slotP1 = document.getElementById("slot-p1");
    const slotP2 = document.getElementById("slot-p2");

    document.getElementById("cont-slot-p1").innerHTML = "";
    document.getElementById("cont-slot-p2").innerHTML = "";

    // CARTA DO JOGADOR
    const playerCard = document.querySelector(
        `.hand .card[data-id="${player1Card.carta_id}"]`
    );
    playerCard.classList.remove("selected");

    // CARTA DO OPONENTE
    const enemyCard = createCardElement(player2Card);

    // cria perto do avatar inimigo
    const avatar2 = document.getElementById("avatar-2");
    const avatarRect = avatar2.getBoundingClientRect();

    enemyCard.classList.add("draw-card");
    enemyCard.style.position = "fixed";
    enemyCard.style.left = `${avatarRect.left}px`;
    enemyCard.style.top = `${avatarRect.top}px`;
    enemyCard.style.width = "180px";
    enemyCard.style.height = "250px";
    enemyCard.style.zIndex = "9999";

    document.body.appendChild(enemyCard);

    // ANIMAÇÕES AO MESMO TEMPO
    await Promise.all([
        animateCardToTarget(playerCard, slotP1),
        animateCardToTarget(enemyCard, slotP2)
    ]);

    // ADICIONA CARTAS NOS SLOTS
    slotP1.innerHTML = "";
    slotP2.innerHTML = "";

    // carta jogador
    slotP1.appendChild(playerCard);
    playerCard.style.visibility = "visible";

    // carta inimiga
    const enemyFinalCard = createCardElement(player2Card);
    slotP2.appendChild(enemyFinalCard);
    enemyCard.remove()
}

function animateDrop(cardElement) {
    return new Promise((resolve) => {
        const rect = cardElement.getBoundingClientRect();

        // clone animado
        const clone = cardElement.cloneNode(true);

        clone.classList.add("dropping-card");
        clone.style.left = `${rect.left}px`;
        clone.style.top = `${rect.top}px`;
        clone.style.width = `${rect.width}px`;
        clone.style.height = `${rect.height}px`;
        clone.style.animation = `
            dropCard 0.8s forwards
        `;

        document.body.appendChild(clone);

        // remove original
        cardElement.remove();
        setTimeout(() => {
            clone.remove();
            resolve();
        }, 800);
    });
}
async function drop_cards_animation() {
    const slotP1 = document.getElementById("slot-p1");
    const slotP2 = document.getElementById("slot-p2");
    const discard = document.querySelector(".discard");

    // pega cartas
    const card1 = slotP1.querySelector(".card");
    const card2 = slotP2.querySelector(".card");

    // guarda clones para descarte
    const discardCards = [];

    if (card1) {
        discardCards.push(card1.cloneNode(true));
    }

    // anima simultaneamente
    await Promise.all([
        card1 ? animateDrop(card1) : Promise.resolve(),
        card2 ? animateDrop(card2) : Promise.resolve()

    ]);

    // adiciona mini pilha no descarte
    discardCards.forEach((card, index) => {
        const mini = card.cloneNode(true);
        mini.classList.add("not-selected-card")
        mini.style.position = "absolute";
        mini.style.left = `${(index * 4) -40}px`;
        mini.style.top = `${(index * -4) -50}px`;
        mini.style.transform = `
            scale(0.6)
            rotate(${(Math.random() * 16) - 8}deg)
            translateY(${Math.random() * 6}px)
        `;
        discard.appendChild(mini);
    });

    document.getElementById("effects-p1").innerHTML = "";
    document.getElementById("effects-p2").innerHTML = "";
}

function showBattleChange(targetElement, changeData) {
    console.log(changeData)
    const number = document.createElement("div");
    number.classList.add("floating-number");
    // tipo
    if (changeData.type === "damaged") {
        number.classList.add("damage");
        number.textContent = `-${changeData.value}`;
    }
    else if (changeData.type === "healed") {
        number.classList.add("heal");
        number.textContent = `+${changeData.value}`;
    }
    else {
        number.classList.add("neutral");
        number.textContent = "0";
    }

    // posição
    const rect = targetElement.getBoundingClientRect();
    number.style.left = `${rect.left + rect.width / 2}px`;
    number.style.top = `${rect.top}px`;
    number.style.fontSize = "40px";
    number.style.fontWeight = 700;
    document.body.appendChild(number);

    // remover depois
    setTimeout(() => {
        number.remove();
    }, 1000);
};