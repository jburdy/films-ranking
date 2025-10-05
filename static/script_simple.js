// Version simplifiée du script pour débugger
console.log('Script chargé');

// Fonctions utilitaires
function showScreen(screenId) {
    console.log('Affichage de l\'écran:', screenId);
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });
    document.getElementById(screenId).classList.remove('hidden');
}

function showLoading(show = true) {
    console.log('Loading:', show);
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

// Initialisation immédiate
console.log('Initialisation...');
showScreen('start-screen');
showLoading(false);
console.log('Initialisation terminée');

// Gestion du formulaire
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM chargé');

    const form = document.getElementById('start-form');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            console.log('Formulaire soumis');
            alert('Formulaire soumis - fonctionnalité en cours de développement');
        });
    } else {
        console.error('Formulaire non trouvé');
    }
});
