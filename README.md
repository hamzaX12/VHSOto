# VHSOnto — Web Sémantique pour la valorisation du patrimoine de Safi 🏛️📍

Ce projet est une application web simple permettant d'afficher sur une carte interactive les lieux patrimoniaux, les événements culturels, les artisans et les services touristiques de la ville de Safi à partir d'une ontologie RDF.

---

## 🌐 Description du projet

VHSOnto utilise :
- 🐍 **FastAPI** pour servir l'application backend
- 📄 **rdflib** pour charger et interroger les données RDF
- 🗺️ **Leaflet.js** pour afficher les lieux sur une carte
- 📁 **Jinja2** pour les templates HTML

Les entités qui possèdent des coordonnées (`aPourCoordonnées`) sont affichées automatiquement sur la carte.

---

## 📦 Technologies utilisées

- Python 3.9+
- FastAPI
- rdflib
- Jinja2
- HTML / CSS / JavaScript
- Leaflet.js
- OpenStreetMap

---

## 🚀 Instructions pour exécuter le projet

### 1. Cloner le dépôt
```bash
git clone git@github.com:hamzaX12/VHSOto.git
cd VHSOto

### 3. Installer les dépendances
```bash
pip install fastapi uvicorn rdflib jinja2

### 4. Lancer le serveur FastAPI
```
   uvicorn main:app --reload
```
### Ouvrez votre navigateur à l'adresse :
👉 http://127.0.0.1:8000


