# Flask Agri-Shop App - CI/CD avec GitHub Actions, Docker et Azure

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

Le workflow GitHub Actions se compose de trois jobs, chacun correspondant à une étape clé du processus de construction, publication, et déploiement de l'application Flask. Voici une vue d'ensemble globale des trois jobs.

1. Build (Construction de l'image Docker)
Ce job est responsable de la construction de l'image Docker de l'application Flask. À partir du fichier Dockerfile, l'image est construite localement. Cependant, comme chaque job GitHub Actions s'exécute dans un environnement isolé, cette image n'est pas disponible pour les jobs suivants une fois le job terminé.
Pour garantir la disponibilité de l'image, elle est sauvegardée sous forme d'artefact (.tar) afin d'être partagée entre les jobs.

**Commandes principales** :

```bash
docker build -t flask-agriapp:v1 .
docker save flask-agriapp:v1 -o flask-agriapp.tar

```

2. Push (Publication de l'image sur DockerHub)
Ce job récupère l'image sauvegardée par le job précédent, la charge à nouveau dans Docker, puis la taggue et pousse sur DockerHub. Cela rend l'image disponible sur un registre public pour les étapes suivantes.


**Commandes principales** :

```bash
docker load -i flask-agriapp.tar
docker tag flask-agriapp:v1 ${{ secrets.DOCKER_USERNAME }}/flask-agriapp:v1
docker push ${{ secrets.DOCKER_USERNAME }}/flask-agriapp:v1
```

### 3. **Job: Deploy (Déploiement de l'application sur Azure)**

Ce job déploie l'application sur Azure Container Apps à l'aide de l'Azure CLI.

- **Actions** :
    - Authentification à Azure avec les secrets du Service Principal
    - Déploiement de l'image Docker depuis DockerHub vers Azure Container Apps

**Commandes principales** :

```bash
az login --service-principal -u ${{ secrets.AZURE_CLIENT_ID }} -p ${{ secrets.AZURE_CLIENT_SECRET }} --tenant ${{ secrets.AZURE_TENANT_ID }}
az containerapp create \
  --name flask-agriapp \
  --resource-group flask-agriapp-rg \
  --environment agriapp-env \
  --image ${{ secrets.DOCKER_USERNAME }}/flask-agriapp:v1 \
  --target-port 5000 \
  --ingress external \
  --cpu 0.5 --memory 1.0Gi
```
Il faut noter que le groupe resource `flask-agriapp-rg` et l'environment `agriapp-env``ont été déjà créé même si on pouvait le faire dans le job de déploiement.

## Résultats

Voici les résultats visuels du processus CI/CD :

### 1. **Image Docker sur DockerHub**
   L'image Docker construite et poussée vers DockerHub est disponible sous le nom `flask-agriapp:v1`. Vous pouvez la retrouver dans votre compte DockerHub.
    
   <img src="imagesDemo\imageDockurHub.png" width="1200" height="300">


### 2. **Image de l'ACR (Azure Container Registry)**
   Si vous utilisez un ACR pour stocker les images Docker, voici l'image de l'ACR où l'image a été poussée :

  <img src="imagesDemo\azureContainerRegister.png" width="1200" height="300">

   Details  
  <img src="imagesDemo\acr-details.png" width="1200" height="300">

### 3. **Image de l'App Déployée sur Azure Container Apps**
   L'application Flask est déployée sur Azure Container Apps et accessible via un endpoint public. Voici une capture d'écran de l'application déployée :

   Accueil
   <img src="imagesDemo\accueil-app-deployed.png" width="1200" height="300">

   Produits
   <img src="imagesDemo\produits-catalog.png" width="1200" height="300">

### 4. **Image de Succès des Jobs GitHub Actions**
   Voici une image montrant le succès des trois jobs dans GitHub Actions : **Build**, **Push**, et **Deploy**.

   Details de l'action réusssi
   <img src="imagesDemo\succes-jobs.png" width="1200" height="300">
