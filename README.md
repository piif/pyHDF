# pyHDF

Outils pour batcher les opérations sur le site partenaires de la carte HDF

## Intro

Ce projet s'inscrit dans le cadre de la gestion d'une bourse aux livres pour une association de parents d'élèves dans un lycée des Hauts de France.

Dans cette région, la "carte génération HDF" (souvent abbréviée CG) est un moyen de paiement oferts aux élèves et provisionné avec 110€ à la rentrée de seconde puis avec 55€ par années suivantes.

Les associations de parents d'élèves qui se déclarent partenaires peuvent débiter cette carte pour payer le prêt de livres et l'achat groupé de fournitures.

Par ailleurs, si cette association est affiliée à la FCPE, elle peut disposer du logiciel "BAL" édité par le FCPE France. Celui-ci permet de centraliser les stocks, les incriptions et les réglements.
On peut donc y stocker les informations relatives aux cartes HDF.

## But

Le but de ce projet est de faciliter 3 opérations :
 - exporter la liste des cartes à débiter, en consultant la base de données adossée au logiciel BAL
 - effectuer les débits CG en masse
 - réconcilier les relevés furnis par le site partenaire avec les données dans la base BAL

Les trois actions sont disjointes et vous pouvez n'utilisr que la partie "débit en masse" sans avoir le logiciel BAL

## Détails techniques

Comme la région HdF ne fournit pas d'API documentée pour effectuer ces opérations, l'idée est de "piloter" un navigateur web afin de faire comme si on effectuait les débits et les exports manuellement, mais via un programme qui va le faire plus vite et avec moins de risque d'erreurs.

Pour cela, le projet utilise le langage python (parce que largement répandu, il sera donc plus facile de passer la main aux futurs membres de l'association) et l'outil playwright qui intègre de quoi simuler des opérations sur un navigateur
