#import "@preview/polylux:0.4.0": *

#let primary-color = rgb("#343885") // Indigo-like Blue matching the reference
#let secondary-color = rgb("#E0E0E0") 
#let text-color = rgb("#333333")

// --- Layout & Theme ---
#let academic-theme(footer-left: [], footer-center: [], body) = {
  set page(
    paper: "presentation-16-9",
    margin: (rest: 0cm, bottom: 1cm),
    footer: context {
      set text(size: 10pt, fill: white)
      block(
        fill: primary-color,
        width: 100%,
        height: 100%, // Fill the footer area
        inset: (x: 1cm, y: 0.2cm),
        grid(
          columns: (1fr, 2fr, 1fr),
          align(left + horizon, footer-left),
          align(center + horizon, footer-center),
          align(right + horizon, context {
            counter(page).display() + " / " + str(counter(page).final().at(0))
          })
        )
      )
    },
    footer-descent: 0.5cm, // Ensure footer sticks to bottom with no gap // Ensure footer sticks to bottom with no gap
  )
  set text(font: "DejaVu Sans", size: 15pt, fill: text-color)
  set strong(delta: 300)
  set par(justify: true)
  
  body
}

// --- Slide Wrappers ---

#let new-slide(title: none, content) = {
  slide({
    pad(x: 1.5cm, y: 1cm, {
      if title != none {
        // Regular slides: Title in primary color with a separator line
        text(fill: primary-color, weight: "bold", size: 1.4em, title)
        v(0.3em)
        line(length: 100%, stroke: 2pt + primary-color)
        v(0.8em)
      } else {
        v(2em)
      }
      content
    })
  })
}

#let title-slide-custom(title, subtitle, authors) = {
  slide({
    // Full centered layout for title slide
    align(center + horizon, {
      // Title Box (Rounded, Blue, Shadow-like feel via spacing)
      block(
        fill: primary-color,
        radius: 15pt,
        width: 90%,
        inset: (y: 1.5em, x: 1em),
        {
          text(size: 2em, weight: "bold", fill: white, title)
          if subtitle != none {
            v(0.5em)
            text(size: 1.2em, fill: white.darken(5%), subtitle)
          }
        }
      )
      
      v(2cm)
      
      // Authors section
      text(size: 1.1em, weight: "regular", authors)
    })
  })
}

// --- Content ---

#show: academic-theme.with(
  footer-left: [Soutenance Projet - 20/12/2025],
  footer-center: [C.L.A.R.A.],
)

// --- Slide 1: Title ---
#title-slide-custom(
  "C.L.A.R.A.",
  "Agentification & Analyse d'Images Médicales",
  [
    *Membres du groupe:*
    #v(1em)
    #grid(
      columns: (2.5cm, 2.5cm, 2.5cm, 2.5cm), // Fixed column widths
      gutter: 0pt, // No spacing between columns
      align: center + horizon, // Center the entire grid
      [
        #block(clip: true, width: 2.5cm, height: 2.5cm, image("images/aglae.tournois.jpg", fit: "cover"))
        #v(0.2em)
        #align(center)[#text(size: 0.5em)[aglae.tournois]]
      ],
      [
        #block(clip: true, width: 2.5cm, height: 2.5cm, image("images/andy.shan.jpg", fit: "cover"))
        #v(0.2em)
        #align(center)[#text(size: 0.5em)[andy.shan]]
      ],
      [
        #block(clip: true, width: 2.5cm, height: 2.5cm, image("images/lois.breant.jpg", fit: "cover"))
        #v(0.2em)
        #align(center)[#text(size: 0.5em)[lois.breant]]
      ],
      [
        #block(clip: true, width: 2.5cm, height: 2.5cm, image("images/oscar.le-dauphin.jpg", fit: "cover"))
        #v(0.2em)
        #align(center)[#text(size: 0.5em)[oscar.le-dauphin]]
      ]
    )
  ]
)

// --- Slide 2: Introduction ---
#new-slide(title: "Introduction & Objectifs")[ 
  *Contexte :* 
  Module "Agentification" - SCIA/Santé 3ème Année.
  
  *Problématique :*
  Comment transformer une analyse d'image médicale "boîte noire" en un processus transparent, planifié et vérifiable ?

  #v(0.5em)
  *Objectif :*
  Créer un agent capable de :
  - *Planifier* son analyse (qualité, zone, anomalies).
  - *Utiliser des outils* (Vision, Classification).
  - *Contextualiser* ses actions (Mémoire à court terme).

  #v(1em)
  #block(fill: secondary-color, inset: 0.5em, radius: 5pt, width: 100%)[
    #text(style: "italic")[
      "L'avenir de l'IA réside dans des systèmes capables de raisonner, de planifier et d'apprendre des modèles du monde."
    ] \ 
    - *Yann LeCun* (Objective-Driven AI)
  ]
]

