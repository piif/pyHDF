Ce programme `importerReglements.py` effectue des modifications dans la base de données de BAL. **Il est donc très important d'effectuer une sauvegarde juste avant son utilisation**, pour ne pas perdre de données en cas de souci.

Il est important de comprendre que ce programme n'est en rien maintenu ou garanti par les éditeurs du logiciel BAL, et qu'il peut donc très bien corrompre les données de BAL.

Le but de ce programme est d'ajouter des règlements dans BAL à partire d'une liste fournie dans un fichier de type Excel ou Google Sheet.  
En entrée, il utilise un fichier contenant des données séparées par des tabulations, ce qu'on peut obtenir facilement depuis un Google Sheet en utilisant le menu Fichier → Télécharger → "Valeurs séparées par des tabulation (.tsv)".

Le fichier doit contenir les 11 colonnes suivantes :
 - `Action` : elle peut être vide ou commencer par `#` pour ignorer la ligne.  
   Sinon, elle doit valoir "Ajout" pour insérer un nouveal paiement, ou "Mise à jour" pour modifier un existant.  
   Cette dernière option n'est pas encore implémentée.
 - `CodeBourse` : il s'agit du "Code bourse aux livres de l'enfant" qu'on peut voir dans le panneau "identification", sous le bloc "solde".
 - `Type` : le type de transction; peut valoir `Versement`, `Remboursement` ou `Provision`.
 - `Mode` : le mode de réglement; peut valoir `Carte bancaire`, `Carte région`, `Chèque`, `Espèces`, `Virements` ou `Autres`.  
    Dans le cas d'une `provision`, le mode doit être `Autres`
 - `Intitule` : le libellé de ce réglement.
 - `Montant` : la montant, en euro, avec un `.` comme séparateur des centimes
 - `Date` : la date de la transaction, au format `AAAA/MM/JJ hh:mm:ss`.
 - `Payeur` : le nom du tireur du chèque, ou de propriétaire de la carte bancaire ou de la carte génération
 - `Banque` : le nom de la banque, dans le cas d'un chèque. Il faut que le nom corresponde exactement à un des noms pré enregistrés dans la liste des banque de BAL (voir l'onglet "Listes", bouton "Banques")
 - `Numero` : le numéro de reçu pour les espèce, le n° de chèque ou celui de la carte région.
 - `Reference` : le n° de transaction dans le cas d'une carte région.

De plus, on accepte une colonne "commentaire" en dernier, afin de pouvoir reprendre le résultat d'un premier import après avoir corrigé des erreurs.

Pour s'en servir, il faut avoir installé l'environnement Python et paramétré l'accès à mysql (voir [la doc d'installation](Installation.md))

De plus, comme la base est cryptée à l'arrêt du logiciel, il faut que BAL soit lancé avant d'effectuer cette requête.

On peut alors lancer une simulation par la commande suivante :  
`python .\importerReglements.py --entree fichier_de_reglements.tsv --rapport fichier_rapport`

Le fichier rapport va alors contenir la même chose que le fichier d'entrée, avec une colonne commentaire en plus, pouvant contenir :
 - "insertion OK" : le règlement est inséré dans BAL (uniquement en mode "execution")
 - "erreur lors de l'insertion" : une erreur a eu lieu au moment de l'insertion
 - "Code bourse ... introuvable" : le code demandé n'existe pas dans BAL
 - "Plusieurs réponses pour le code bourse ..." : plusieurs élève sont affectés au même code

Ce fichier peut être modifié et repris comme entrée du programme.

Après avoir corrigé les éventuelles erreurs, vous pouvez relancer le programme avec l'option `--execution`.  
La base de données est alors mise à jour, et les modifications apparaissent dans BAL immédiatement.

**Attention** : aucun contrôle de doublons n'est fait, donc si vous lancez le programme 2 fois avec les mêmes données, vous aurez des paiements en double exemplaire.  
Donc si après un premier import vous modifiez le fichier de rapport pour corriger des erreurs, n'oubliez pas d'enlever les lignes déjà insérées (celle avec un commentaire "insertion OK") ou de supprimer le "Ajout" de la première colonne.

Vérifiez bien que les changements semblent cohérents avant de faire une nouvelle sauvegarde.