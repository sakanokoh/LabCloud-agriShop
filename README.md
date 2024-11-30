# Flask Agri-Shop App - CI/CD avec GitHub Actions, Docker, Trivy et Azure

## Description du projet

Ce projet a pour objectif de déployer une application Flask (Flask AgriApp) sur Azure à l'aide de Docker et de GitHub Actions. L'application est construite dans un conteneur Docker, scannée pour des vulnérabilités de sécurité avec **Trivy**, puis déployée sur **Azure Container Apps**. Ce workflow assure une intégration continue et un déploiement continu (CI/CD), tout en garantissant la sécurité des images Docker.

## Outils nécessaires

1. **Git & GitHub** : Utilisé pour la gestion du code source et l'intégration avec GitHub Actions.
2. **Azure** : Compte Azure pour déployer l'application via Azure CLI et gérer les ressources sur Azure.
3. **Docker & DockerHub** : Utilisé pour la création, le stockage et le déploiement de l'image Docker.
4. **Python** : Langage utilisé pour développer l'application Flask.

## Cloner le projet

1. Clonez le repository sur votre machine locale en utilisant Git :
   ```bash
   git clone https://github.com/sakanokoh/LabCloud-agriShop.git
   cd LabCloud-agriShop
   ```

## S'authentifier sur Azure et créer un Service Principal

### Authentification via Azure CLI

1. **Connectez-vous à votre compte Azure** :
    
    ```bash
    az login
    
    ```
    
    Cela ouvrira une fenêtre de navigateur pour vous permettre de vous connecter à votre compte Azure.
    
2. **Créer un Service Principal (SP)** avec des droits nécessaires sur l'abonnement ou le groupe de ressources :
    
    ```bash
    az ad sp create-for-rbac --name "flask-agriapp-sp" --role Contributor --scopes /subscriptions/<subscription-id>/resourceGroups/<resource-group-name>
    
    ```
    
    Cette commande crée un **Service Principal** avec le rôle `Contributor` sur le groupe de ressources spécifié. Elle renverra des informations contenant :
    
    - **AppId** (client_id)
    - **Password** (client_secret)
    - **Tenant** (tenant_id)
3. **Ajouter ces valeurs aux secrets GitHub** :
Allez dans votre dépôt GitHub, puis dans **Settings** -> **Secrets** et ajoutez ces valeurs sous les noms suivants :
    - `AZURE_CLIENT_ID`
    - `AZURE_CLIENT_SECRET`
    - `AZURE_TENANT_ID`
En plus de ça, il faut faire de la même pour les credentials de DockerHub, après avoir les récupèrer depuis DockerHub 
    - `DOCKER_USERNAME`
    - `DOCKER_PASSWORD`

### Alternative pour la création Service Principal via le Portail Azure

1. Allez sur **Azure Portal** et dans **Azure Active Directory** -> **App registrations** -> **New registration**.
2. Créez une application en définissant un nom et l'URI de redirection.
3. Une fois l'application créée, allez dans **Certificates & secrets**, puis **New client secret** pour obtenir un client secret.
4. Allez dans **API permissions** et assignez le rôle `Contributor` à l'application pour l'accès au groupe de ressources ou à l'abonnement.

## Description des Jobs GitHub Actions

Le workflow GitHub Actions est divisé en trois jobs :

### 1. **Job: Build (Construction de l'image Docker)**

Ce job construit l'image Docker de l'application Flask et la pousse vers DockerHub.

- **Actions** :
    - Checkout du code source
    - Authentification DockerHub via un login sécurisé
    - Construction et envoi de l'image Docker vers DockerHub

**Commandes principales** :

```bash
docker build -t <username>/flask-agriapp:v1 .
docker push <username>/flask-agriapp:v1

```

### 2. **Job: Scan (Analyse de l'image Docker avec Trivy)**

Ce job effectue un scan de l'image Docker construite à la recherche de vulnérabilités de sécurité (vulnérabilités de sévérité `HIGH` et `CRITICAL`).

- **Actions** :
    - Téléchargement et installation de la base de données Trivy
    - Exécution du scan Trivy sur l'image Docker
    - Échec du job si des vulnérabilités sont détectées

**Commandes principales** :

```bash
trivy image --exit-code 1 --severity HIGH,CRITICAL <username>/flask-agriapp:v1

```

### 3. **Job: Deploy (Déploiement de l'application sur Azure)**

Ce job déploie l'application sur Azure Container Apps à l'aide de l'Azure CLI.

- **Actions** :
    - Authentification à Azure avec les secrets du Service Principal
    - Déploiement de l'image Docker depuis DockerHub vers Azure Container Apps

**Commandes principales** :

```bash
az containerapp create --name flask-agriapp --resource-group flask-agriapp-rg --environment agriapp-env --image <username>/flask-agriapp:v1 --target-port 5000 --ingress external --cpu 0.5 --memory 1.0Gi

```
Il faut noter que le groupe resource `flask-agriapp-rg` et l'environment `agriapp-env``ont été déjà créé même si on pouvait le faire dans le job de déploiement.

## Résultats

Voici les résultats visuels du processus CI/CD :

### 1. **Image Docker sur DockerHub**
   L'image Docker construite et poussée vers DockerHub est disponible sous le nom `flask-agriapp:v1`. Vous pouvez la retrouver dans votre compte DockerHub.
   
   ![Image Docker sur DockerHub](imagesDemo\imageDockurHub.png) 


### 2. **Image de l'ACR (Azure Container Registry)**
   Si vous utilisez un ACR pour stocker les images Docker, voici l'image de l'ACR où l'image a été poussée :

   ![ACR sur Azure](imagesDemo\azureContainerRegister.png)

   Details  
   ![Details ACR sur Azure](imagesDemo\acr-details.png)

### 3. **Image de l'App Déployée sur Azure Container Apps**
   L'application Flask est déployée sur Azure Container Apps et accessible via un endpoint public. Voici une capture d'écran de l'application déployée :

   Accueil
   ![App Déployée sur Azure](imagesDemo\accueil-app-deployed.png) 

   Produits
   ![App Déployée sur Azure](imagesDemo\produits-catalog.png)

### 4. **Image de Succès des Jobs GitHub Actions**
   Voici une image montrant le succès des trois jobs dans GitHub Actions : **Build**, **Scan**, et **Deploy**.

   Action echoué par le manque du niveau de securité recommandé
   ![Echec et Succès des Jobs GitHub Actions](imagesDemo\sec-fail-flow.png)  

   Details de l'action réusssi
    ![Details succès des Jobs GitHub Actions](imagesDemo\succes-jobs.png) 