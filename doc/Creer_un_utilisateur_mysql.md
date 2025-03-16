Le logiciel BAL utilise une base de données mysql, qu'il installe et paramètre lui même lors de l'installation du logiciel.

Il configure le service avec un utilisateur et un mot de passe qui ne sont pas accessibles.

Donc si on veut accéder directement à la base de données, il faut disposer d'un autre utilisateur, avec suffisamment de droits.

La [documentation de mysql](https://dev.mysql.com/doc/mysql-windows-excerpt/5.7/en/resetting-permissions-windows.html) propose une solution permettant de créer un utilisateur mysql lorsqu'on a accès au serveur.

Dans le cas du logiciel BAL, cette base est sur le poste de travail, dans le répertoire `C:\FCPE-Applications\MySql 5.1\`

On peut donc créer un fichier `C:\FCPE-Applications\mon-user.sql` contenant ceci (nom et mot de passe à adapter évidement) :
```
create user 'mon_user' identified by 'mon_mot_de_passe';
grant all privileges on *.* to 'mon_user'@'%' with grant option;
```

Il faut ensuite arrêter le service mysql (bien s'assurer que le logiciel BAL n'est pas actif auparavant) :
 - lancer le "gestionnaire de taches" avec l'entrée "exécuter en tant qu'administrateur"
 - sélectionner le dernier onglet ("services")
 - descendre jusqu'à la ligne "mysql"
 - clic-droit , "arrêter"

Depuis une console PowerShell, lancer la commande suivante :  
`&"C:\FCPE-Applications\MySql 5.1\bin\mysqld.exe" --init-file="C:\\FCPE-Applications\\mon-user.sql" --console`  
(il y a bien des simples `\` dans la première partie et des doubles dans la 2ème partie)

Depuis le gestionnaire de taches, relancer le service (clic droit, "démarrer")

Depuis la console, vous pouvez maintenant exécuter la commande suivante :  
`&"C:\FCPE-Applications\MySql 5.1\bin\mysql.exe -umon-user -p`  
La commande va vous demander un mot de passe et vous arrivez ensuite à un prompt où vous pouvez vérifier les accès comme dans cet exemple de dialogue :
```
PS C:\Users\fcpe> &"C:\FCPE-Applications\MySql 5.1\bin\mysql.exe" -umon-user -p
Enter password: ***************
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 698
Server version: 5.1.73-community MySQL Community Server (GPL)

Copyright (c) 2000, 2013, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| bl2                |
| bl2_ed             |
| bl2_init           |
| bl2_internet       |
| bl_norma           |
| mysql              |
| test               |
+--------------------+
8 rows in set (0.00 sec)

mysql> use bl2
Database changed
mysql> select count(*) from f_enfant;
+----------+
| count(*) |
+----------+
|     1192 |
+----------+
1 row in set (0.00 sec)

mysql> exit
Bye
PS C:\Users\fcpeb>
```

Pour plus de facilité, vous pouvez ensuite installer le logiciel [Mysql Workbench](https://www.mysql.com/products/workbench/) et créer un accès à la base locale. 
Vous pourrez alors exécuter des requêtes et voir les résultats de façon plus confortable.
