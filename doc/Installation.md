# Intro

Pour utiliser les différents programmes de ce projet, il faut disposer de plusieurs choses.  
Tout n'est pas nécessaire selon les outils que vous voulez utiliser; voici la liste de ce qui est nécessaire à chacune des 4 tâches :
 - Extraire les CG à débiter : le logiciel BAL configuré en monoposte, un utilisateur mysql et
   un client mysql (Mysql Workbench idéalement, mais la ligne de commande intégrée avec BAL suffit)
 - Débiter les CG : python et playwright , un accès à l'espace partenaire "génération HDF"
 - Extraire les relevés : python et playwright , un accès à l'espace partenaire "génération HDF"
 - Reconcilier les relevés avec BAL : le logiciel BAL configuré en monoposte, python,
   un utilisateur mysql

# Le code

Téléchargez le code de ce projet, via le [lien pour obtenir un zip](https://github.com/piif/pyHDF/archive/refs/heads/main.zip).  
Dézippez le fichier dans un dossier où vous avez les droits (votre dossier "Documents" par exemple). 

Dans ce dossier, copiez le fichier `config.example.yml` dans un fichier `config.yml` et ouvrez ce dernier avec un éditeur de texte (le bloc note suffit).

Dans ce fichier, renseignez :
 - l'identifiant et le mot de passe de votre espace partenaire HDF, dans la section "HDF".
 - l'utilisateur mysql local

Attention à bien laisser alignées les entrées précédées de quelques espaces.

# BAL

Le logiciel BAL est édité par la [FCPE](https://www.fcpe.asso.fr/) et il est réservé aux associations qui lui sont affiliées.
Il faut entrer en contact avec eux pour l'installer.

Il doit être possible d'utiliser ces programmes de ce projet avec une version multiposte ou en réseau, mais cela n'a pas été testé.

# Python

Commencez par installer python pour windows, via [le site officiel](https://www.python.org/downloads/windows/).  
À l'heure où cette doc est écrite, on en est à la version 3.12.4, 64 bits

À partir d'une console (`cmd` ou Power shell), allez dans le dossier du code et lancez la commande suivante :
`pip install --requirement .\requirements.txt`

Les dépendances vont alors s'installer, notamment `playwright`

Enfin, configurez `playwright` via cette commande :  
`playwright install chromium`

# Utilisateur mysql

voir [Créer un utilisateur mysql](Creer_un_utilisateur_mysql.md)

# Client mysql

Il est plus confortable d'installer [Mysql Workbench](https://www.mysql.com/products/workbench/) mais on peut se contenter de la ligne de commande puisque BAL installe le serveur mysql et un client. 
Pour cela depuis Power Shell, utilisez la commande
`&"C:\FCPE-Applications\MySql 5.1\bin\mysql.exe" -umon-user -p`

# Accès à l'espace partenaire

Vous devez disposer d'un identifiant (n° à 4 hiffres ?) et un mot de passe sur [l'espace partenaire](https://partenaires.cartegeneration.hautsdefrance.fr)

Ces information doivent être ajoutées à la configuration du projet (voir la section "Le code")
