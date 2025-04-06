# Application d'Annotation pour YOLO Pose au format COCO

Cette application Python 3 permet d'annoter des datasets destinés à la détection de poses humaines pour le modèle YOLO, en utilisant le format d'annotation COCO. Elle permet de charger des images et leurs annotations associées (fichier `annotations.coco.json`), puis de modifier et sauvegarder de nouveaux points d'annotation pour chaque image.

## Fonctionnalités principales

- **Chargement d'un dataset au format COCO** : 
  L'application charge un dataset d'images et d'annotations au format COCO. Le fichier `annotations.coco.json` est analysé pour extraire les informations nécessaires (images, keypoints).
  
- **Affichage des images et des keypoints** : 
  Pour chaque image du dataset, l'application affiche l'image correspondante et superpose les points clés (keypoints) sous forme de cercles.
  
- **Déplacement des keypoints** : 
  L'utilisateur peut déplacer les cercles représentant les keypoints à l'aide de la souris. Les coordonnées des cercles sont mises à jour en temps réel.
  
- **Ajustement de la taille des cercles** : 
  L'utilisateur peut ajuster la taille des cercles via un curseur placé à gauche de la fenêtre.

- **Zoom et navigation de l'image** :
  Des boutons permettent de zoomer et dézoomer l'image pour une vue plus précise. L'utilisateur peut également déplacer l'image (pan) en mode "grab", permettant de déplacer l'image dans toutes les directions.
  Un bouton "reset zoom" permet de réinitialiser le zoom de l'image.

- **Sauvegarde des annotations** :
  Un bouton "Sauvegarder" permet d'écrire les nouvelles coordonnées des keypoints modifiés dans le fichier `annotations.coco.json`, mettant à jour le champ `keypoints` de l'élément `annotations` correspondant à l'index de l'image actuelle.

- **Navigation entre les images** :
  Un bouton "Suivant" permet de passer à l'image suivante dans le dataset (index +1). Un bouton "Précédent" permet de revenir à l'image précédente (index -1).
  À chaque changement d'image, les cercles sont automatiquement positionnés selon les coordonnées des keypoints de cette image, et l'utilisateur peut les ajuster à nouveau.

## Prérequis

Pour exécuter cette application, vous aurez besoin des éléments suivants :

- Testé avec **Python 3.12.3** 
- **Tkinter** : pour créer l'interface graphique.
- **Pillow** : pour charger et manipuler les images.
- **JSON** : pour traiter le fichier d'annotations COCO.

### Installation des dépendances

1. Clonez ce dépôt :

   ```bash
   git clone https://github.com/muicka/tools/annotation-yolo-pose.git
   cd annotation-yolo-pose
2. Installez les dépendances via pip :

   ```bash
   pip install -r requirements.txt

3. Exécutez le script Python 

   ```bash
   python3 app.py
