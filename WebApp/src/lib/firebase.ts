import { initializeApp } from "firebase/app";
import { getDatabase, ref, get } from "firebase/database";
import type { RaspberryData } from "@/types";

// Configuration Firebase (uniquement pour Realtime Database)
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

// Initialisation de Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

// Fonction pour récupérer les données du Raspberry Pi
export async function fetchRaspberryData(): Promise<RaspberryData> {
  try {
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
