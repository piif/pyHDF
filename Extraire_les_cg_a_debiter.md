Dans la base de données de BAL, on peut extraire les informations des cartes génération à débiter à partir de la requête sql suivante :
```
select e.Nom as nom, e.Prenom as prenom,
       e.NbLivresLivraison, e.NbLivresALivrer,
       e.CarteRegion as carte,
       cast(concat(substring(e.Date_Nai, 9, 2), '/', substring(e.Date_Nai, 6, 2), '/', substring(e.Date_Nai, 1, 4)) as char) as naissance,
       r.Montant+r.Provision as montant,
       cast(concat(c.Libelle, ' ', s.Libelle) as char) as classe
--  into outfile 'c:\\users\\fcpeb\\cg_a_faire.tsv'
  from b_reglement r, f_enfant e, p_clsec c, p_clsec s
 where r.CodeEnfant = e.Id1
   and c.id1 = e.CodeClasse
   and s.id1 = e.CodeSection
   and e.CarteRegion != ''
   and e.NbLivresLivraison > 0 and (select count(*) from b_mouvement m where m.CodeEnfant = e.Id1 and EtatLivraison = 'L') <= 1 -- e.NbLivresALivrer <= 1
   and ( r.Type = 'Provision'
    or   ( r.Mode = 'Carte région' and r.RecepisseCarte is null)
       )
-- limit 30
 ;
```

Si on décommente la partie "into" on obtient un fichier qui peut être utilisé en entrée du programme `debiterCartes`

Pour pouvoir effectuer cette requête il faut s'être créé un utilisateur avec suffisamment de droits, puisque l'utilisateur mysql utilisé par le logiciel à un mot de passe tenu secret.  
Pour cela, on peut passer par la procédure indiquée dans [Creer_un_utilisateur_mysql](Creer_un_utilisateur_mysql.md).