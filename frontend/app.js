// ===== CAHIER NUMÉRIQUE - SPA avec Auto-Détection =====

// ===== CONFIGURATION =====

const API_URL = 'http://localhost:8000';

// État global de l'application
const state = {
    view: 'chat',  // 'chat' | 'library' | 'lesson' | 'favorites' | 'mes-cours'
    selectedMatiere: null,
    selectedLesson: null,
    chatHistory: [],
    lessonsCache: {},
    isLoading: false,
    detectedNiveau: null,
    detectedMatiere: null,
    // Pagination pour la bibliothèque
    displayedLessonsCount: 50,
    // Recherche bibliothèque
    searchQuery: '',
    searchResults: null,
    // Favoris (stockés dans localStorage)
    favorites: [],
    // Animation uniquement au chargement initial
    isInitialLibraryLoad: true,
    // Source pour les recherches (vikidia, mes_cours, tous)
    selectedSource: 'vikidia',
    // Quiz
    currentQuiz: null,           // Quiz actif {quiz_id, questions, ...}
    quizAnswers: [],             // Réponses utilisateur [0, 2, 1, ...]
    currentQuestionIndex: 0,     // Index question actuelle (0-based)
    quizCompleted: false,        // Quiz terminé ou non
    quizResults: null,           // Résultats après validation
    quizHistory: []              // Historique des quiz (localStorage)
};

// ===== FAVORIS =====

function loadFavorites() {
    const saved = localStorage.getItem('favorites');
    if (saved) {
        try {
            state.favorites = JSON.parse(saved);
        } catch (e) {
            state.favorites = [];
        }
    }
}

function saveFavorites() {
    localStorage.setItem('favorites', JSON.stringify(state.favorites));
}

function isFavorite(matiere, titre) {
    return state.favorites.some(fav => fav.matiere === matiere && fav.titre === titre);
}

function toggleFavorite(lesson) {
    const index = state.favorites.findIndex(fav =>
        fav.matiere === lesson.matiere && fav.titre === lesson.titre
    );

    if (index >= 0) {
        // Remove from favorites
        state.favorites.splice(index, 1);
    } else {
        // Add to favorites
        state.favorites.push({
            titre: lesson.titre,
            matiere: lesson.matiere,
            resume: lesson.resume,
            niveau: lesson.niveau,
            url: lesson.url,
            nb_chunks: lesson.nb_chunks,
            addedAt: Date.now()
        });
    }

    saveFavorites();
}

// ===== QUIZ HISTORY =====

function loadQuizHistory() {
    const saved = localStorage.getItem('quiz_history');
    if (saved) {
        try {
            state.quizHistory = JSON.parse(saved);
        } catch (e) {
            state.quizHistory = [];
        }
    }
}

function saveQuizToHistory(quiz, results) {
    const historyEntry = {
        quiz_id: quiz.quiz_id,
        titre: quiz.titre,
        matiere: quiz.matiere,
        niveau: quiz.niveau,
        nb_questions: quiz.nb_questions,
        score: results.score,
        percentage: results.percentage,
        performance_level: results.performance_level,
        completed_at: Date.now()
    };

    state.quizHistory.push(historyEntry);

    // Limiter à 50 entrées
    if (state.quizHistory.length > 50) {
        state.quizHistory = state.quizHistory.slice(-50);
    }

    localStorage.setItem('quiz_history', JSON.stringify(state.quizHistory));
}

// ===== ROUTER SPA =====

/**
 * Navigue vers une vue avec des paramètres optionnels
 */
function navigateTo(view, params = {}) {
    state.view = view;
    Object.assign(state, params);

    // Mettre à jour l'historique navigateur
    const url = buildURL(view, params);
    history.pushState({ view, params }, '', url);

    renderView();
}

/**
 * Construit l'URL pour l'historique
 */
function buildURL(view, params) {
    if (view === 'chat') return '/';
    if (view === 'library' && params.selectedMatiere) {
        return `/#library/${params.selectedMatiere}`;
    }
    if (view === 'lesson' && params.selectedMatiere && params.selectedLesson) {
        return `/#lesson/${params.selectedMatiere}/${encodeURIComponent(params.selectedLesson)}`;
    }
    if (view === 'quiz-setup' && params.selectedMatiere && params.selectedLesson) {
        return `/#quiz/${params.selectedMatiere}/${encodeURIComponent(params.selectedLesson)}`;
    }
    return `/#${view}`;
}

/**
 * Rend la vue actuelle
 */
function renderView() {
    const mainContainer = document.getElementById('app-main');
    const inputFooter = document.getElementById('input-footer');

    // Clear containers
    mainContainer.innerHTML = '';
    inputFooter.innerHTML = '';

    // Reset dataset when changing views
    delete mainContainer.dataset.currentMatiere;

    // Update nav toggle buttons
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === state.view);
    });

    // Update header logo based on selected matiere
    updateHeaderLogo();

    // Render appropriate view
    switch (state.view) {
        case 'chat':
            renderChatView(mainContainer, inputFooter);
            break;
        case 'library':
            renderLibraryView(mainContainer);
            break;
        case 'favorites':
            renderFavoritesView(mainContainer);
            break;
        case 'mes-cours':
            renderMesCoursView(mainContainer);
            break;
        case 'lesson':
            renderLessonView(mainContainer);
            break;
        case 'quiz-setup':
            renderQuizSetupView(mainContainer);
            break;
        case 'quiz-active':
            renderQuizActiveView(mainContainer);
            break;
        case 'quiz-results':
            renderQuizResultsView(mainContainer);
            break;
    }
}

// ===== VUE CHAT (avec Auto-Détection) =====

