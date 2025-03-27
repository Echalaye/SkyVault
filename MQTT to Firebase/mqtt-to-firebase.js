const mqtt = require("mqtt");
const admin = require("firebase-admin");
const fs = require("fs");
const path = require("path");
const { InfluxDB, Point } = require("@influxdata/influxdb-client");
const { WriteApi } = require("@influxdata/influxdb-client-apis");
require("dotenv").config({ path: path.join(__dirname, "../InfluxDB/.env") });

// Configuration InfluxDB
const influxConfig = {
  url: "http://localhost:8086",
  token: process.env.INFLUXDB_ADMIN_TOKEN,
  org: process.env.INFLUXDB_ORG,
  bucket: process.env.INFLUXDB_BUCKET,
};

console.log("Configuration InfluxDB:", {
  ...influxConfig,
});

// Initialiser le client InfluxDB
const influxDB = new InfluxDB({
  url: influxConfig.url,
  token: influxConfig.token,
});
const writeApi = influxDB.getWriteApi(
  influxConfig.org,
  influxConfig.bucket,
  "s",
  1000
);

// Chemin vers votre fichier de clé de service Firebase
const serviceAccountPath = path.join(__dirname, "serviceAccountKey.json");

// Configuration MQTT
const mqttConfig = {
  host: "skyvault.local", // Adresse de votre Raspberry Pi avec Mosquitto
  port: 1883,
  username: "admin", // Si configuré dans mosquitto.conf
  password: "admin", // Si configuré dans mosquitto.conf
  clientId: "mqtt-firebase-bridge-" + Math.random().toString(16).substr(2, 8),
};

// Sujets MQTT à écouter - Ajout de plus de sujets pour capturer toutes les données
const topics = ["sensors/humidity", "sensors/gas"];

// Initialiser Firebase Admin
try {
  if (!fs.existsSync(serviceAccountPath)) {
    console.error(
      "Erreur: Fichier de clé de service Firebase non trouvé.",
      "\n",
      "Veuillez créer un projet Firebase, générer une clé de service et la sauvegarder dans serviceAccountKey.json",
      "\n",
      "Pour cela, suivez les instructions ci-dessous:",
      "\n",
      "1. Allez sur https://console.firebase.google.com/",
      "\n",
      "2. Créez un nouveau projet ou sélectionnez un projet existant",
      "\n",
      "3. Dans les paramètres du projet, allez à 'Comptes de service'",
      "\n",
      "4. Générez une nouvelle clé privée",
      "\n",
      "5. Sauvegardez le fichier JSON téléchargé sous le nom 'serviceAccountKey.json' dans ce dossier"
    );
    process.exit(1);
  }

  const serviceAccount = require(serviceAccountPath);
  console.log(`Projet Firebase détecté: ${serviceAccount.project_id}`);

  const databaseURL = `https://skyvault-9ae81-default-rtdb.europe-west1.firebasedatabase.app/`;
  console.log(`Tentative de connexion à la base de données: ${databaseURL}`);

  // Initialiser l'application Firebase
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: databaseURL,
  });

  console.log("Firebase initialisé avec succès");
} catch (error) {
  console.error("Erreur lors de l'initialisation de Firebase:", error);
  process.exit(1);
}

// Référence à la Realtime Database uniquement
const realtimeDb = admin.database();
console.log("Connexion à Realtime Database établie");

// Connexion au broker MQTT
console.log("Connexion au serveur MQTT en cours...");
const client = mqtt.connect(`mqtt://${mqttConfig.host}:${mqttConfig.port}`, {
  username: mqttConfig.username,
  password: mqttConfig.password,
  clientId: mqttConfig.clientId,
});

if (!client) {
  console.error("Erreur lors de la connexion au serveur MQTT");
  process.exit(1);
}

// Garder une trace des sujets découverts
const discoveredTopics = new Set();

client.on("connect", () => {
  console.log("Connecté au broker MQTT");

  // S'abonner aux sujets
  topics.forEach((topic) => {
    client.subscribe(topic, (err) => {
      if (!err) {
        console.log(`Abonné au sujet: ${topic}`);
      } else {
        console.error(`Erreur lors de l'abonnement au sujet ${topic}:`, err);
      }
    });
  });
});

client.on("message", async (topic, message) => {
  try {
    const messageStr = message.toString();

    // Ajouter le sujet à la liste des sujets découverts s'il est nouveau
    if (!discoveredTopics.has(topic)) {
      discoveredTopics.add(topic);
      console.log(`Nouveau sujet découvert: ${topic}`);
      console.log(
        `Liste des sujets découverts: ${Array.from(discoveredTopics).join(
          ", "
        )}`
      );
    }

    console.log(`Message reçu sur ${topic}: ${messageStr}`);

    // Extraire le nom du capteur du sujet (ex: "sensors/gas" -> "gas")
    const sensorName = topic.split("/").pop();

    // Ajouter des métadonnées avec la nouvelle structure simplifiée
    const record = {
      value: messageStr,
      topic: topic,
    };

    // Stocker dans Realtime Database
    try {
      // Créer une structure de chemin simplifiée
      const dbPath = `sensors/${sensorName}`;

      // Stocker la dernière valeur
      await realtimeDb.ref(dbPath).set({
        ...record,
        last_updated: admin.database.ServerValue.TIMESTAMP,
      });

      console.log(
        `Données enregistrées dans Realtime Database pour ${sensorName}`
      );

      // Envoyer les données vers InfluxDB
      const point = new Point("sensor_data")
        .tag("topic", topic)
        .floatField("value", parseFloat(messageStr))
        .timestamp(new Date());

      await writeApi.writePoint(point);
      console.log(`Données enregistrées dans InfluxDB pour ${topic}`);
    } catch (error) {
      console.error(
        "Erreur lors de l'enregistrement dans la base de données:",
        error
      );
    }
  } catch (error) {
    console.error("Erreur lors du traitement du message:", error);
  }
});

// Afficher les statistiques toutes les minutes
setInterval(() => {
  console.log(`--- Statistiques ---`);
  console.log(
    `Sujets découverts (${discoveredTopics.size}): ${Array.from(
      discoveredTopics
    ).join(", ")}`
  );
  console.log(`-------------------`);
}, 60000);

client.on("error", (error) => {
  console.error("Erreur MQTT:", error);
});

// Gestion de la fermeture propre
process.on("SIGINT", () => {
  console.log("Fermeture des connexions...");
  client.end();
  writeApi.close();
  process.exit(0);
});
