Ce programme `reconcilierTransactions.py` effectue des modifications dans la base de données de BAL. **Il est donc très important d'effectuer une sauvegarde juste avant son utilisation**, pour ne pas perdre de données en cas de souci.

Il est important de comprendre que ce programme n'est en rien maintenu ou garanti par les éditeurs du logiciel BAL, et qu'il peut donc très bien corrompre les données de BAL.

Le but de ce programme est de mettre à jour les règlements dans BAL en fonction des relevés du site HDF.  
En entrée, il utilise le fichier issu de l'[extraction des relevés](Extraire_les-releves.md)

Pour s'en servir, il faut avoir installé l'environnement Python et paramétré l'accès à mysql (voir [la doc d'installation](Installation.md))

De plus, comme la base est cryptée à l'arrêt du logiciel, il faut que BAL soit lancé avant d'effectuer cette requête.

On peut alors lancer une simulation par la commande suivante :  
`python .\reconcilierTransactions.py --entree fichier_de_transactions.csv --rapport fichier_rapport`

Le fichier rapport va alors contenir la même chose que le fichier d'entrée, avec une colonne commentaire en plus, pouvant contenir :
 - "Règlement mis à jour dans BAL" : transaction reportée correctement dans BAL (uniquement en mode "execution")
 - "Intitule = '...', Montant = ..., ..." : liste des modifications à effectuer dans BAL (uniquement en mode "simulation")
 - "déjà fait" : cette transaction est déjà reportée dans BAL
 - "CG introuvable dans BAL" : ce n° de carte n'est pas renseigné dans la fiche de l'élève
 - "Plusieurs réponses pour une même carte" : plusieurs élèves ont ce même n° de carte de renseigné
 - "le nom ne correspond pas : attendu ... / trouvé ..." : le nom de l'élève trouvé dans BAL ne correspond pas exactement à celui dans le relevé.
 - "Pas de transaction correspondante trouvée dans BAL" : dans les règlements de l'élève, il n'y a pas de provision ou de versement qui correspond à ce montant
 - "Plusieurs transactions correspondantes trouvées dans BAL" : dans les règlements de l'élève, il y a plusieurs provisions ou versements qui correspondent à ce montant

Après avoir corrigé les éventuelles erreurs (dans le relevé pour les noms, ou dans BAL pour les n° de carte et les réglements), vous pouvez relancer le programme avec l'option `--execution`.  
La base de données est alors mise à jour, et les modifications apparaissent dans BAL immédiatement.

Vérifiez bien que les changements semblent cohérents avant de faire une nouvelle sauvegarde.