function renderChatView(mainContainer, inputFooter) {
    // Messages container
    const messagesDiv = document.createElement('div');
    messagesDiv.className = 'messages-container';
    messagesDiv.id = 'messages-container';

    // Restore chat history or show welcome
    if (state.chatHistory.length === 0) {
        messagesDiv.innerHTML = `
            <div class="message-wrapper bot-message welcome-msg">
                <div class="message-avatar bot-avatar">
                    <img src="${getMascotImage('accueil')}"
                         alt="Marianne"
                         class="mascot-image">
                </div>
                <div class="message-bubble paper-bubble">
                    <div class="message-content">
                        <h3>Bienvenue dans ton cahier numérique ! 👋</h3>
                        <p>Je suis là pour t'aider avec tes devoirs de collège.</p>
                        <p><strong>Nouveau :</strong> Je détecte automatiquement ta matière et ton niveau ! Plus besoin de les sélectionner. 🎯</p>

                        <div class="info-box">
                            <span class="info-icon">💡</span>
                            <p><strong>Astuce :</strong> Pose ta question directement ou clique sur une matière ci-dessus pour explorer les leçons !</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Restore messages
        state.chatHistory.forEach(msg => {
            if (msg.type === 'user') {
                messagesDiv.appendChild(createUserMessage(msg.content));
            } else if (msg.type === 'bot') {
                messagesDiv.appendChild(createBotMessage(msg.content, msg.sources, msg.detection));
            }
        });
    }

    mainContainer.appendChild(messagesDiv);

    // Input footer
    inputFooter.innerHTML = `
        <div class="input-wrapper paper-bubble">
            ${state.detectedNiveau || state.detectedMatiere ? `
                <div class="detection-badge">
                    🤖 Détecté : ${state.detectedNiveau || ''} ${state.detectedMatiere ? '• ' + formatMatiere(state.detectedMatiere) : ''}
                </div>
            ` : ''}
            <div class="source-selector">
                <label for="source-select">📚 Chercher dans :</label>
                <select id="source-select" class="source-select">
                    <option value="vikidia">Cours généraux</option>
                    <option value="mes_cours">Mes Cours (PDFs personnels)</option>
                    <option value="tous">Les deux</option>
                </select>
            </div>
            <div class="input-indicator" id="input-indicator">
                <span class="indicator-dot"></span>
                <span id="indicator-text">Prêt à répondre</span>
            </div>
            <div class="input-area">
                <textarea
                    id="user-input"
                    class="message-input"
                    placeholder="Pose ta question ici... (ex: C'est quoi le théorème de Pythagore ?)"
                    rows="1"
                ></textarea>
                <button id="send-button" class="send-btn">
                    <svg class="send-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                    </svg>
                    <span class="btn-glow"></span>
                </button>
            </div>
        </div>
    `;

    // Attach event listeners
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    userInput.addEventListener('input', autoResizeTextarea);

    // Focus input
    userInput.focus();
    scrollToBottom();
}

async function handleSendMessage() {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const indicatorText = document.getElementById('indicator-text');
    const question = userInput.value.trim();

    if (!question || state.isLoading) return;

    // Add user message to history
    state.chatHistory.push({ type: 'user', content: question });

    // Clear input
    userInput.value = '';
    autoResizeTextarea();

    // Update UI
    const messagesContainer = document.getElementById('messages-container');
    messagesContainer.appendChild(createUserMessage(question));

    // Show loading
    state.isLoading = true;
    sendButton.disabled = true;
    userInput.disabled = true;
    indicatorText.textContent = 'Recherche en cours...';

    const loadingEl = createLoadingMessage();
    messagesContainer.appendChild(loadingEl);
    scrollToBottom();

    try {
        // Get selected source
        const sourceSelect = document.getElementById('source-select');
        const source = sourceSelect ? sourceSelect.value : 'vikidia';
        state.selectedSource = source;

        // Call auto-detect API
        const response = await fetch(`${API_URL}/api/chat/auto`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, source })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        // Update detected info
        state.detectedNiveau = data.niveau_detecte;
        state.detectedMatiere = data.matiere_detectee;

        // Remove loading
        loadingEl.remove();

        // Check if ambiguous
        if (data.ambigue && data.matieres_possibles && data.matieres_possibles.length > 1) {
            // Show choice buttons
            const choiceEl = createMatiereChoiceMessage(data.matieres_possibles, question);
            messagesContainer.appendChild(choiceEl);
        } else {
            // Add bot response
            const botEl = createBotMessage(data.answer, data.sources, {
                niveau: data.niveau_detecte,
                matiere: data.matiere_detectee
            });
            messagesContainer.appendChild(botEl);

            // Save to history
            state.chatHistory.push({
                type: 'bot',
                content: data.answer,
                sources: data.sources,
                detection: {
                    niveau: data.niveau_detecte,
                    matiere: data.matiere_detectee
                }
            });
        }

        scrollToBottom();

    } catch (error) {
        console.error('❌ Error:', error);
        loadingEl.remove();
        const errorEl = createBotMessage(
            "Désolé, une erreur s'est produite. 😕 Vérifie que le serveur est bien lancé et réessaie !",
            []
        );
        messagesContainer.appendChild(errorEl);
    } finally {
        state.isLoading = false;
        sendButton.disabled = false;
        userInput.disabled = false;
        indicatorText.textContent = 'Prêt à répondre';
        userInput.focus();
    }
}

// ===== VUE BIBLIOTHÈQUE (Liste des Leçons) =====

async function renderLibraryView(mainContainer) {
    if (!state.selectedMatiere) {
        // Show matiere selection with mascot cards
        const matieres = [
            'mathematiques', 'francais', 'histoire_geo', 'svt',
            'physique_chimie', 'technologie', 'anglais', 'espagnol'
        ];
        mainContainer.innerHTML = `
            <div class="library-intro">
                <div class="library-intro-header">
                    <img src="${getMascotImage('accueil')}"
                         alt="Marianne"
                         class="library-intro-mascot">
                    <div>
                        <h2>Bibliothèque de Cours</h2>
                        <p>Choisis une matière pour explorer les leçons disponibles</p>
                    </div>
                </div>
                <div class="subject-cards-grid">
                    ${matieres.map(m => `
                        <button class="subject-card" data-matiere="${m}">
                            <img src="${getMascotImage('base', m)}"
                                 alt="${formatMatiere(m)}"
                                 class="subject-card-mascot">
                            <span class="subject-card-name">${formatMatiere(m)}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
        `;

        // Attach click handlers to subject cards
        mainContainer.querySelectorAll('.subject-card').forEach(card => {
            card.addEventListener('click', () => {
                const matiere = card.dataset.matiere;
                document.body.setAttribute('data-subject', matiere);
                navigateTo('library', { selectedMatiere: matiere });
            });
        });
        return;
    }

    // Vérifier si le contenu affiché correspond déjà à la matière sélectionnée
    const currentGridMatiere = mainContainer.dataset.currentMatiere;
    if (currentGridMatiere === state.selectedMatiere) {
        return;
    }

    // Check if lessons are already in cache
    const cachedLessons = state.lessonsCache[state.selectedMatiere];

    try {
        // Fetch lessons from API (or use cache)
        let lessons;
        if (cachedLessons) {
            lessons = cachedLessons;
        } else {
            // Show temporary loading message (no skeleton)
            mainContainer.innerHTML = `
                <div class="library-container">
                    <div class="library-header">
                        <div class="library-header-row">
                            <img src="${getMascotImage('base', state.selectedMatiere)}"
                                 alt="${formatMatiere(state.selectedMatiere)}"
                                 class="library-header-mascot">
                            <div>
                                <h2>${formatMatiere(state.selectedMatiere)}</h2>
                                <p>Chargement des leçons...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            const response = await fetch(`${API_URL}/api/lecons/${state.selectedMatiere}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            lessons = data.lecons;
            state.lessonsCache[state.selectedMatiere] = lessons;
        }

        // Reset displayed count and search when changing subject
        state.displayedLessonsCount = 50;
        state.searchQuery = '';
        state.isInitialLibraryLoad = true; // Activer animations pour nouveau chargement

        // Render lessons with pagination
        renderLessonsWithPagination(mainContainer, lessons);

        // Marquer le container avec la matière actuellement affichée
        mainContainer.dataset.currentMatiere = state.selectedMatiere;

    } catch (error) {
        console.error('❌ Error loading lessons:', error);
        mainContainer.innerHTML = `
            <div class="library-error">
                <h2>❌ Erreur</h2>
                <p>Impossible de charger les leçons. Vérifie que le serveur est lancé.</p>
            </div>
        `;
    }
}

function renderLessonsWithPagination(mainContainer, allLessons) {
    // Filtrer les leçons si une recherche est active
    let filteredLessons = allLessons;
    if (state.searchQuery) {
        const query = normalizeString(state.searchQuery);
        filteredLessons = allLessons.filter(lesson => {
            const titre = normalizeString(lesson.titre);
            const resume = normalizeString(lesson.resume);
            return titre.includes(query) || resume.includes(query);
        });
    }

    const lessonsToShow = filteredLessons.slice(0, state.displayedLessonsCount);
    const hasMore = state.displayedLessonsCount < filteredLessons.length;

    // Message si aucun résultat
    const noResultsMessage = state.searchQuery && filteredLessons.length === 0 ? `
        <div class="no-results">
            <p>😕 Aucune leçon trouvée pour "<strong>${state.searchQuery}</strong>"</p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem;">Essaie avec d'autres mots-clés.</p>
        </div>
    ` : '';

    mainContainer.innerHTML = `
        <div class="library-container">
            <div class="library-header">
                <div class="library-header-row">
                    <img src="${getMascotImage('base', state.selectedMatiere)}"
                         alt="${formatMatiere(state.selectedMatiere)}"
                         class="library-header-mascot">
                    <div>
                        <h2>${formatMatiere(state.selectedMatiere)}</h2>
                        <p>${allLessons.length} leçons disponibles${state.searchQuery ? ` • ${filteredLessons.length} résultat(s)` : ` • Affichage de ${lessonsToShow.length} leçons`}</p>
                    </div>
                </div>
            </div>

            <div class="library-search">
                <div class="search-input-wrapper">
                    <span class="search-icon">🔍</span>
                    <input
                        type="text"
                        id="library-search-input"
                        class="search-input"
                        placeholder="Rechercher une leçon par titre ou mot-clé..."
                        value="${state.searchQuery}"
                    />
                    ${state.searchQuery ? `
                        <button id="clear-search-btn" class="clear-search-btn" title="Effacer la recherche">✕</button>
                    ` : ''}
                </div>
            </div>

            ${noResultsMessage}

            <div class="lessons-grid" id="lessons-grid">
                ${lessonsToShow.map((lesson, i) => createLessonCard(lesson, i, state.isInitialLibraryLoad)).join('')}
            </div>

            ${hasMore ? `
                <div class="load-more-container">
                    <button id="load-more-btn" class="btn-load-more">
                        📚 Charger 50 leçons de plus (${filteredLessons.length - state.displayedLessonsCount} restantes)
                    </button>
                </div>
            ` : ''}
        </div>
    `;

    // Attach search input listener
    const searchInput = document.getElementById('library-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const cursorPosition = e.target.selectionStart; // Sauvegarder position curseur
            state.searchQuery = e.target.value;
            state.displayedLessonsCount = 50; // Reset pagination on search
            state.isInitialLibraryLoad = false; // Désactiver animations lors de la recherche
            renderLessonsWithPagination(mainContainer, allLessons);

            // Restaurer le focus et la position du curseur après le re-render
            setTimeout(() => {
                const newSearchInput = document.getElementById('library-search-input');
                if (newSearchInput) {
                    newSearchInput.focus();
                    newSearchInput.setSelectionRange(cursorPosition, cursorPosition);
                }
            }, 0);
        });

        // Focus only if no search active (avoid refocus on typing)
        if (!state.searchQuery) {
            setTimeout(() => searchInput.focus(), 100);
        }
    }

    // Attach clear search button
    document.getElementById('clear-search-btn')?.addEventListener('click', () => {
        state.searchQuery = '';
        state.displayedLessonsCount = 50;
        renderLessonsWithPagination(mainContainer, allLessons);
    });

    // Attach click listeners to lesson cards
    attachLessonCardListeners();

    // Attach load more button
    if (hasMore) {
        document.getElementById('load-more-btn')?.addEventListener('click', () => {
            state.displayedLessonsCount += 50;
            renderLessonsWithPagination(mainContainer, allLessons);
        });
    }
}

