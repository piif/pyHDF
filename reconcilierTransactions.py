import sys, os, getopt
from datetime import datetime
import mysql.connector

from myTools import info
from config import readConfig

def usage(message = None):
    if message is not None:
        info(message)
    info(f"""
Utilisation :
    {sys.argv[0]} --entree fichier_d_entree [ --rapport fichier_de_rapport ] [ --config fichier_de_config ] [ --execution ]

fichier_d_entree : fichier au format généré par extraireTransactions, donc colonnes séparées par des tabulations contenant n° transaction, n° carte, nom+prénom, date, montant
fichier_de_rapport : même format avec une colonne supplémentaire indiquant le résultat de l'opération
option --execution : effectue les modification en base (par défaut on ne fait qu'une simulation)
""")
    sys.exit(1)


def setResult(report, fields, result):
    resultLine = '\t'.join(fields + [ result ])
    info(result)
    print(resultLine, file=report)


def connexion(cfg):
    cnx = mysql.connector.connect(
        user=cfg['database']['user'], password=cfg['database']['password'],
        host=cfg['database']['server'], port=cfg['database']['port'],
        database=cfg['database']['base'], charset='utf8')
    query = cnx.cmd_query("select Nom from f_enfant limit 1")
    rows, diag = cnx.get_rows()
    if rows[0][0] is None:
        raise Exception("La base BAL est cryptée : démarrer le logiciel pour qu'elle soit en clair")
    return cnx

def addUpdate(update, field, current, expected, quote = True):
    if current == expected:
        return update
    if quote:
        return update + [ f"{field} = '{expected}'" ]
    else:
        return update + [ f"{field} = {expected}" ]

def convDate(d):
    if len(d) == 10: # avec des "/"
        return f"{d[6:10]}-{d[3:5]}-{d[0:2]} 00:00:00"
    else:
        return f"{d[4:8]}-{d[2:4]}-{d[0:2]} 00:00:00"

def reconcilier(cnx, testMode, trx, cg, nom_prenom, date, montant):
    info(f"recherche de {cg} pour {nom_prenom}")
    query = cnx.cmd_query(f"""
        select Id1 as Id, cast(concat(Nom, ' ', Prenom) as char) as NomPrenom
          from f_enfant e
         where e.CarteRegion = '{cg}'""")
    rows, diag = cnx.get_rows()
    if len(rows) == 0:
        return "CG introuvable dans BAL"
    if len(rows) > 1:
        return "Plusieurs réponses pour une même carte"

    (id, nom_prenom_bal) = rows[0]
    if nom_prenom_bal.lower() != nom_prenom.lower() :
        return f"le nom ne correspond pas : attendu {nom_prenom.lower()} / trouvé {nom_prenom_bal.lower()}"
    
    query = cnx.cmd_query(f"""
        select Id1, Intitule, Montant, Mode, Type, DateRegle, CodeCheque,
               DateModif, Provision, Detail, RecepisseCarte
        from b_reglement
        where CodeEnfant = {id}""")
    rows, diag = cnx.get_rows()
    found = []
    for row in rows:
        # info(row)
        (balId1, balIntitule, balMontant, balMode, balType, balDateRegle, balCodeCheque,
         balDateModif, balProvision, balDetail, balRecepisseCarte) = row
        if (
            balMontant == float(montant) and balType == 'Versement' and balMode == "Carte région"
        ) or (
            balProvision == float(montant) and balType == 'Provision'
        ):
            found += [ row ]
    if len(found) == 0:
        return "Pas de transaction correspondante trouvée dans BAL"
    if len(found) > 1:
        return "Plusieurs transactions correspondantes trouvées dans BAL"

    # info(f"Trouvé {found}")
    (balId1, balIntitule, balMontant, balMode, balType, balDateRegle, balCodeCheque,
         balDateModif, balProvision, balDetail, balRecepisseCarte) = found[0]

    update = []
    update = addUpdate(update, 'Intitule', balIntitule, f"Carte/Récépissé n° : {cg}/{trx}")
    update = addUpdate(update, 'Montant', balMontant, float(montant), False)
    update = addUpdate(update, 'Mode', balMode, "Carte région")
    update = addUpdate(update, 'Type', balType, "Versement")
    update = addUpdate(update, 'DateRegle', balDateRegle.isoformat(sep=' '), convDate(date))
    update = addUpdate(update, 'CodeCheque', balCodeCheque, cg)
    update = addUpdate(update, 'Provision', balProvision, 0.0, False)
    update = addUpdate(update, 'RecepisseCarte', balRecepisseCarte, trx)
    if len(update) != 0:
        update = addUpdate(update, 'DateModif', balDateModif, "now()", False)
    else:
        return "Déjà fait"

    if testMode:
        return ', '.join(update)

    query = f"""
        update b_reglement
           set {', '.join(update)}
         where Id1 = {balId1}"""
    # info(query)
    c = cnx.cursor()
    c.execute(query)
    if c.rowcount != 1:
        c.close()
        return f"erreur lors de l'update : rowcount = {c.rowcount}"
    c.close()

    return "Règlement mis à jour dans BAL"

def main(argv):
    testMode=True
    headless=True
    configPath = os.path.dirname(__file__) + "/config.yml"
    inputPath = None
    reportPath = None

    try:
        opts, args = getopt.getopt(argv, "c:i:o:r", [ "config=", "entree=", "rapport=", "execution" ])
    except getopt.GetoptError as err:
        info(err)
        usage()

    for o, a in opts:
        if o in ("-c", "--config"):
            configPath = a
        elif o in ("-i", "--entree"):
            inputPath = a
        elif o in ("-o", "--rapport"):
            reportPath = a
        elif o in ("-r", "--execution"):
            testMode = False
        else:
            usage("option {o} inattendue")

    if inputPath is None:
        usage("fichier d'entrée obligatoire")
    info(f"lecture des transaction à reporter dans BAL depuis le fichier {inputPath}")

    cfg=readConfig(configPath)


    if reportPath is None:
        report = sys.stdout
        info("Pas de destination pour le rapport, il sera affiché sur la console")
    else:
        report = open(reportPath, 'w', encoding=cfg['encoding'])
        info(f"Le rapport sera envoyé dans le fichier {reportPath}")

    cnx = connexion(cfg)

    input = open(inputPath, 'r', encoding=cfg['encoding'])

    count = 0
    for line in input.readlines():
        count += 1
        fields = line.strip('\n\r').split('\t')
        if line[0] == '#':
            setResult(report, fields, "ignoré")
            continue
        if len(fields) == 0:
            continue
        (trx, cg, nom_prenom, date, montant) = fields[0:5]

        result = reconcilier(cnx, testMode, trx, cg, nom_prenom, date, montant)
        setResult(report, fields, result)

        # if count == 3:
        #     break

    report.close()
    cnx.close()

if __name__ == "__main__":
    main(sys.argv[1:])