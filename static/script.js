// État de l'application
var currentPair = null;
var comparisonsMade = 0;
var maxComparisons = 50;

// Fonctions utilitaires
function showScreen(screenId) {
    var screens = document.querySelectorAll('.screen');
    for (var i = 0; i < screens.length; i++) {
        screens[i].classList.add('hidden');
    }
    var targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.remove('hidden');
    }
}

function showLoading(show) {
    if (typeof show === 'undefined') show = true;
    var loading = document.getElementById('loading');
    if (loading) {
        if (show) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }
}

function updateProgress() {
    var progressFill = document.getElementById('progress-fill');
    if (progressFill) {
        var percentage = (comparisonsMade / maxComparisons) * 100;
        progressFill.style.width = percentage + '%';
    }

    var comparisonCount = document.getElementById('comparison-count');
    var maxComparisonsDisplay = document.getElementById('max-comparisons-display');
    if (comparisonCount) comparisonCount.textContent = comparisonsMade;
    if (maxComparisonsDisplay) maxComparisonsDisplay.textContent = maxComparisons;
}

// Fonction pour faire des requêtes HTTP
function makeRequest(url, options) {
    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        var method = (options && options.method) ? options.method : 'GET';
        xhr.open(method, url);

        if (options && options.headers) {
            for (var header in options.headers) {
                xhr.setRequestHeader(header, options.headers[header]);
            }
        }

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    resolve(response);
                } catch (e) {
                    reject(new Error('Erreur de parsing JSON'));
                }
            } else {
                reject(new Error('Erreur HTTP: ' + xhr.status));
            }
        };

        xhr.onerror = function () {
            reject(new Error('Erreur de connexion'));
        };

        if (options && options.body) {
            xhr.send(options.body);
        } else {
            xhr.send();
        }
    });
}

// Gestion du formulaire de démarrage
function initForm() {
    var form = document.getElementById('start-form');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            var formData = new FormData(e.target);
            var userData = {
                user_name: formData.get('user_name'),
                max_comparisons: parseInt(formData.get('max_comparisons'))
            };

            showLoading(true);

            makeRequest('/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            })
                .then(function (result) {
                    if (result.status === 'success') {
                        maxComparisons = userData.max_comparisons;
                        comparisonsMade = 0;
                        showScreen('comparison-screen');
                        loadNextPair();
                    } else {
                        alert('Erreur lors du démarrage: ' + result.message);
                        showLoading(false);
                    }
                })
                .catch(function (error) {
                    alert('Erreur de connexion: ' + error.message);
                    showLoading(false);
                });
        });
    }
}

// Chargement d'une nouvelle paire
function loadNextPair() {
    showLoading(true);

    makeRequest('/get_pair')
        .then(function (result) {
            if (result.error) {
                alert('Erreur: ' + result.error);
                showLoading(false);
                return;
            }

            currentPair = result;
            displayPair(result);
            updateProgress();
            showLoading(false);
        })
        .catch(function (error) {
            alert('Erreur de connexion: ' + error.message);
            showLoading(false);
        });
}

// Affichage d'une paire de films
function displayPair(pair) {
    var filmAGenre = document.getElementById('film-a-genre');
    var filmACategory = document.getElementById('film-a-category');
    var filmADescription = document.getElementById('film-a-description');

    if (filmAGenre) filmAGenre.textContent = pair.film1.genre;
    if (filmACategory) filmACategory.textContent = pair.film1.category;
    if (filmADescription) filmADescription.textContent = pair.film1.description;

    var filmBGenre = document.getElementById('film-b-genre');
    var filmBCategory = document.getElementById('film-b-category');
    var filmBDescription = document.getElementById('film-b-description');

    if (filmBGenre) filmBGenre.textContent = pair.film2.genre;
    if (filmBCategory) filmBCategory.textContent = pair.film2.category;
    if (filmBDescription) filmBDescription.textContent = pair.film2.description;
}

// Gestion des choix
function makeChoice(choice) {
    if (!currentPair) return;

    showLoading(true);

    makeRequest('/compare', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            film1_id: currentPair.film1.id,
            film2_id: currentPair.film2.id,
            result: choice
        })
    })
        .then(function (result) {
            if (result.status === 'success') {
                comparisonsMade = result.comparisons_made;
                updateProgress();

                if (comparisonsMade >= maxComparisons) {
                    finishRanking();
                } else {
                    loadNextPair();
                }
            } else if (result.status === 'skipped') {
                loadNextPair();
            } else {
                alert('Erreur: ' + result.error);
                showLoading(false);
            }
        })
        .catch(function (error) {
            alert('Erreur de connexion: ' + error.message);
            showLoading(false);
        });
}

// Finalisation du classement
function finishRanking() {
    showLoading(true);

    makeRequest('/finish')
        .then(function (result) {
            if (result.status === 'success') {
                displayResults(result);
                showScreen('results-screen');
            } else {
                alert('Erreur lors de la finalisation: ' + result.error);
            }
            showLoading(false);
        })
        .catch(function (error) {
            alert('Erreur de connexion: ' + error.message);
            showLoading(false);
        });
}

// Affichage des résultats
function displayResults(data) {
    var finalComparisons = document.getElementById('final-comparisons');
    var finalConfidence = document.getElementById('final-confidence');

    if (finalComparisons) finalComparisons.textContent = data.comparisons_made;
    if (finalConfidence) finalConfidence.textContent = Math.round(data.confidence * 100) + '%';

    var tbody = document.getElementById('results-tbody');
    if (tbody) {
        tbody.innerHTML = '';

        for (var i = 0; i < data.results.length; i++) {
            var film = data.results[i];
            var row = document.createElement('tr');
            row.innerHTML =
                '<td>' + film.rank + '</td>' +
                '<td>' + film.description + '</td>' +
                '<td>' + film.genre + '</td>' +
                '<td>' + film.category + '</td>' +
                '<td>' + film.score_mu + '</td>' +
                '<td>' + Math.round(film.confidence * 100) + '%</td>';
            tbody.appendChild(row);
        }
    }
}

// Initialisation des event listeners
function initEventListeners() {
    // Boutons de choix des films
    var filmButtons = document.querySelectorAll('.btn-film');
    for (var i = 0; i < filmButtons.length; i++) {
        filmButtons[i].addEventListener('click', function (e) {
            var choice = parseInt(e.target.getAttribute('data-choice'));
            makeChoice(choice);
        });
    }

    // Bouton égalité
    var equalBtn = document.getElementById('equal-btn');
    if (equalBtn) {
        equalBtn.addEventListener('click', function () {
            makeChoice(3);
        });
    }

    // Bouton passer
    var skipBtn = document.getElementById('skip-btn');
    if (skipBtn) {
        skipBtn.addEventListener('click', function () {
            makeChoice(0);
        });
    }

    // Bouton arrêter
    var stopBtn = document.getElementById('stop-btn');
    if (stopBtn) {
        stopBtn.addEventListener('click', function () {
            if (confirm('Êtes-vous sûr de vouloir arrêter le classement ?')) {
                finishRanking();
            }
        });
    }
}

// Initialisation principale
function init() {
    console.log('Initialisation du script...');
    showScreen('start-screen');
    showLoading(false);
    initForm();
    initEventListeners();
    console.log('Script initialisé');
}

// Attendre que le DOM soit chargé
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}