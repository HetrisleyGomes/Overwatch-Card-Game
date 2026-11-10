// MÚSICA ==================
const music = document.getElementById("background-music");

async function loadThemeMusic(theme=null) {
    try {
        const response = await fetch("/api/theme-music/combate");
        if (!response.ok) {
            throw new Error("Erro ao buscar música do tema");
        }

        const data = await response.json();
        if (!data.url) {
            return;
        }

        savedTrack = data.url;
        music.src = savedTrack;
        music.load();
    } catch (error) {
        console.error("Não foi possível carregar a música do tema:", error);
    }
};
loadThemeMusic();