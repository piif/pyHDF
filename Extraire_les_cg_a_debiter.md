## Intro

Dans le logiciel BAL, on peut gérer les cartes génération.
Il faut renseigner pour cela :
 - le n° de carte dans la zone "carte région" de la page "identification"
 - la date de naissance de l'élève dans sa fiche foyer

On peut ensuite saisir les règlement de 2 façons :
 - créer une provision, de type "autres" ou de type "chèque" avec le montant qui sera à débiter
 - créer tout de suite un versement de type "carte région"

On a ensuite besoin de lister toutes les cartes génération à débiter, en filtrant éventuellement sur ceux qu'on a déjà livré.

Il faut donc :
 - lister toutes les provisions et tous les versements sans n° de transaction
 - filtrer sur ceux dont les livres sont distribués
 - sortir nom, prénom, n° de carte, date de naissance, montant à débiter (et classe éventuellement)

## Requête

Dans la base de données de BAL, on peut extraire ces informations à partir de la requête sql suivante :
```
select e.Nom as nom, e.Prenom as prenom,
       e.CarteRegion as carte,
       cast(concat(substring(e.Date_Nai, 9, 2), '/', substring(e.Date_Nai, 6, 2), '/', substring(e.Date_Nai, 1, 4)) as char) as naissance,
       r.Montant+r.Provision as montant,
       cast(concat(c.Libelle, ' ', s.Libelle) as char) as classe
--  into outfile 'c:\\users\\fcpe\\cg_a_faire.tsv'
  from b_reglement r, f_enfant e, p_clsec c, p_clsec s
 where r.CodeEnfant = e.Id1
   and c.id1 = e.CodeClasse
   and s.id1 = e.CodeSection
   and e.CarteRegion != ''
   and e.NbLivresLivraison > 0
   and (select count(*)
          from b_mouvement m
         where m.CodeEnfant = e.Id1
           and EtatLivraison = 'L'
       ) <= 1
   and ( r.Type = 'Provision'
    or   ( r.Mode = 'Carte région' and r.RecepisseCarte is null)
       )
-- limit 30
 ;
```

Si on décommente la partie "into" (chemin du fichier à adapter à votre ordinateur) on obtient un fichier qui peut être utilisé en entrée du programme `debiterCartes`.

Si on commente la partie `and NbLivresLivraison...` et `and (select ...) <= 1`, on sort tous les débits, y compris pour les élèves à qui on n'a pas encore livré les livres

## Remarque

Pour pouvoir effectuer cette requête il faut s'être créé un utilisateur avec suffisamment de droits, puisque l'utilisateur mysql utilisé par le logiciel BAL à un mot de passe tenu secret.  
Pour cela, on peut passer par la procédure indiquée dans [Creer un utilisateur mysql](Creer_un_utilisateur_mysql.md).