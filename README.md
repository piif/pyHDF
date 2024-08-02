# pyHDF

Outils pour batcher les opérations sur le site partenaires de la carte HDF

## Intro

Ce projet s'inscrit dans le cadre de la gestion d'une bourse aux livres pour une association de parents d'élèves dans un lycée des Hauts de France.

Dans cette région, la "carte génération HDF" (souvent abbréviée CG) est un moyen de paiement oferts aux élèves et provisionné avec 110€ à la rentrée de seconde puis avec 55€ par années suivantes.

Les associations de parents d'élèves qui se déclarent partenaires peuvent débiter cette carte pour payer le prêt de livres et l'achat groupé de fournitures.

Par ailleurs, si cette association est affiliée à la FCPE, elle peut disposer du logiciel "BAL" édité par la FCPE France. Celui-ci permet de centraliser les stocks, les incriptions et les règlements.
On peut aussi y gérer les informations relatives aux cartes HDF.

## /!\ AVERTISSEMENT /!\

Ces programmes et procédures sont fournis "tel quel", sans aucune garantie, et ne sont aucunement soutenu ou validé par les éditeurs du logiciel BAL.

Tout peut donc se mettre à ne plus marcher, notamment après une mise à jour du logiciel, ou ne pas être adapté à certaines combinaisons d'options.

Avant toute opération de réconciliation des données, il faut absolument effectuer une sauvegarde du logiciel BAL, puis vérifier ensuite que les données sont cohérentes

Par ailleurs, lorsquee le logiciel BAL s'arrête, il crypte une partie des données (surement pour des raisons de conformité RGPD).  
Il faut donc que le logiciel soit actif lorsqu'on lance des programmes qui dialoguent avec la base de données.

## But

Le but de ce projet est de faciliter 4 opérations :
 - [Exporter la liste des cartes à débiter](doc/Extraire_les_cg_a_debiter.md), en consultant la base de données adossée au logiciel BAL;
 - [Effectuer les débits CG en masse](doc/Debiter_les_CG.md);
 - [Extraire les relevés de paiement depuis le site](doc/Extraire_les_releves.md) (les relevés hebdomadaire ne contenant pas les n° de transaction, il est intéressant de les exporter à partir de lapage de recherche);
 - [Réconcilier les relevés](doc/Reconcilier_les_releves.md) fournis par le site partenaire avec les données dans la base BAL, c'est à dire transformer les provisions en paiements effectifs avec leur date et leur n° de transaction.

Les quatre actions sont disjointes et vous pouvez n'utiliser que les parties "débit en masse" et "extraction des relevés" sans avoir le logiciel BAL.

Consultez la [doc d'installation](doc/Installation.md) pour savoir ce qu'il faut installer selon vos besoins.

## Détails techniques

Comme la région HdF ne fournit pas d'API documentée pour effectuer ces opérations, l'idée est de "piloter" un navigateur web afin de faire comme si on effectuait les débits et les exports manuellement, mais via un programme qui va le faire plus vite et avec moins de risque d'erreurs.

Pour cela, le projet utilise le langage python (parce que largement répandu, il sera donc plus facile de passer la main aux futurs membres de l'association) et l'outil playwright qui intègre de quoi simuler des opérations sur un navigateur.

Par ailleurs, la partie réconciliation a besoin d'écrire directement dans la base de données du logiciel BAL.  
Pour cela, il est nécessaire de créer un utilisateur mysql, en suivant la procédure indiquée dans  [Creer un utilisateur mysql](doc/Creer_un_utilisateur_mysql.md).
