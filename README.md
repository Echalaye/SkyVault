# SkyVault

## Sommaire

- [SkyVault](#SkyVault)
  - [I- Installation de la solution](#i-installation-de-la-solution)
    - [A. Set Up Raspberry](#setuptrasp)
# I. Installation de la solution

1- Clonné ce répository

2- Suivre ce schéma de montage ![schéma installation](img/schema_montage.png)

### A. Set up raspberry <a name=setuprasp />
- **Préparation de l'os** : installation de Raspbery pi os [here](https://www.raspberrypi.com/software/). Renommer l'hostname de la machine en skyvault.local        

- **Installation de docker et docker compose** : 
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh --dry-run
```
- **Importe docker compose** : Récupérer le docker-compose.yml dans le dossier MQTT. Excuter la commande ``` docker compose up ```

### Set Up ESP32
- **Sur l'esp32 publisher** :
  - Ajouter le script esp32_pub.py dans l'esp32 (fichier dans le dossier MQTT)
  - Ajouter la ligne ```import esp32_pub``` dans le fichier boot.py de l'esp32

- **Sur l'esp32 subscriber** :
  - Ajouter le script esp32_pub.py dans l'esp32 (fichier dans le dossier MQTT)
  - Ajouter la ligne ```import esp32_sub``` dans le fichier boot.py de l'esp32
  - Ajouter les fichier **esp32_gpio_lcd.py** et **lcd_api.py** dans l'esp32 (fichier dans le dossier library)

### Set Up firebase
- **Lancer les commande suivante**: 

```bash
cd MQTTtoFirebase/
npm run install
```

penser a parler de import webrpl_setup dans la partie SetUp
