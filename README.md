# Dev_project
Système de surveillance

Page de documentation de Mikrotik :https://wiki.mikrotik.com/wiki/Manual:TOC

Nous avons utilisé la solution Mikrotik qui est un émulateur de routeur, la documentation ci-dessous pour voir son fonctionnement.
https://mikrotik.com/download#

En complément de nos routeurs, nous avons aussi utilisé l'utilitaire WinBox pour la configuration et la gestion graphique de nos routeurs.
https://mikrotik.com/download#

Configuration du routeur :
- Installer Mikrotik sur une VM, la démarrer et récupérer l'adresse MAC du routeur (interface / print brief).
- Installer Winbox et se connecter avec l'adresse MAC recupéré précédemment.
- Pour obtenri des adresses sur les interfaces du router, dans la colonne de droite, aller dans ip -> dhclient.

Pour démarrer le serveur web :
- Lancer le fichier main.py

Login/ Password pour accéder au système de supervision :
admin/admin

Sur l'interface web :
- Modifier les adresses pour les adapter à votre configuration.
- Cliquer sur superviser pour voir les valeurs s'affichées sur la page d'acceuil.



