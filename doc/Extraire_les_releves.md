Le programme `extraireTransactions.py` a pour but de récupérer l'historique des paiements sur le site "génération HDF", entre 2 dates
Pour s'en servir, il faut avoir installé l'environnement Python et disposer d'un accès à l'espace partenaire (voir [la doc d'installation](Installation.md))

On peut alors lancer la commande :
`python .\extraireTransactions.py --debut date_de_debut --fin date_de_fin --rapport le_fichier_rapport`

On peut ne pas mettre de date de fin, la recherche va alors jusqu'ux dernières transactions en date.

Cela va remplir le fichier rapport avec les colonnes suivantes :
 - n° de transaction
 - n° de carte
 - nom prénom de l'élève
 - date de la transaction
 - montant (négatif quand il s'agit d'une annulation)

# Cas d'erreurs

Comme la recherche retourne une liste paginée, le programme doit faire "page suivante" jusqu'à la fin.
Il arrive qu'un changement de page ne soit pas pris en compte et on se retrouve alors avec 2 exemplaires de la même page.  
La seule solution consiste à recommencer, éventuellement en pluieurs fois avec des intervalles de dates plus courts.  
Une option `--visible` permet d'afficher à l'écran le navigateur utilisé par le programme. Il semble que les cas d'erreur se produisent moins dans ce mode, mais c'est plus lent.
