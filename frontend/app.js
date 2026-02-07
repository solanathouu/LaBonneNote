// ===== CAHIER NUMÉRIQUE - Frontend Logic =====

const API_URL = 'http://localhost:8000/api/chat';

// App state
const state = {
    niveau: 'college',
    matiere: '',
    isLoading: false,
    messageHistory: []
};

// DOM elements
const elements = {
    niveauSelect: document.getElementById('niveau-select'),
    matiereSelect: document.getElementById('matiere-select'),
    messagesContainer: document.getElementById('messages-container'),
    userInput: document.getElementById('user-input'),
    sendButton: document.getElementById('send-button'),
    indicator: document.getElementById('input-indicator'),
    indicatorText: document.getElementById('indicator-text')
};

// Templates
const templates = {
    userMessage: document.getElementById('user-message-template'),
    botMessage: document.getElementById('bot-message-template'),
    loading: document.getElementById('loading-template')
};

// ===== INITIALIZATION =====

function init() {
    console.log('📖 Cahier Numérique - Initializing...');

    // Event listeners
    elements.niveauSelect.addEventListener('change', handleNiveauChange);
    elements.matiereSelect.addEventListener('change', handleMatiereChange);
    elements.sendButton.addEventListener('click', handleSendMessage);
    elements.userInput.addEventListener('keydown', handleInputKeydown);
    elements.userInput.addEventListener('input', autoResizeTextarea);

    // Set initial theme
    updateTheme();

    // Focus input
    elements.userInput.focus();

    console.log('✅ Ready!');
}

// ===== EVENT HANDLERS =====

function handleNiveauChange(e) {
    state.niveau = e.target.value;
    updateIndicator();
}

function handleMatiereChange(e) {
    state.matiere = e.target.value;
    updateTheme();
    updateIndicator();
}

function handleInputKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
}

async function handleSendMessage() {
    const question = elements.userInput.value.trim();

    if (!question || state.isLoading) return;

    // Add user message
    addUserMessage(question);

    // Clear input
    elements.userInput.value = '';
    autoResizeTextarea();

    // Set loading state
    setLoading(true);
    const loadingElement = addLoadingMessage();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question,
                niveau: state.niveau,
                matiere: state.matiere || undefined
            })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        // Remove loading
        loadingElement.remove();

        // Add bot response
        addBotMessage(data.answer, data.sources || []);

        // Save to history
        state.messageHistory.push({
            question,
            answer: data.answer,
            sources: data.sources,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        console.error('❌ Error:', error);
        loadingElement.remove();
        addBotMessage(
            "Désolé, une erreur s'est produite. 😕 Vérifie que le serveur est bien lancé et réessaie !",
            []
        );
    } finally {
        setLoading(false);
        elements.userInput.focus();
    }
}

// ===== UI UPDATES =====

function setLoading(loading) {
    state.isLoading = loading;
    elements.sendButton.disabled = loading;
    elements.userInput.disabled = loading;
    elements.indicatorText.textContent = loading ? 'Recherche en cours...' : 'Prêt à répondre';
}

function updateTheme() {
    if (state.matiere) {
        document.body.setAttribute('data-theme', state.matiere);
    } else {
        document.body.removeAttribute('data-theme');
    }
}

function updateIndicator() {
    const niveau = elements.niveauSelect.options[elements.niveauSelect.selectedIndex].text;
    const matiere = state.matiere ?
        elements.matiereSelect.options[elements.matiereSelect.selectedIndex].text :
        'Toutes matières';

    if (!state.isLoading) {
        elements.indicatorText.textContent = `${niveau} • ${matiere}`;
    }
}

function autoResizeTextarea() {
    const textarea = elements.userInput;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function scrollToBottom() {
    elements.messagesContainer.scrollTo({
        top: elements.messagesContainer.scrollHeight,
        behavior: 'smooth'
    });
}

// ===== MESSAGE CREATION =====

function addUserMessage(text) {
    const clone = templates.userMessage.content.cloneNode(true);
    const content = clone.querySelector('.message-content');
    content.textContent = text;

    elements.messagesContainer.appendChild(clone);
    scrollToBottom();
}

function addBotMessage(text, sources = []) {
    const clone = templates.botMessage.content.cloneNode(true);
    const content = clone.querySelector('.message-content');
    const sourcesContainer = clone.querySelector('.message-sources');

    // Format message content
    content.innerHTML = formatMarkdown(text);

    // Add sources if any
    if (sources && sources.length > 0) {
        const sourcesTitle = document.createElement('div');
        sourcesTitle.style.cssText = 'font-weight: 700; margin-bottom: 0.5rem; font-size: 0.9rem; opacity: 0.9;';
        sourcesTitle.textContent = `📚 Sources (${sources.length})`;
        sourcesContainer.appendChild(sourcesTitle);

        sources.forEach((source, index) => {
            const sourceEl = createSourceElement(source, index);
            sourcesContainer.appendChild(sourceEl);
        });
    }

    elements.messagesContainer.appendChild(clone);
    scrollToBottom();
}

function addLoadingMessage() {
    const clone = templates.loading.content.cloneNode(true);
    elements.messagesContainer.appendChild(clone);
    scrollToBottom();
    return elements.messagesContainer.lastElementChild;
}

// ===== FORMATTING =====

function formatMarkdown(text) {
    // Simple markdown-like formatting
    let formatted = text;

    // Bold: **text**
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic: *text*
    formatted = formatted.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');

    // Code: `code`
    formatted = formatted.replace(/`(.+?)`/g, '<code style="background: rgba(255,255,255,0.2); padding: 0.2rem 0.4rem; border-radius: 4px; font-family: monospace;">$1</code>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

function createSourceElement(source, index) {
    const sourceEl = document.createElement('div');
    sourceEl.className = 'source-item';
    sourceEl.style.animationDelay = `${index * 80}ms`;

    const icon = getSubjectIcon(source.matiere);
    const title = source.titre || 'Source';
    const matiereText = formatMatiere(source.matiere);

    sourceEl.innerHTML = `
        <span style="font-size: 1.2rem;">${icon}</span>
        <span style="flex: 1; font-weight: 600;">${title}</span>
        <span style="opacity: 0.8; font-size: 0.85rem;">${matiereText}</span>
    `;

    if (source.url) {
        sourceEl.style.cursor = 'pointer';
        sourceEl.addEventListener('click', () => window.open(source.url, '_blank'));
    }

    return sourceEl;
}

// ===== HELPERS =====

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

function formatMatiere(matiere) {
    const names = {
        'mathematiques': 'Maths',
        'francais': 'Français',
        'histoire_geo': 'Histoire-Géo',
        'svt': 'SVT',
        'physique_chimie': 'Physique-Chimie',
        'technologie': 'Techno',
        'anglais': 'Anglais',
        'espagnol': 'Espagnol'
    };
    return names[matiere] || matiere;
}

// ===== START =====

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

console.log('📚 Cahier Numérique - Frontend loaded');
