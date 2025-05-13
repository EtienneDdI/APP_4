## Simulateur d’Automates Défenseurs

Ce projet est une application Python avec interface graphique permettant de simuler le comportement de différents **automates de défense** dans un contexte inspiré du football robotique ou de la robotique décisionnelle. Il permet de visualiser les transitions d’états d’un automate sous forme de graphe dynamique.

---

## Fonctionnalités

- Interface graphique interactive avec **PyQt5**
- Affichage des graphes de transitions avec **matplotlib** et **networkx**
- Support de différents comportements :
  - Bloquer un adversaire
  - Se placer entre la balle et le but
  - Intercepter une passe
  - Marquer un joueur
  - Protéger le but
- Deux modes de simulation :
  - Aléatoire (choix automatique des événements)
  - Manuel (choix de l’événement par l'utilisateur)

---

## Lancer l’application

1. **Installer les dépendances** (de préférence dans un environnement virtuel) :

```bash
pip install -r requirements.txt
```

2. **Lancer l'application** :

```bash
python IHM.py
```

---

## Dépendances principales

- `PyQt5`
- `matplotlib`
- `networkx`
- `pydot` *(optionnel mais recommandé pour un affichage optimisé)*
- `graphviz` *(à installer aussi côté système si nécessaire)*

---

## Fichiers

- `IHM.py` — Code principal de l’interface et de la logique
- `requirements.txt` — Dépendances Python
- `APP_4.ipynb` — Carnet annexe (non indispensable à l’exécution de l’IHM)

---

## Auteur

- **Vincent**
- **Antoine**
- **Cléante**
- **Etienne**

---
