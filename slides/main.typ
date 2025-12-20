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
  set text(font: "DejaVu Sans", size: 14pt, fill: text-color)
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
  "C.L.A.R.A. 🩺",
  "LLM'S AGENTIC AND BIOMEDICAL - ING3 SCIA/Santé",
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
        #block(clip: true, width: 2.5cm, height: 2.5cm, image("images/lois.breant.png", fit: "cover"))
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
  *Problématique :*
  Comment concevoir un agent intelligent capable d'analyser des images médicales de manière autonome et explicable ?

  #v(0.5em)
  *Objectif :*
  Créer un agent capable de :
  - *Planifier* une analyse.
  - *Utiliser des outils pertinants* pour répondre aux attentes du patient.
  - *Mémoriser et contextualiser* ses actions.
  - *Minimiser les coûts* d'utilisation des LLMs.

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
  - *Backend (FastAPI) :* Orchestration des agents (Planner/Executor/Reactive).

  - *Frontend (React/Vite) :* Visualisation temps réel du graphe de raisonnement. 
  
  #align(center)[
    #image("../report/images/architecture.png", height: 50%)
    #v(0.5em)
    #text(size: 0.8em, style: "italic")[Figure 1 : Architecture Globale]
  ]
]

// Slides 4, 5, 6 lol
#new-slide(title: "Motifs Agentiques")[ 
  #set text(size: 1.5em)
  *1. Planner-Executor*
  #v(0.5em)
  - *Pourquoi ?* L'analyse médicale est procédurale.
  - *Comment ?* Le Planner décompose les actions, l'Executor agit.
]


#new-slide(title: "Motifs Agentiques")[ 
  #set text(size: 1.5em)
  #v(0.5em)
  *2. Mémoire (Contextuelle)*
  - *Pourquoi ?* Partager les résultats entre les tâches.
  - *Comment ?* Résolution de variables (`$step_id`) et passage de contexte.
]

#new-slide(title: "Motifs Agentiques")[ 
  #set text(size: 1.3em)
  *3. Outils & Délégation*
  L'Executor délègue les tâches perceptives :

  #v(0.5em)
  - *Outil Classification (CNN)*
    - *Input :* Image (Mammographie/Scan).
    - *Output :* Label (Bénin/Malin) + Confiance.

  #v(0.5em)
  - *Agent Vision (VLM)*
    - *Input :* Image + Instructions.
    - *Output :* Description textuelle et analyse visuelle.
]

// --- Slide 5: Implémentation Technique ---
#new-slide(title: "Stack Technique & Streaming")[ 
  *Backend :*
  - Python 3.13, FastAPI.
  - Modèle `google/gemma-3-27b-it` (Vision & Texte).
  - Client `openrouter`.

  *Frontend :*
  - React 19, Tailwind CSS v4.
  - Graphe dynamique (Mermaid/Recharts).

  #v(1em)
  #block(stroke: (left: 4pt + primary-color), inset: (left: 1em))[
    *Streaming de réponse en temps réel :* \ 
    Flux continu JSON (`AgentResponse`). L'utilisateur voit l'agent "réfléchir" et peut consulter chaque étape de la plannification.
  ]
]

// --- Slide 6: Protocole d'Évaluation ---
#new-slide(title: "Monitoring & Métriques")[
  *Approche :*
  Monitoring temps réel de la performance des agents via une instrumentation dédiée.

  #v(1em)
  *Métriques loggées :*
  - *Latence :* Temps d'exécution par étape (Planner/Executor/Vision).
  - *Consommation :* Comptage précis des tokens (Input/Output) pour l'analyse des coûts.
  
  #v(1em)
  *Instrumentation :*
  - Export automatique dans `telemetrics.csv`.
  - Permet d'identifier les goulots d'étranglement.
]
// --- Slide 7: Analyse Économique ---
#new-slide(title: "Coûts & Scalabilité")[ 
  *Modèle Économique :*
  
  #grid(columns: (1fr, 1fr), gutter: 1cm,
    [
      - *Stratégie :* Utilisation de modèles "Free Tier" (Gemma, Llama) via OpenRouter pour le développement.
      - *Coût réel :* Quasi-nul pour le prototype.
      
      #v(1em)
      *Suivi des coûts :*
      Chaque appel API est loggé avec :
      - Modèle utilisé.
      - Tokens (Prompt & Complétion).
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
        *Optimisation :* \ Le Planner est léger (texte), la Vision est le poste principal de consommation (images).
      ]
    ]
  )
]

// --- Slide 8: Conclusion & Perspectives ---
#new-slide(title: "Conclusion")[ 
  #grid(columns: (1fr, 1fr), gutter: 1cm,
    [
      *Apports du projet :*
      - Architecture agentique fonctionnelle (Planner/Executor).
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
  "Démo Time 🔥",
  none,
  none
)