function attachLessonCardListeners() {
    document.querySelectorAll('.lesson-card').forEach(card => {
        const titre = card.dataset.titre;
        const matiere = card.dataset.matiere || state.selectedMatiere;

        // Click sur toute la carte = ouvrir la leçon
        card.addEventListener('click', () => {
            navigateTo('lesson', { selectedMatiere: matiere, selectedLesson: titre });
        });

        // Bouton favori
        card.querySelector('.btn-favorite')?.addEventListener('click', (e) => {
            e.stopPropagation(); // Ne pas ouvrir la leçon

            // Trouver la leçon complète pour toggle
            const lesson = {
                titre: titre,
                matiere: matiere,
                resume: card.querySelector('.lesson-resume')?.textContent || '',
                niveau: card.querySelector('.lesson-niveau')?.textContent || 'college',
                nb_chunks: parseInt(card.querySelector('.lesson-chunks')?.textContent) || 0,
                url: ''
            };

            toggleFavorite(lesson);

            // Re-render la vue actuelle pour mettre à jour l'étoile
            if (state.view === 'favorites') {
                renderFavoritesView(document.getElementById('app-main'));
            } else {
                // Juste mettre à jour visuellement
                const isFav = isFavorite(matiere, titre);
                const btn = card.querySelector('.btn-favorite');
                btn.textContent = isFav ? '⭐' : '☆';
                btn.classList.toggle('active', isFav);
                btn.title = isFav ? 'Retirer des favoris' : 'Ajouter aux favoris';
                card.classList.toggle('is-favorite', isFav);
            }
        });

        // Bouton "Lire" garde le même comportement (déjà géré par le click sur la carte)
        card.querySelector('.btn-read')?.addEventListener('click', (e) => {
            e.stopPropagation(); // Éviter double navigation
            navigateTo('lesson', { selectedMatiere: matiere, selectedLesson: titre });
        });

        // Bouton "Poser une question" a un comportement différent
        card.querySelector('.btn-ask')?.addEventListener('click', (e) => {
            e.stopPropagation(); // Empêcher le click sur la carte
            navigateTo('chat');
            setTimeout(() => {
                const input = document.getElementById('user-input');
                if (input) {
                    input.value = `Explique-moi ${titre}`;
                    input.focus();
                }
            }, 100);
        });

        // Bouton "Quiz"
        card.querySelector('.btn-quiz')?.addEventListener('click', (e) => {
            e.stopPropagation(); // Empêcher le click sur la carte
            navigateTo('quiz-setup', { selectedMatiere: matiere, selectedLesson: titre });
        });
    });
}