// --- Slide 3: Architecture Globale ---
#new-slide(title: "Architecture du Système")[ 
  *Approche Modulaire :*
  - *Backend (FastAPI) :* Orchestration des agents (Planner, Executor, Reactive).
  - *Frontend (React/Vite) :* Visualisation temps réel du graphe de raisonnement. 
  
  #align(center)[
    #image("../report/images/architecture.png", height: 50%)
    #v(0.5em)
    #text(size: 0.8em, style: "italic")[Figure 1 : Architecture Globale et Flux de Données]
  ]
]

// --- Slide 4: Motifs de Conception (Design Patterns) ---
#new-slide(title: "Motifs Agentiques Clés")[ 
  #grid(columns: (1fr, 1fr), gutter: 1.5cm,
    [
      *1. Planner-Executor*
      - *Pourquoi ?* L'analyse médicale est procédurale.
      - *Comment ?* Le Planner décompose (ex: "Vérifier radio"), l'Executor agit.
      
      #v(0.5em)
      *2. Mémoire (Contextuelle)*
      - *Pourquoi ?* Partager les résultats entre les tâches.
      - *Comment ?* Résolution de variables (`$step_id`) et passage de contexte.
    ],
    [
      *3. Outils & Délégation*
      - *Pourquoi ?* Utiliser des experts pour chaque sous-tâche.
      - *Comment ?* L'Executor délègue à `vision_tool` ou `classification_tool` selon le plan.
      
      #v(1em)
      #block(fill: secondary-color, inset: 0.5em, radius: 5pt, width: 100%)[
        *Note:* Ces motifs augmentent la traçabilité et la robustesse.
      ]
    ]
  )
]

// --- Slide 5: Implémentation Technique ---
#new-slide(title: "Stack Technique & Streaming")[ 
  *Backend :*
  - Python 3.13, FastAPI.
  - Modèles : `google/gemma-3-27b-it` (Vision & Texte).
  - Client `openrouter`.

  *Frontend :*
  - React 19, Tailwind CSS v4.
  - Graphe dynamique (Mermaid/Recharts).

  #v(1em)
  #block(stroke: (left: 4pt + primary-color), inset: (left: 1em))[
    *Streaming Temps Réel :* \ 
    Flux continu JSON (`AgentResponse`). L'utilisateur voit l'agent "réfléchir" étape par étape, améliorant la confiance utilisateur.
  ]
]

// --- Slide 6: Protocole d'Évaluation ---
#new-slide(title: "Évaluation & Métriques")[ 
  *Méthodologie :*
  Comparaison sur 50 cas cliniques variés (Fractures, Pneumonies, Normal).

  #v(1em)
  *Métriques suivies (via Telemetrics):*
  - *Taux de Succès :* Pertinence du diagnostic final vs Ground Truth.
  - *Latence :* Temps total de traitement (Planner + Execution).
  - *Consommation :* Nombre de tokens (Input/Output) par étape.
  
  #v(1em)
  *Instrumentation :*
  - Logging automatique dans `telemetrics.csv`.
  - Suivi détaillé par `session_id` et `agent_id`.
]

// --- Slide 7: Analyse Économique ---
#new-slide(title: "Coûts & Scalabilité")[ 
  *Modèle Économique :*
  
  #grid(columns: (1fr, 1fr), gutter: 1cm,
    [
      - *Stratégie Actuelle :* Utilisation de modèles "Free Tier" (Gemma, Llama) via OpenRouter pour le développement.
      - *Coût Réel :* Quasi-nul pour le prototype.
      
      #v(1em)
      *Suivi des Coûts :*
      Chaque appel API est loggé avec :
      - Modèle utilisé.
      - Tokens (Prompt + Completion).
      - Latence.
    ],
    [
      #align(center + horizon)[
        #image("../report/images/provider_costs.svg", height: 45%)
        #v(0.5em)
        #text(size: 0.8em, style: "italic")[Figure 2 : Simulation des Coûts]
      ]
      #align(center)[
        #v(0em)
        *Optimisation :* \ Le Planner consomme peu (contexte court), l'Executor (Vision) est le poste principal.
      ]
    ]
  )
]

// --- Slide 8: Conclusion & Perspectives ---
#new-slide(title: "Conclusion")[ 
  #grid(columns: (1fr, 1fr), gutter: 1cm,
    [
      *Apports du projet :*
      - Architecture agentique fonctionnelle (Planner-Executor).
      - Transparence accrue pour le praticien (Graphe de pensée).
      - Démonstration de la viabilité des modèles Open Source.
    ],
    [
      *Perspectives :*
      - *Latence :* Optimiser le streaming et paralléliser.
      - *Robustesse :* Ajouter un agent "Critic" pour valider les diagnostics.
      - *Mémoire :* Intégrer un vrai RAG pour l'historique médical.
    ]
  )
]

// --- Slide 9: Q&A ---
#title-slide-custom(
  "Démo Time",
  none,
  none
)
