# Module Frontend - "Cahier Numérique"

## État
✅ **IMPLÉMENTÉ** - Design "Cahier Numérique" complet et fonctionnel

## Concept Design
**Aesthetic Direction**: "Cahier Numérique" - Modern French school notebook aesthetic
- Inspiration from iconic French school cahiers (squared paper notebooks)
- Subject-specific color coding (like colored section dividers)
- Clean, studious but youthful and motivating
- Subtle grid pattern background (like squared paper)

## Architecture
```
frontend/
├── index.html       # ✅ Page principale avec chat complet
├── style.css        # ✅ Design system "Cahier Numérique" (890+ lignes)
└── app.js           # ✅ Logique complète + appels API (295+ lignes)
```

## Fonctionnalités Implémentées
✅ **Interface principale**:
- En-tête avec branding animé et logo
- Sélecteurs niveau (6ème-3ème, college) et matière avec 8 options
- Zone de chat scrollable avec scroll automatique
- Templates de messages (utilisateur, bot, loading)

✅ **Messages**:
- Bulles utilisateur (accent color, alignées à droite)
- Bulles bot (blanc avec bordure accent, alignées à gauche)
- Message d'accueil expliquant le bot avec liste des matières
- Affichage des sources sous chaque réponse (titre, matière, icône)
- Formatage Markdown-like (gras, italique, listes, code)

✅ **Interactions**:
- Champ de saisie auto-resize (max 120px)
- Bouton envoyer avec animation rotation au hover
- Envoi avec Entrée (Shift+Entrée pour nouvelle ligne)
- Indicateur de chargement avec dots animés
- Désactivation input pendant requête

✅ **Thématisation dynamique**:
- Changement de couleur d'accent selon la matière sélectionnée
- 8 couleurs de matières (maths=bleu, français=violet, histoire=orange, etc.)
- Transitions fluides entre thèmes
- Icônes par matière (📐 📝 🗺️ 🔬 ⚗️ ⚙️ 🇬🇧 🇪🇸)

✅ **Design System**:
- **Typography**: Lexend (display, 600-800) + DM Sans (body, 400-700)
- **Colors**: Paper white (#fefdfb) + paper cream (#faf9f6) avec grille Séyès
- **Background**: Grille quadrillée 8x8px + texture papier subtile (SVG noise)
- **Animations**: fadeInDown, fadeInUp, messageSlideIn, bounce, loading dots
- **Shadows**: 4 niveaux paper-like (sm, md, lg, page)
- **Spacing**: Échelle 8-point (xs à 2xl)
- **Border radius**: 4 tailles (sm=8px à xl=20px)

✅ **Responsive Design**:
- Mobile-first approach
- Breakpoints: 768px (tablet), 480px (mobile)
- Grid adaptatif pour liste des matières
- Tailles de police réduites sur mobile
- Controls en colonne sur petit écran

✅ **Accessibilité**:
- Labels avec icônes pour les sélecteurs
- Focus visible pour navigation clavier
- ARIA labels sur boutons
- Respect de prefers-reduced-motion
- Contraste de couleurs suffisant

## Connexion Backend
- **API Base**: `http://localhost:8000`
- **Endpoint**: `POST /api/chat`
- **Payload**: `{question, niveau, matiere}`
- **Response**: `{answer, sources, nb_sources}`

## Technical Stack
- **HTML5** avec templates
- **CSS3** avec variables CSS, grid, flexbox
- **Vanilla JavaScript** (ES6+)
- **Google Fonts**: Lexend + DM Sans
- **Aucune dépendance** npm/CDN

## Caractéristiques Uniques
1. **Grille de fond dynamique** simulant un cahier quadrillé
2. **Couleurs par matière** qui transforment toute l'interface
3. **Sources cliquables** avec animation en cascade
4. **Auto-resize textarea** fluide
5. **Animations subtiles** mais impactantes (bounce logo, rotation bouton)
6. **Typographie distinctive** évitant les choix génériques

## Conventions
- Nommage des classes en français (ex: `.message-bulle`, `.controle-groupe`)
- Commentaires de code en français
- Messages console en français avec emojis
- Code structuré par sections avec séparateurs clairs
- Variables CSS pour cohérence du design system

## Comment Utiliser
1. Lancer le backend: `cd backend && uvicorn main:app --reload`
2. Ouvrir navigateur: `http://localhost:8000`
3. Sélectionner niveau et matière
4. Poser une question
5. Recevoir réponse avec sources

## Design Philosophy
> "Clean, studious, but youthful" - L'interface évite l'esthétique enfantine tout en restant accueillante et motivante pour les 11-15 ans. Chaque choix de couleur, d'espacement et d'animation a été pensé pour créer une expérience mémorable qui donne envie d'apprendre.