function createLessonCard(lesson, index, animate = false) {
    // Nettoyer le résumé des crochets et le tronquer si trop long
    let cleanResume = lesson.resume.replace(/^\[.+?\]\s*/gm, '').replace(/\n\[.+?\]\s*/g, '\n');
    if (cleanResume.length > 150) {
        cleanResume = cleanResume.substring(0, 150) + '...';
    }

    // Check if lesson is favorite
    const isFav = isFavorite(lesson.matiere, lesson.titre);

    return `
        <div class="lesson-card ${isFav ? 'is-favorite' : ''}" data-titre="${lesson.titre}" data-matiere="${lesson.matiere}">
            <button class="btn-favorite ${isFav ? 'active' : ''}" title="${isFav ? 'Retirer des favoris' : 'Ajouter aux favoris'}">
                ${isFav ? '⭐' : '☆'}
            </button>
            <div class="lesson-icon">${getSubjectIcon(lesson.matiere)}</div>
            <div class="lesson-content">
                <h3 class="lesson-title">${lesson.titre}</h3>
                <p class="lesson-resume">${cleanResume}</p>
                <div class="lesson-meta">
                    <span class="lesson-niveau">${lesson.niveau}</span>
                    <span class="lesson-chunks">${lesson.nb_chunks} sections</span>
                </div>
            </div>
            <div class="lesson-actions">
                <button class="btn-quiz" title="Faire un quiz">📝</button>
                <button class="btn-read" title="Lire la leçon">📖</button>
                <button class="btn-ask" title="Poser une question">💬</button>
            </div>
        </div>
    `;
}

// ===== VUE FAVORIS =====

function renderFavoritesView(mainContainer) {
    const favorites = state.favorites;

    if (favorites.length === 0) {
        mainContainer.innerHTML = `
            <div class="favorites-empty">
                <div class="empty-state-mascot">
                    <img src="${getMascotImage('confused')}"
                         alt="Aucun favori">
                </div>
                <h2>Aucun favori pour l'instant</h2>
                <p>Clique sur l'étoile ⭐ d'une leçon pour l'ajouter à tes favoris.</p>
                <button class="btn-primary" onclick="navigateTo('library', {})">
                    📚 Explorer la bibliothèque
                </button>
            </div>
        `;
        return;
    }

    // Sort favorites by date (most recent first)
    const sortedFavorites = [...favorites].sort((a, b) => b.addedAt - a.addedAt);

    mainContainer.innerHTML = `
        <div class="library-container">
            <div class="library-header">
                <h2>⭐ Mes Favoris</h2>
                <p>${favorites.length} leçon(s) favorite(s)</p>
            </div>

            <div class="lessons-grid" id="lessons-grid">
                ${sortedFavorites.map((lesson, i) => createLessonCard(lesson, i)).join('')}
            </div>
        </div>
    `;

    // Attach click listeners
    attachLessonCardListeners();
}

// ===== VUE MES COURS (PDFs personnels) =====

async function renderMesCoursView(mainContainer) {
    mainContainer.innerHTML = `
        <div class="library-container">
            <div class="library-header">
                <h2>📄 Mes Cours</h2>
                <p>Importe tes propres cours en PDF pour les interroger avec le chatbot</p>
            </div>

            <!-- Zone d'upload -->
            <div class="upload-zone" id="upload-zone">
                <div class="upload-content">
                    <div class="empty-state-mascot">
                        <img src="${getMascotImage('reading')}"
                             alt="Importer un PDF">
                    </div>
                    <h3>Glisse un PDF ici</h3>
                    <p>ou clique pour sélectionner un fichier</p>
                    <input type="file" id="file-input" accept=".pdf" style="display: none;">
                    <button class="btn-primary" onclick="document.getElementById('file-input').click()">
                        Choisir un fichier PDF
                    </button>
                </div>
                <div class="upload-progress" id="upload-progress" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill"></div>
                    </div>
                    <p id="progress-text">Upload en cours...</p>
                </div>
            </div>

            <!-- Liste des PDFs -->
            <div id="pdf-list" class="pdf-list">
                <h3>📚 Mes documents (chargement...)</h3>
            </div>
        </div>
    `;

    // Setup drag & drop
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', async (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].name.endsWith('.pdf')) {
            await uploadPDF(files[0]);
        } else {
            alert('Veuillez déposer un fichier PDF');
        }
    });

    fileInput.addEventListener('change', async (e) => {
        if (e.target.files.length > 0) {
            await uploadPDF(e.target.files[0]);
        }
    });

    // Charger la liste des PDFs
    await loadPDFList();
}

async function uploadPDF(file) {
    const uploadProgress = document.getElementById('upload-progress');
    const uploadContent = document.querySelector('.upload-content');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');

    try {
        // Afficher la barre de progression
        uploadContent.style.display = 'none';
        uploadProgress.style.display = 'block';
        progressText.textContent = `Upload de ${file.name}...`;

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_URL}/api/upload-pdf`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const result = await response.json();

        progressFill.style.width = '100%';
        progressText.textContent = `✅ ${result.message} (${result.nb_pages} pages, ${result.nb_chunks} chunks)`;

        // Recharger la liste après 2 secondes
        setTimeout(async () => {
            uploadContent.style.display = 'flex';
            uploadProgress.style.display = 'none';
            progressFill.style.width = '0%';
            document.getElementById('file-input').value = '';
            await loadPDFList();
        }, 2000);

    } catch (error) {
        console.error('Erreur upload:', error);
        progressText.textContent = '❌ Erreur lors de l\'upload';
        setTimeout(() => {
            uploadContent.style.display = 'flex';
            uploadProgress.style.display = 'none';
        }, 2000);
    }
}

async function loadPDFList() {
    const pdfList = document.getElementById('pdf-list');

    try {
        const response = await fetch(`${API_URL}/api/mes-cours`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        if (data.nb_pdfs === 0) {
            pdfList.innerHTML = `
                <div style="text-align: center; padding: 2rem; opacity: 0.6;">
                    <p>📂 Aucun document importé pour l'instant</p>
                </div>
            `;
            return;
        }

        pdfList.innerHTML = `
            <h3>📚 Mes documents (${data.nb_pdfs})</h3>
            <div class="pdf-grid">
                ${data.pdfs.map(pdf => `
                    <div class="pdf-card">
                        <div class="pdf-icon">📄</div>
                        <div class="pdf-info">
                            <h4>${pdf.filename}</h4>
                            <p>${(pdf.size / 1024).toFixed(1)} KB • ${new Date(pdf.uploaded_at).toLocaleDateString('fr-FR')}</p>
                        </div>
                        <button class="btn-delete" onclick="deletePDF('${pdf.filename}')">
                            🗑️ Supprimer
                        </button>
                    </div>
                `).join('')}
            </div>
        `;

    } catch (error) {
        console.error('Erreur chargement PDFs:', error);
        pdfList.innerHTML = '<p>❌ Erreur lors du chargement</p>';
    }
}

async function deletePDF(filename) {
    if (!confirm(`Supprimer "${filename}" ?`)) return;

    try {
        const response = await fetch(`${API_URL}/api/mes-cours/${encodeURIComponent(filename)}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        await loadPDFList();

    } catch (error) {
        console.error('Erreur suppression:', error);
        alert('Erreur lors de la suppression');
    }
}

// Rendre deletePDF accessible globalement
window.deletePDF = deletePDF;

