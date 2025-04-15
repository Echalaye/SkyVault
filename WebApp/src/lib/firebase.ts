import { initializeApp } from "firebase/app";
import { getDatabase, ref, get } from "firebase/database";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import type { RaspberryData } from "@/types";

// Configuration Firebase
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

// Email et mot de passe pour l'authentification
const ADMIN_EMAIL = "nathiii045@gmail.com";
const ADMIN_PASSWORD = "Skyvault";

// Initialisation de Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);
const auth = getAuth(app);

// Fonction pour s'authentifier avec email et mot de passe
export async function signInAdmin() {
  try {
    const userCredential = await signInWithEmailAndPassword(
      auth,
      ADMIN_EMAIL,
      ADMIN_PASSWORD
    );
    console.log("Authentifié comme admin", userCredential.user.uid);
    return userCredential.user;
  } catch (error) {
    console.error("Erreur d'authentification:", error);
    throw error;
  }
}

// Fonction pour récupérer les données du Raspberry Pi
export async function fetchRaspberryData(): Promise<RaspberryData> {
  try {
    // Vérifier si l'utilisateur est connecté, sinon se connecter
    if (!auth.currentUser) {
      await signInAdmin();
    }

    const raspberryRef = ref(database, "sensors/");
    const snapshot = await get(raspberryRef);
    console.log(snapshot.val());

    if (snapshot.exists()) {
      return snapshot.val() as RaspberryData;
    } else {
      throw new Error("Aucune donnée disponible");
    }
  } catch (error) {
    console.error("Erreur lors de la récupération des données:", error);
    throw error;
  }
}
