# SkyVault

## Sommaire

- [SkyVault](#SkyVault)
  - [I- Installation de la solution](#i-installation-de-la-solution)
    - [A. Configuration du Raspberry](#a-configuration-du-raspberry)
    - [B. Configuration de l'ESP32](#b-configuration-de-lesp32)
    - [C. Configuration du Webrepl](#c-configuration-du-webrepl)
    - [D. Configuration de Firebase](#d-configuration-de-firebase)
    - [E. Configuration de l'application Web](#e-configuration-de-lapplication-web)
  - [II- Lancement de la solution](#ii-lancement-de-la-solution)
    - [1- Lancer le raspberry](#1-lancer-le-raspberry)
    - [2- Lancer l'ESP32 publisher](#2-lancer-lesp32-publisher)
    - [3- Lancer l'ESP32 subscriber](#3-lancer-lesp32-subscriber)
    - [4- Lancer l'application Web](#4-lancer-lapplication-web)

# I. Installation de la solution

1- Clonez ce dépôt

2- Suivez le schéma d'installation dans le dossier **schema**.

> [!ATTENTION]
> Pour voir le schéma, ouvrez [wokwi](https://wokwi.com/projects/305568836183130690)
> Copiez-collez le fichier .json dans le **diagram.json** sur wokwi

### A. Configuration du Raspberry

- **Préparation de l'OS** : installation de Raspberry Pi OS [ici](https://www.raspberrypi.com/software/). Renommez l'hostname de la machine en skyvault.local

- **Installation de Docker et Docker Compose** :

```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh --dry-run
```

- **Configuration du Raspberry - MQTT** :

Créer un dossier dans le répertoire racine, et y mettre le fichier docker-compose.yml (issu du dossier MQTT).

Une fois fait, lancer la commande `docker compose up` dans le répertoire racine.

Le serveur MQTT est maintenant opérationnel.

- **Configuration du Raspberry - InfluxDB et Grafana** :

Créer un dossier dans le répertoire racine, et y mettre le fichier docker-compose.yml (issu du dossier InfluxDB et Grafana) et le fichier .env (à partir du fichier .env.example).

Une fois fait, lancer la commande `docker compose up` dans le répertoire racine.

Le serveur InfluxDB et Grafana est maintenant opérationnel.

### B. Configuration de l'ESP32

- **Sur l'ESP32 publisher** :

  - Ajoutez le script esp32_pub.py dans l'ESP32 (fichier dans le dossier MQTT)
  - Ajoutez la ligne `import esp32_pub` dans le fichier boot.py de l'ESP32

- **Sur l'ESP32 subscriber** :
  - Ajoutez le script esp32_pub.py dans l'ESP32 (fichier dans le dossier MQTT)
  - Ajoutez la ligne `import esp32_sub` dans le fichier boot.py de l'ESP32
  - Ajoutez les fichiers **esp32_gpio_lcd.py** et **lcd_api.py** dans l'ESP32 (fichiers dans le dossier library)

### C. Configuration du Webrepl

- **Sur l'ESP32 publisher** :
  - Connectez-vous à l'ESP32
  - Dans l'interpréteur de commandes Thonny IDE, utilisez cette commande : `import webrepl_setup`
  - Définissez un mot de passe
  - Maintenant suivez ce [tutoriel](https://bhave.sh/micropython-webrepl-thonny/)

> [!REMARQUE]
> L'adresse IP est statique : 192.168.234.96.
> N'oubliez pas de mettre votre mot de passe.

- **Sur l'ESP32 subscriber** :
  - Connectez-vous à l'ESP32
  - Dans l'interpréteur de commandes Thonny IDE, utilisez cette commande : `import webrepl_setup`
  - Définissez un mot de passe
  - Maintenant suivez ce [tutoriel](https://bhave.sh/micropython-webrepl-thonny/)

> [!REMARQUE]
> L'adresse IP est statique : 192.168.234.222.
> N'oubliez pas de mettre votre mot de passe.

### D. Configuration de Firebase

- **Lancez les commandes suivantes sur votre ordinateur** :

```bash
cd MQTT\ to\ Firebase/
npm i
```

Il vous faut maintenant créer un projet sur le site Firebase, puis créer une Realtime Database.

Une fois fait, téléchargez votre serviceAccountKey.json, et placez-le dans le dossier "MQTT To Firebase".

La configuration de Firebase est terminée, créez maintenant le même fichier .env que celui utilisé pour le raspberry.

### E. Configuration de l'application Web

- **Lancez les commandes suivantes sur votre ordinateur** :

```bash
cd WebApp/
npm i
```

Si vous voulez construire l'application en production, utilisez plutôt ces commandes :

```bash
cd WebApp/
npm i
npm run build
```

# II. Lancement de la solution

Une fois tous les composants installés, vous pouvez lancer la solution en faisant ces actions dans l'ordre :

1. **Lancer le raspberry** :

Vérifier que le serveur MQTT est bien lancé, et que le serveur Web est accessible.

2. **Lancer l'ESP32 publisher** :

Exécutez le script esp32_pub.py sur l'ESP32 publisher.

3. **Lancer l'ESP32 subscriber** :

Exécutez le script esp32_sub.py sur l'ESP32 subscriber.

4. **Lancer l'application Web** :

Lancez l'application Web en exécutant la commande `npm run dev` dans le dossier WebApp.