// ===== VUE DÉTAIL LEÇON =====

async function renderLessonView(mainContainer) {
    if (!state.selectedMatiere || !state.selectedLesson) {
        navigateTo('library', { selectedMatiere: state.selectedMatiere });
        return;
    }

    // Show loading
    mainContainer.innerHTML = `
        <div class="lesson-detail-loading">
            <div class="breadcrumbs">
                <a href="#" data-nav="library">Bibliothèque</a> ›
                <a href="#" data-nav="library-matiere">${formatMatiere(state.selectedMatiere)}</a> ›
                <span>${state.selectedLesson}</span>
            </div>
            <h2>Chargement...</h2>
            ${createSkeletonCard()}
        </div>
    `;

    try {
        const titre = encodeURIComponent(state.selectedLesson);
        const url = `${API_URL}/api/lecons/${state.selectedMatiere}/detail?titre=${titre}`;

        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const lesson = await response.json();

        mainContainer.innerHTML = `
            <div class="lesson-detail">
                <div class="breadcrumbs">
                    <a href="#" data-nav="library">📚 Bibliothèque</a> ›
                    <a href="#" data-nav="library-matiere">${getSubjectIcon(state.selectedMatiere)} ${formatMatiere(state.selectedMatiere)}</a> ›
                    <span>${lesson.titre}</span>
                </div>

                <div class="lesson-header">
                    <div class="lesson-header-row">
                        <img src="${getMascotImage('base', lesson.matiere)}"
                             alt="${formatMatiere(lesson.matiere)}"
                             class="lesson-header-mascot">
                        <div>
                            <h1>${lesson.titre}</h1>
                            <div class="lesson-meta-large">
                                <span class="meta-badge">${formatMatiere(lesson.matiere)}</span>
                                <span class="meta-badge">${lesson.niveau}</span>
                                <span class="meta-badge">${lesson.nb_chunks} sections</span>
                                <span class="meta-badge">${lesson.source}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="lesson-body">
                    <div class="lesson-resume-section">
                        <h3>📝 Résumé</h3>
                        <div class="lesson-text">${formatMarkdown(lesson.resume)}</div>
                        <button id="btn-show-full" class="btn-expand">📖 Lire le contenu complet</button>
                    </div>

                    <div id="lesson-full-content" class="lesson-full-content hidden">
                        <h3>📚 Contenu Complet</h3>
                        <div class="lesson-text">${formatLessonContent(lesson.contenu_complet)}</div>
                    </div>
                </div>

                <div class="lesson-actions-bottom">
                    <button id="btn-quiz" class="btn-primary" data-matiere="${lesson.matiere}" data-titre="${lesson.titre}">
                        📝 Faire un quiz sur cette leçon
                    </button>
                    <button id="btn-ask-about" class="btn-primary">
                        💬 Poser une question sur cette leçon
                    </button>
                    ${lesson.url ? `<a href="${lesson.url}" target="_blank" class="btn-secondary">🔗 Voir sur Vikidia</a>` : ''}
                </div>
            </div>
        `;

        // Attach event listeners
        document.querySelectorAll('.breadcrumbs a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                if (link.dataset.nav === 'library') {
                    navigateTo('library', { selectedMatiere: null });
                } else if (link.dataset.nav === 'library-matiere') {
                    navigateTo('library', { selectedMatiere: state.selectedMatiere });
                }
            });
        });

        document.getElementById('btn-show-full')?.addEventListener('click', () => {
            document.getElementById('lesson-full-content').classList.remove('hidden');
            document.getElementById('btn-show-full').style.display = 'none';
        });

        document.getElementById('btn-ask-about')?.addEventListener('click', () => {
            navigateTo('chat');
            setTimeout(() => {
                const input = document.getElementById('user-input');
                if (input) {
                    input.value = `Explique-moi ${lesson.titre}`;
                    input.focus();
                }
            }, 100);
        });

        document.getElementById('btn-quiz')?.addEventListener('click', (e) => {
            const matiere = e.target.dataset.matiere;
            const titre = e.target.dataset.titre;
            navigateTo('quiz-setup', { selectedMatiere: matiere, selectedLesson: titre });
        });

    } catch (error) {
        console.error('❌ Error loading lesson:', error);
        mainContainer.innerHTML = `
            <div class="lesson-error">
                <h2>❌ Erreur</h2>
                <p>Impossible de charger cette leçon.</p>
                <button onclick="navigateTo('library', {selectedMatiere: '${state.selectedMatiere}'})">
                    ← Retour à la bibliothèque
                </button>
            </div>
        `;
    }
}

// ===== HELPERS - MESSAGE CREATION =====

function createUserMessage(text) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper user-message';
    wrapper.innerHTML = `
        <div class="message-bubble paper-bubble user-bubble">
            <div class="message-content">${escapeHtml(text)}</div>
        </div>
        <div class="message-avatar user-avatar">
            <span>✏️</span>
        </div>
    `;
    return wrapper;
}

function createBotMessage(text, sources = [], detection = null) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot-message';

    // Créer la section sources avec les liens Vikidia et Bibliothèque
    let sourcesHTML = '';
    if (sources && sources.length > 0) {
        sourcesHTML = `
            <div class="message-sources">
                <div style="font-weight: 700; margin-bottom: 0.5rem; font-size: 0.9rem; opacity: 0.9;">
                    📚 Sources (${sources.length})
                </div>
                ${sources.map((s, i) => `
                    <div class="source-item">
                        <span style="font-size: 1.2rem;">${getSubjectIcon(s.matiere)}</span>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; margin-bottom: 0.25rem;">${s.titre}</div>
                            <div style="opacity: 0.8; font-size: 0.85rem;">${formatMatiere(s.matiere)}</div>
                        </div>
                        <div class="source-links">
                            ${s.url ? `<a href="${s.url}" target="_blank" class="source-link-btn vikidia-btn" title="Voir sur Vikidia">🔗 Vikidia</a>` : ''}
                            <button class="source-link-btn library-btn" data-matiere="${s.matiere}" data-titre="${s.titre}" title="Voir dans la bibliothèque">📚 Bibliothèque</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Construire le badge de détection seulement si les valeurs sont valides
    let detectionBadge = '';
    if (detection && (detection.niveau || detection.matiere)) {
        const niveauText = detection.niveau || '';
        const matiereText = detection.matiere ? formatMatiere(detection.matiere) : '';
        const separator = niveauText && matiereText ? ' • ' : '';
        detectionBadge = `<div class="detection-info">🤖 Détecté : ${niveauText}${separator}${matiereText}</div>`;
    }

    // Utiliser la mascotte de la matière détectée si disponible
    const mascotImage = getMascotImage('base', detection?.matiere);

    wrapper.innerHTML = `
        <div class="message-avatar bot-avatar">
            <img src="${mascotImage}"
                 alt="Marianne"
                 class="mascot-image">
        </div>
        <div class="message-bubble paper-bubble bot-bubble">
            ${detectionBadge}
            <div class="message-content">${formatMarkdown(text)}</div>
            ${sourcesHTML}
        </div>
    `;

    // Attacher les event listeners pour les boutons bibliothèque
    setTimeout(() => {
        wrapper.querySelectorAll('.library-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const matiere = btn.dataset.matiere;
                const titre = btn.dataset.titre;

                navigateTo('lesson', {
                    selectedMatiere: matiere,
                    selectedLesson: titre
                });
            });
        });
    }, 0);

    return wrapper;
}

