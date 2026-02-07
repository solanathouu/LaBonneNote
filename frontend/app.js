// ===== CAHIER NUMÉRIQUE - SPA avec Auto-Détection =====

// ===== CONFIGURATION =====

const API_URL = 'http://localhost:8000';

// État global de l'application
const state = {
    view: 'chat',  // 'chat' | 'library' | 'lesson'
    selectedMatiere: null,
    selectedLesson: null,
    chatHistory: [],
    lessonsCache: {},
    isLoading: false,
    detectedNiveau: null,
    detectedMatiere: null
};

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

    // Render appropriate view
    switch (state.view) {
        case 'chat':
            renderChatView(mainContainer, inputFooter);
            break;
        case 'library':
            renderLibraryView(mainContainer);
            break;
        case 'lesson':
            renderLessonView(mainContainer);
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
                    <span>🤖</span>
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
        // Call auto-detect API
        const response = await fetch(`${API_URL}/api/chat/auto`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
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
        // Show matiere selection screen
        mainContainer.innerHTML = `
            <div class="library-intro">
                <h2>📚 Bibliothèque de Cours</h2>
                <p>Sélectionne une matière ci-dessus pour voir toutes les leçons disponibles.</p>
            </div>
        `;
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
                        <h2>${getSubjectIcon(state.selectedMatiere)} ${formatMatiere(state.selectedMatiere)}</h2>
                        <p>⏳ Chargement des leçons...</p>
                    </div>
                </div>
            `;

            const response = await fetch(`${API_URL}/api/lecons/${state.selectedMatiere}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            lessons = data.lecons;
            state.lessonsCache[state.selectedMatiere] = lessons;
        }

        // Render lessons
        mainContainer.innerHTML = `
            <div class="library-container">
                <div class="library-header">
                    <h2>${getSubjectIcon(state.selectedMatiere)} ${formatMatiere(state.selectedMatiere)}</h2>
                    <p>${lessons.length} leçons disponibles</p>
                </div>

                <div class="lessons-grid" id="lessons-grid">
                    ${lessons.map((lesson, i) => createLessonCard(lesson, i)).join('')}
                </div>
            </div>
        `;

        // Marquer le container avec la matière actuellement affichée
        mainContainer.dataset.currentMatiere = state.selectedMatiere;

        // Attach click listeners
        document.querySelectorAll('.lesson-card').forEach(card => {
            // Click sur toute la carte = ouvrir la leçon
            card.addEventListener('click', () => {
                const titre = card.dataset.titre;
                navigateTo('lesson', { selectedMatiere: state.selectedMatiere, selectedLesson: titre });
            });

            // Bouton "Lire" garde le même comportement (déjà géré par le click sur la carte)
            card.querySelector('.btn-read')?.addEventListener('click', (e) => {
                e.stopPropagation(); // Éviter double navigation
                const titre = card.dataset.titre;
                navigateTo('lesson', { selectedMatiere: state.selectedMatiere, selectedLesson: titre });
            });

            // Bouton "Poser une question" a un comportement différent
            card.querySelector('.btn-ask')?.addEventListener('click', (e) => {
                e.stopPropagation(); // Empêcher le click sur la carte
                const titre = card.dataset.titre;
                navigateTo('chat');
                setTimeout(() => {
                    const input = document.getElementById('user-input');
                    if (input) {
                        input.value = `Explique-moi ${titre}`;
                        input.focus();
                    }
                }, 100);
            });
        });

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

function createLessonCard(lesson, index) {
    // Nettoyer le résumé des crochets et le tronquer si trop long
    let cleanResume = lesson.resume.replace(/^\[.+?\]\s*/gm, '').replace(/\n\[.+?\]\s*/g, '\n');
    if (cleanResume.length > 150) {
        cleanResume = cleanResume.substring(0, 150) + '...';
    }

    return `
        <div class="lesson-card" data-titre="${lesson.titre}" style="animation-delay: ${index * 50}ms">
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
                <button class="btn-read">📖 Lire</button>
                <button class="btn-ask">💬 Poser une question</button>
            </div>
        </div>
    `;
}

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
                    <h1>${getSubjectIcon(lesson.matiere)} ${lesson.titre}</h1>
                    <div class="lesson-meta-large">
                        <span class="meta-badge">${lesson.niveau}</span>
                        <span class="meta-badge">${lesson.nb_chunks} sections</span>
                        <span class="meta-badge">${lesson.source}</span>
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
                    <div class="source-item" style="animation-delay: ${i * 80}ms">
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

    wrapper.innerHTML = `
        <div class="message-avatar bot-avatar">
            <span>📚</span>
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
            <span>📚</span>
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
            <span>🤔</span>
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

// ===== INITIALIZATION =====

function init() {
    console.log('📖 Cahier Numérique SPA - Initializing...');

    initTheme();
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
