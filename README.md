# SkyVault

## Sommaire

- [SkyVault](#SkyVault)
  - [Sommaire](#sommaire)
  - [I. Introduction](#i-introduction)
  - [II- Fonctionnement](#ii-fonctionnement)
  - [III- Installation de la solution](#iii-installation-de-la-solution)


## I. Introduction

En 2180 des nuages denses de pollution très dangereux pour la santé se déplacent au gré du vent. Des pluies toxiques s'abatent sur les villes rendant les balcons toxique. 
SkyVault est une solution IOT de protection des balcons.

## II. Fonctionnement

SkyVault est une solution composé de:
- Un haut parleur (représentant la fermeture du balcon).
- Un capteur de gaz pour detecter la concentration en gaz dans l'air extérieur.
- Un capteur d'humidité pour détecter l'arrivé des pluies.
- Un ESP32 pour envoyer les données des capteur.
- Une Raspberry pour traiter les données et les envoyées a une base de données
- Un Cloud AWS pour stocker les données des capteur envoyé par les Raspberry

Lorsque la concentration de gaz est trop grande ou que le niveau d'humidité extérieur est trop hauts la raspberry enclanche le mécanisme de fermeture du balcon (fait sonné le haut parleur) pour protéger l'utilisateur des dangers extérieurs.

# III. Installation de la solution

1- Clonné ce répository

2- Suivre ce schéma de montage ![schéma installation](schema_wokwi.png)

3- Installer la lib **<DHT.h>** en utilisant le dossier zip stocker dans le dossier external_lib 