function createLoadingMessage() {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot-message loading-wrapper';
    wrapper.innerHTML = `
        <div class="message-avatar bot-avatar">
            <img src="${getMascotImage('loading')}"
                 alt="Recherche en cours..."
                 class="mascot-image mascot-thinking">
        </div>
        <div class="message-bubble paper-bubble">
            <div class="loading-skeleton">
                <div class="skeleton-line"></div>
                <div class="skeleton-line short"></div>
                <div class="skeleton-line"></div>
            </div>
            <div class="loading-text">
                <span class="thinking-dots">
                    <span>.</span><span>.</span><span>.</span>
                </span>
                <span>Je cherche dans mes cours</span>
            </div>
        </div>
    `;
    return wrapper;
}

function createMatiereChoiceMessage(matieres, question) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot-message';
    wrapper.innerHTML = `
        <div class="message-avatar bot-avatar">
            <img src="${getMascotImage('thinking')}"
                 alt="Question..."
                 class="mascot-image">
        </div>
        <div class="message-bubble paper-bubble bot-bubble">
            <div class="message-content">
                <p><strong>Hmm, ta question pourrait concerner plusieurs matières :</strong></p>
                <div class="matiere-choice-buttons">
                    ${matieres.map(m => `
                        <button class="matiere-choice-btn" data-matiere="${m}" data-question="${escapeHtml(question)}">
                            ${getSubjectIcon(m)} ${formatMatiere(m)}
                        </button>
                    `).join('')}
                </div>
                <p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
                    <em>Clique sur la matière qui correspond le mieux à ta question.</em>
                </p>
            </div>
        </div>
    `;

    // Attach click handlers
    wrapper.querySelectorAll('.matiere-choice-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const matiere = btn.dataset.matiere;
            const question = btn.dataset.question;

            // Disable buttons
            wrapper.querySelectorAll('.matiere-choice-btn').forEach(b => b.disabled = true);

            // Re-send question with selected matiere
            await sendQuestionWithMatiere(question, matiere);
        });
    });

    return wrapper;
}

async function sendQuestionWithMatiere(question, matiere) {
    const messagesContainer = document.getElementById('messages-container');
    const loadingEl = createLoadingMessage();
    messagesContainer.appendChild(loadingEl);
    scrollToBottom();

    try {
        const response = await fetch(`${API_URL}/api/chat/auto`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, matiere })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        loadingEl.remove();

        const botEl = createBotMessage(data.answer, data.sources, {
            niveau: data.niveau_detecte,
            matiere: data.matiere_detectee
        });
        messagesContainer.appendChild(botEl);

        state.chatHistory.push({
            type: 'bot',
            content: data.answer,
            sources: data.sources,
            detection: {
                niveau: data.niveau_detecte,
                matiere: data.matiere_detectee
            }
        });

        scrollToBottom();
    } catch (error) {
        console.error('❌ Error:', error);
        loadingEl.remove();
    }
}

function createSkeletonCard() {
    return `
        <div class="skeleton-card">
            <div class="skeleton-line"></div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line"></div>
        </div>
    `;
}

// ===== HELPERS - FORMATTING =====

