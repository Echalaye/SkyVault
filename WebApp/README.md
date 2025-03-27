# SkyVault - Application de Monitoring

Cette application web permet de visualiser les données de capteurs (humidité et gaz) récupérées à partir d'un Raspberry Pi via Firebase Realtime Database.

## Fonctionnalités

- Affichage des données d'humidité et de gaz en temps réel
- Indicateur de statut en ligne/hors ligne du Raspberry Pi
- Mode sombre/clair
- Bouton de rafraîchissement des données

## Installation

1. Clonez ce dépôt
2. Installez les dépendances:

```bash
npm install
```

3. Copiez le fichier `.env.example` en `.env` et remplissez-le avec vos informations Firebase (uniquement pour Realtime Database):

```bash
cp .env.example .env
```

4. Démarrez l'application en mode développement:

```bash
npm run dev
```

## Structure des données Firebase

L'application utilise uniquement Firebase Realtime Database et s'attend à une structure de données comme suit:

```json
{
  "data_humidity": {
    "last_updated": 1743082809606,
    "topic": "data/humidity",
    "value": "33"
  },
  "data_gas": {
    "last_updated": 1743082813421,
    "topic": "data/gas",
    "value": "125"
  }
}
```

## Technologies utilisées

- React
- TypeScript
- Vite
- TailwindCSS
- Shadcn/UI
- Firebase Realtime Database

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ["./tsconfig.node.json", "./tsconfig.app.json"],
      tsconfigRootDir: import.meta.dirname,
    },
  },
});
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from "eslint-plugin-react-x";
import reactDom from "eslint-plugin-react-dom";

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    "react-x": reactX,
    "react-dom": reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs["recommended-typescript"].rules,
    ...reactDom.configs.recommended.rules,
  },
});
```
