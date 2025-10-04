// État de l'application
let currentPair = null;
let comparisonsMade = 0;
let maxComparisons = 50;

// Éléments DOM
const startScreen = document.getElementById('start-screen');
const comparisonScreen = document.getElementById('comparison-screen');
const resultsScreen = document.getElementById('results-screen');
const loading = document.getElementById('loading');

// Fonctions utilitaires
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.add('hidden');
    });
    document.getElementById(screenId).classList.remove('hidden');
}

function showLoading(show = true) {
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

function updateProgress() {
    const progressFill = document.getElementById('progress-fill');
    const percentage = (comparisonsMade / maxComparisons) * 100;
    progressFill.style.width = `${percentage}%`;

    document.getElementById('comparison-count').textContent = comparisonsMade;
    document.getElementById('max-comparisons-display').textContent = maxComparisons;
}

// Gestion du formulaire de démarrage
document.getElementById('start-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const userData = {
        user_name: formData.get('user_name'),
        max_comparisons: parseInt(formData.get('max_comparisons'))
    };

    showLoading(true);

    try {
        const response = await fetch('/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        const result = await response.json();

        if (result.status === 'success') {
            maxComparisons = userData.max_comparisons;
            comparisonsMade = 0;
            showScreen('comparison-screen');
            await loadNextPair();
        } else {
            alert('Erreur lors du démarrage: ' + result.message);
        }
    } catch (error) {
        alert('Erreur de connexion: ' + error.message);
    } finally {
        showLoading(false);
    }
});

// Chargement d'une nouvelle paire
async function loadNextPair() {
    showLoading(true);

    try {
        const response = await fetch('/get_pair');
        const result = await response.json();

        if (result.error) {
            alert('Erreur: ' + result.error);
            return;
        }

        currentPair = result;
        displayPair(result);
        updateProgress();
    } catch (error) {
        alert('Erreur de connexion: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Affichage d'une paire de films
function displayPair(pair) {
    // Film A
    document.getElementById('film-a-genre').textContent = pair.film1.genre;
    document.getElementById('film-a-category').textContent = pair.film1.category;
    document.getElementById('film-a-description').textContent = pair.film1.description;

    // Film B
    document.getElementById('film-b-genre').textContent = pair.film2.genre;
    document.getElementById('film-b-category').textContent = pair.film2.category;
    document.getElementById('film-b-description').textContent = pair.film2.description;
}

// Gestion des choix
async function makeChoice(choice) {
    if (!currentPair) return;

    showLoading(true);

    try {
        const response = await fetch('/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                film1_id: currentPair.film1.id,
                film2_id: currentPair.film2.id,
                result: choice
            })
        });

        const result = await response.json();

        if (result.status === 'success') {
            comparisonsMade = result.comparisons_made;
            updateProgress();

            if (comparisonsMade >= maxComparisons) {
                await finishRanking();
            } else {
                await loadNextPair();
            }
        } else if (result.status === 'skipped') {
            await loadNextPair();
        } else {
            alert('Erreur: ' + result.error);
        }
    } catch (error) {
        alert('Erreur de connexion: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Finalisation du classement
async function finishRanking() {
    showLoading(true);

    try {
        const response = await fetch('/finish');
        const result = await response.json();

        if (result.status === 'success') {
            displayResults(result);
            showScreen('results-screen');
        } else {
            alert('Erreur lors de la finalisation: ' + result.error);
        }
    } catch (error) {
        alert('Erreur de connexion: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Affichage des résultats
function displayResults(data) {
    document.getElementById('final-comparisons').textContent = data.comparisons_made;
    document.getElementById('final-confidence').textContent = Math.round(data.confidence * 100) + '%';

    const tbody = document.getElementById('results-tbody');
    tbody.innerHTML = '';

    data.results.forEach(film => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${film.rank}</td>
            <td>${film.description}</td>
            <td>${film.genre}</td>
            <td>${film.category}</td>
            <td>${film.score_mu}</td>
            <td>${Math.round(film.confidence * 100)}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Event listeners pour les boutons
document.querySelectorAll('.btn-film').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const choice = parseInt(e.target.getAttribute('data-choice'));
        makeChoice(choice);
    });
});

document.getElementById('equal-btn').addEventListener('click', () => {
    makeChoice(3);
});

document.getElementById('skip-btn').addEventListener('click', () => {
    makeChoice(0);
});

document.getElementById('stop-btn').addEventListener('click', () => {
    if (confirm('Êtes-vous sûr de vouloir arrêter le classement ?')) {
        finishRanking();
    }
});

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    showScreen('start-screen');
});