function formatMarkdown(text) {
    let formatted = text;

    // Supprimer les contenus entre crochets au début des lignes/paragraphes
    formatted = formatted.replace(/^\[.+?\]\s*/gm, '');
    formatted = formatted.replace(/\n\[.+?\]\s*/g, '\n');

    // Détecter et formater les titres de sections (lignes courtes sans ponctuation finale)
    // Un titre : commence par une majuscule, moins de 80 caractères, pas de point final
    formatted = formatted.replace(/^([A-ZÀ-Ÿ][^\n]{5,79}[^\.\!\?\:\n])$/gm, '<strong>$1</strong>');

    // Convertir les titres Markdown en gras souligné (#### -> <strong><u>)
    formatted = formatted.replace(/^####\s+(.+)$/gm, '<strong><u>$1</u></strong>');
    formatted = formatted.replace(/^###\s+(.+)$/gm, '<strong><u>$1</u></strong>');
    formatted = formatted.replace(/^##\s+(.+)$/gm, '<strong><u>$1</u></strong>');
    formatted = formatted.replace(/^#\s+(.+)$/gm, '<strong><u>$1</u></strong>');

    // Gras et italique
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');

    // Code inline
    formatted = formatted.replace(/`(.+?)`/g, '<code style="background: rgba(255,255,255,0.2); padding: 0.2rem 0.4rem; border-radius: 4px; font-family: monospace;">$1</code>');

    // Retours à la ligne
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

function formatLessonContent(text) {
    // Split into paragraphs and format
    return text.split('\n\n')
        .map(p => `<p>${formatMarkdown(p)}</p>`)
        .join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function normalizeString(str) {
    // Normalise une chaîne pour la recherche : lowercase + suppression accents
    return str.toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');
}

function formatMatiere(matiere) {
    const names = {
        'mathematiques': 'Mathématiques',
        'francais': 'Français',
        'histoire_geo': 'Histoire-Géo',
        'svt': 'SVT',
        'physique_chimie': 'Physique-Chimie',
        'technologie': 'Technologie',
        'anglais': 'Anglais',
        'espagnol': 'Espagnol'
    };
    return names[matiere] || matiere;
}

function getSubjectIcon(matiere) {
    const icons = {
        'mathematiques': '📐',
        'francais': '✍️',
        'histoire_geo': '🗺️',
        'svt': '🔬',
        'physique_chimie': '⚗️',
        'technologie': '⚙️',
        'anglais': '🔤',
        'espagnol': '🗣️'
    };
    return icons[matiere] || '📖';
}

function getMascotImage(context = 'base', matiere = null) {
    // Contextes spéciaux qui ont priorité sur la matière
    const specialContexts = {
        'loading': 'mascot-loading.png',
        'thinking': 'mascot-thinking.png',
        'confused': 'mascot-confused.png',
        'reading': 'mascot-reading.png',
        'celebrating': 'mascot-celebrating.png',
        'logo': 'mascot-logo.png'
    };

    // Si contexte spécial, utiliser l'image spéciale
    if (context !== 'base' && specialContexts[context]) {
        return `assets/mascot/${specialContexts[context]}`;
    }

    // Mapping matière → fichier PNG
    const matiereImages = {
        'mathematiques': 'Math.png',
        'francais': 'francais.png',
        'histoire_geo': 'histoire_geo.png',
        'svt': 'svt.png',
        'physique_chimie': 'physique_chimie.png',
        'technologie': 'techno.png',
        'anglais': 'anglais.png',
        'espagnol': 'espagnol.png'
    };

    // Si matière fournie, utiliser son image
    if (matiere && matiereImages[matiere]) {
        return `assets/mascot/${matiereImages[matiere]}`;
    }

    // Par défaut : accueil.png pour la page d'accueil, ou mascot-base.png
    return context === 'accueil' ? 'assets/mascot/accueil.png' : 'assets/mascot/mascot-base.png';
}

function updateHeaderLogo() {
    // Le logo du header reste toujours mascot-logo.png
    // Les images par matière sont des illustrations complètes, pas adaptées au petit logo
}

function autoResizeTextarea() {
    const textarea = document.getElementById('user-input');
    if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
}

function scrollToBottom() {
    const container = document.getElementById('messages-container');
    if (container) {
        setTimeout(() => {
            container.scrollTo({
                top: container.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }
}

// ===== EVENT LISTENERS GLOBAUX =====

function attachGlobalListeners() {
    // Toggle buttons (Chat / Bibliothèque)
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            navigateTo(view, view === 'library' ? { selectedMatiere: state.selectedMatiere } : {});
        });
    });

    // Subject buttons
    document.querySelectorAll('.subject-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const matiere = btn.dataset.matiere;

            // Update active state
            document.querySelectorAll('.subject-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update subject (for accent color) - not theme (dark/light)
            document.body.setAttribute('data-subject', matiere);

            // Navigate to library with selected matiere
            navigateTo('library', { selectedMatiere: matiere });
        });
    });

    // Browser back/forward
    window.addEventListener('popstate', (e) => {
        if (e.state) {
            state.view = e.state.view;
            Object.assign(state, e.state.params);
            renderView();
        }
    });
}

// ===== THEME MANAGEMENT =====

function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

function initTheme() {
    // Charger le thème sauvegardé ou détecter la préférence système
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    document.body.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function setupThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle');

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
}

// ===== VUE QUIZ =====

async function renderQuizSetupView(mainContainer) {
    const { selectedMatiere, selectedLesson } = state;

    if (!selectedMatiere || !selectedLesson) {
        mainContainer.innerHTML = '<p class="error">❌ Leçon non trouvée</p>';
        return;
    }

    const mascotSrc = getMascotImage('base', selectedMatiere);
    const matieresIcons = {
        'mathematiques': '📐',
        'francais': '📝',
        'histoire_geo': '🗺️',
        'svt': '🔬',
        'physique_chimie': '⚗️',
        'technologie': '⚙️',
        'anglais': '🇬🇧',
        'espagnol': '🇪🇸'
    };

    const formatMatiere = (mat) => {
        const names = {
            'mathematiques': 'Mathématiques',
            'francais': 'Français',
            'histoire_geo': 'Histoire-Géographie',
            'svt': 'SVT',
            'physique_chimie': 'Physique-Chimie',
            'technologie': 'Technologie',
            'anglais': 'Anglais',
            'espagnol': 'Espagnol'
        };
        return names[mat] || mat;
    };

    mainContainer.innerHTML = `
        <div class="quiz-setup-container">
            <img src="${mascotSrc}" alt="Mascotte" class="mascot-large">

            <h2>📝 Créer un Quiz</h2>
            <div class="lesson-badge">${selectedLesson}</div>
            <div class="matiere-badge" data-matiere="${selectedMatiere}">
                ${matieresIcons[selectedMatiere] || '📚'} ${formatMatiere(selectedMatiere)}
            </div>

            <div class="quiz-config">
                <label for="nb-questions">Nombre de questions :</label>
                <select id="nb-questions">
                    <option value="3">3 questions</option>
                    <option value="5" selected>5 questions</option>
                    <option value="7">7 questions</option>
                    <option value="10">10 questions</option>
                </select>
            </div>

            <button class="btn-primary" id="start-quiz-btn">
                🚀 Générer le quiz
            </button>

            <button class="btn-secondary" id="cancel-quiz-btn">
                ← Retour
            </button>

            <div id="loading-message" class="loading-message" style="display: none;">
                <img src="${getMascotImage('loading')}" class="mascot-small">
                <p>Génération du quiz en cours...</p>
                <p class="loading-subtitle">(Cela peut prendre 10-15 secondes)</p>
            </div>
        </div>
    `;

    // Event listeners
    document.getElementById('start-quiz-btn').addEventListener('click', async () => {
        const nbQuestions = parseInt(document.getElementById('nb-questions').value);
        await startQuizGeneration(selectedMatiere, selectedLesson, nbQuestions);
    });

    document.getElementById('cancel-quiz-btn').addEventListener('click', () => {
        navigateTo('lesson', { selectedMatiere, selectedLesson });
    });
}

async function startQuizGeneration(matiere, titre, nbQuestions) {
    const loadingMessage = document.getElementById('loading-message');
    const startBtn = document.getElementById('start-quiz-btn');

    startBtn.disabled = true;
    loadingMessage.style.display = 'block';

    try {
        const response = await fetch(`${API_URL}/api/quiz/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                matiere,
                titre,
                nb_questions: nbQuestions,
                niveau: state.detectedNiveau || 'college'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        const quiz = await response.json();

        // Initialiser l'état du quiz
        state.currentQuiz = quiz;
        state.quizAnswers = Array(quiz.nb_questions).fill(null);
        state.currentQuestionIndex = 0;
        state.quizCompleted = false;

        // Naviguer vers le quiz actif
        navigateTo('quiz-active');

    } catch (error) {
        console.error('Erreur génération quiz:', error);
        alert(`❌ Erreur lors de la génération du quiz: ${error.message}`);
        startBtn.disabled = false;
        loadingMessage.style.display = 'none';
    }
}

function renderQuizActiveView(mainContainer) {
    if (!state.currentQuiz) {
        mainContainer.innerHTML = '<p class="error">❌ Aucun quiz actif</p>';
        return;
    }

    const quiz = state.currentQuiz;
    const currentIndex = state.currentQuestionIndex;
    const question = quiz.questions[currentIndex];
    const totalQuestions = quiz.nb_questions;
    const userAnswer = state.quizAnswers[currentIndex];

    const mascotSrc = getMascotImage('thinking', quiz.matiere);

    mainContainer.innerHTML = `
        <div class="quiz-active-container">
            <div class="quiz-header">
                <img src="${mascotSrc}" alt="Mascotte" class="mascot-medium">
                <h2>Quiz : ${quiz.titre}</h2>
                <div class="quiz-progress">
                    Question ${currentIndex + 1} / ${totalQuestions}
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${((currentIndex + 1) / totalQuestions) * 100}%"></div>
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Question ${currentIndex + 1}</div>
                <div class="question-text">${question.question}</div>

                <div class="options-grid">
                    ${question.options.map((option, i) => `
                        <button
                            class="option-btn ${userAnswer === i ? 'selected' : ''}"
                            data-index="${i}"
                        >
                            <span class="option-letter">${String.fromCharCode(65 + i)}</span>
                            <span class="option-text">${option}</span>
                        </button>
                    `).join('')}
                </div>
            </div>

            <div class="quiz-navigation">
                <button
                    class="btn-secondary"
                    id="prev-btn"
                    ${currentIndex === 0 ? 'disabled' : ''}
                >
                    ← Précédent
                </button>

                <button
                    class="btn-secondary"
                    id="quit-btn"
                >
                    ❌ Abandonner
                </button>

                ${currentIndex < totalQuestions - 1 ? `
                    <button
                        class="btn-primary"
                        id="next-btn"
                    >
                        Suivant →
                    </button>
                ` : `
                    <button
                        class="btn-primary"
                        id="submit-btn"
                    >
                        ✅ Terminer le quiz
                    </button>
                `}
            </div>
        </div>
    `;

    // Event listeners pour les options
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.currentTarget.dataset.index);
            state.quizAnswers[currentIndex] = index;

            // Update UI
            document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
            e.currentTarget.classList.add('selected');
        });
    });

    // Navigation
    document.getElementById('prev-btn')?.addEventListener('click', () => {
        if (currentIndex > 0) {
            state.currentQuestionIndex--;
            renderQuizActiveView(mainContainer);
        }
    });

    document.getElementById('next-btn')?.addEventListener('click', () => {
        if (currentIndex < totalQuestions - 1) {
            state.currentQuestionIndex++;
            renderQuizActiveView(mainContainer);
        }
    });

    document.getElementById('submit-btn')?.addEventListener('click', async () => {
        // Vérifier que toutes les questions sont répondues
        const unanswered = state.quizAnswers.filter(a => a === null).length;
        if (unanswered > 0) {
            alert(`⚠️ Il reste ${unanswered} question(s) sans réponse !`);
            return;
        }

        await submitQuiz(mainContainer);
    });

    document.getElementById('quit-btn')?.addEventListener('click', () => {
        if (confirm('Voulez-vous vraiment abandonner le quiz ?')) {
            navigateTo('lesson', {
                selectedMatiere: quiz.matiere,
                selectedLesson: quiz.titre
            });
        }
    });
}

async function submitQuiz(mainContainer) {
    const quiz = state.currentQuiz;

    try {
        const response = await fetch(`${API_URL}/api/quiz/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                quiz_id: quiz.quiz_id,
                questions: quiz.questions,
                answers: state.quizAnswers
            })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const results = await response.json();
        state.quizResults = results;
        state.quizCompleted = true;

        // Sauvegarder dans l'historique
        saveQuizToHistory(quiz, results);

        // Naviguer vers les résultats
        navigateTo('quiz-results');

    } catch (error) {
        console.error('Erreur validation quiz:', error);
        alert('❌ Erreur lors de la validation. Réessayez.');
    }
}

function renderQuizResultsView(mainContainer) {
    if (!state.quizResults || !state.currentQuiz) {
        mainContainer.innerHTML = '<p class="error">❌ Résultats non disponibles</p>';
        return;
    }

    const results = state.quizResults;
    const quiz = state.currentQuiz;
    const percentage = results.percentage;

    // Choisir mascotte selon performance
    let mascotContext = 'base';
    if (percentage >= 80) mascotContext = 'celebrating';
    else if (percentage < 50) mascotContext = 'confused';

    const mascotSrc = getMascotImage(mascotContext);

    // Message de feedback
    const feedbackMessage = getPerformanceMessage(percentage);

    mainContainer.innerHTML = `
        <div class="quiz-results-container">
            <div class="results-header">
                <img src="${mascotSrc}" alt="Mascotte" class="mascot-large">
                <h2>🎯 Résultats du Quiz</h2>
                <div class="score-display">
                    <div class="score-big">${results.score} / ${results.total}</div>
                    <div class="score-percentage">${percentage.toFixed(0)}%</div>
                    <div class="performance-badge ${results.performance_level.toLowerCase()}">
                        ${results.performance_level}
                    </div>
                </div>
                <p class="feedback-message">${feedbackMessage}</p>
            </div>

            <div class="results-review">
                <h3>📋 Détails des Réponses</h3>
                ${results.results.map((result, i) => `
                    <div class="result-card ${result.is_correct ? 'correct' : 'incorrect'}">
                        <div class="result-header">
                            <span class="result-icon">${result.is_correct ? '✅' : '❌'}</span>
                            <span class="result-title">Question ${i + 1}</span>
                        </div>
                        <p class="result-question">${quiz.questions[i].question}</p>
                        <p class="result-answer">
                            <strong>Ta réponse :</strong>
                            ${String.fromCharCode(65 + result.user_answer)} - ${quiz.questions[i].options[result.user_answer]}
                        </p>
                        ${!result.is_correct ? `
                            <p class="result-correct-answer">
                                <strong>Bonne réponse :</strong>
                                ${String.fromCharCode(65 + result.correct_answer)} - ${quiz.questions[i].options[result.correct_answer]}
                            </p>
                        ` : ''}
                        <p class="result-explanation">
                            <strong>Explication :</strong> ${result.explanation}
                        </p>
                    </div>
                `).join('')}
            </div>

            <div class="results-actions">
                <button class="btn-primary" id="retry-quiz-btn">
                    🔄 Refaire le quiz
                </button>
                <button class="btn-secondary" id="back-to-lesson-btn">
                    ← Retour à la leçon
                </button>
            </div>
        </div>
    `;

    // Event listeners
    document.getElementById('retry-quiz-btn').addEventListener('click', () => {
        navigateTo('quiz-setup', {
            selectedMatiere: quiz.matiere,
            selectedLesson: quiz.titre
        });
    });

    document.getElementById('back-to-lesson-btn').addEventListener('click', () => {
        navigateTo('lesson', {
            selectedMatiere: quiz.matiere,
            selectedLesson: quiz.titre
        });
    });
}

// Helpers
function getPerformanceMessage(percentage) {
    if (percentage === 100) {
        return "🎉 Parfait ! Tu maîtrises parfaitement cette leçon !";
    } else if (percentage >= 80) {
        return "👏 Excellent travail ! Continue comme ça !";
    } else if (percentage >= 60) {
        return "👍 Bien joué ! Quelques petites erreurs à corriger.";
    } else if (percentage >= 40) {
        return "📚 Pas mal, mais il faudrait revoir certains points.";
    } else {
        return "💪 N'abandonne pas ! Relis la leçon et réessaie.";
    }
}

// ===== INITIALIZATION =====

function init() {
    console.log('📖 Cahier Numérique SPA - Initializing...');

    initTheme();
    loadFavorites();
    loadQuizHistory();  // Charger l'historique des quiz
    attachGlobalListeners();
    setupThemeToggle();

    // Parse initial URL
    const hash = window.location.hash;
    if (hash.startsWith('#library/')) {
        const matiere = hash.split('/')[1];
        navigateTo('library', { selectedMatiere: matiere });
    } else if (hash.startsWith('#lesson/')) {
        const parts = hash.split('/');
        navigateTo('lesson', {
            selectedMatiere: parts[1],
            selectedLesson: decodeURIComponent(parts[2])
        });
    } else if (hash === '#favorites') {
        navigateTo('favorites');
    } else {
        renderView();  // Default: chat view
    }

    console.log('✅ Ready!');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

console.log('📚 Cahier Numérique SPA - Frontend loaded');
