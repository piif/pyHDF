Le programme `debiterCartes.py` a pour but d'effectuer en masse les paiements sur le site "génération HDF"
Pour s'en servir, il faut avoir installé l'environnement Python et disposer d'un accès à l'espace partenaire (voir [la doc d'installation](Installation.md))

Il faut partir d'un fichier texte contenant une ligne d'entête puis une ligne par débit à effectuer.  
L'entête est la suivante : `nom<tab>prénom<tab>numéro<tab>date de naissance<tab>montant`  
Chaque ligne doit donc contenir ces colonnes, séparées par des tabulations, comme ceci :  
`dupont<tab>pierre<tab>12345678<tab>01/02/2003<tab>20.00`

Si d'autres colonnes sont présentes, elles sont ignorées  
Si une ligne est vide, ou si elle commence par le caractère `#`, elle est ignorée

Ce format correspond à la sortie de la commande d'[extraction des cartes à débiter](Extraire_les_cg_a_debiter.md). Il est donc possible d'enchainer ces 2 étapes

On peut alors lancer la commande en "mode simulation" :  
`python .\debiterCartes.py --entree le_fichier_d_entrée --rapport le_fichier_rapport`

Cela va remplir le fichier rapport avec le même contenu que l'entrée, mais en ajoutant une colonne de commentaire.  
Celle-ci peut contenir :
 - simulation OK
 - carte introuvable
 - nom prénom ne correspondent pas (généralement à cause d'accent ou d'espaces)
 - pas assez sur la carte

Vous pouvez alors corriger le fichier et recommencer

Une fois que c'est bon, vous pouvez relancer le programme en lui ajoutant l'option `--execution` pour effectuer réellement les actions.

# Cas d'erreurs

Il arrive qu'un message "Veuillez fournir une valeur." apparaisse pour certaines lignes.  
N'ayant pas compris à quoi c'est du, je ne peux que conseiller de réessayer ...  
Avant cela, ne pas oublier de commenter les lignes déjà faite (en mettant un `#` en début de ligne) pour ne pas faire 2 fois une transaction.

Une option `--visible` permet d'afficher à l'écran le navigateur utilisé par le programme. Il semble que les cas d'erreur ne se produisent pas dans ce mode, mais c'est plus lent.
