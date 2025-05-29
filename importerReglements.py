import sys, os, getopt
from datetime import datetime

from myTools import info
from config import readConfig
from myMysql import connexion, addUpdate

# ATTENTION ! à mettre à jour si on change la liste des colonnes à importer
NB_FIELDS = 11

def usage(message = None):
    if message is not None:
        info(message)
    info(f"""
Utilisation :
    {sys.argv[0]} --entree fichier_d_entree [ --rapport fichier_de_rapport ] [ --config fichier_de_config ] [ --execution ]

fichier_d_entree : fichier d'import de réglements avec {NB_FIELDS} colonnes (voir le détail dans la documentation)
fichier_de_rapport : même format avec une colonne supplémentaire indiquant le résultat de l'opération
option --execution : effectue les modification en base (par défaut on ne fait qu'une simulation)
""")
    sys.exit(1)


def setResult(report, fields, result):
    resultLine = '\t'.join(fields + [ result ])
    info(result)
    print(resultLine, file=report)

def chercherEleve(cnx, CodeBourse):
    query = cnx.cmd_query(f"""
        select Id1 as Id
          from f_enfant e
         where e.CodeBourse = '{CodeBourse}'""")
    rows, diag = cnx.get_rows()
    if len(rows) == 0:
        return None, f"Code bourse {CodeBourse} introuvable"
    if len(rows) > 1:
        return None, f"Plusieurs réponses pour le code bourse {CodeBourse}"
    id = rows[0][0]
    # info(f"{CodeBourse} -> {id}")
    return id, None


colonnesReglement = {
    'CodeEnfant'       : 'NULL',
    'Intitule'         : 'NULL',
    'Montant'          : 0.00, # montant si pas provision
    'Mode'             : 'NULL', # 'Autres',
    'Type'             : 'NULL', # 'Provision',
    'DateRegle'        : 'date(now())',
    'Signe'            : 'NULL',
    'FieldName'        : "'+'",
    'NumRemise'        : 'NULL',
    'RemiseDate'       : 'NULL',
    'RemiseDateImpose' : 'now()',
    'CodeCheque'       : 'NULL', # N° chèque ou CG
    'Tireur'           : 'NULL', # payeur,
    'Banque'           : 'NULL', # banque si chèque
    'NePasEncaisser'   : 0,
    'DateEnr'          : 'now()',
    'NomEnr'           : "'ADMIN'",
    'DateModif'        : 'now()',
    'NomModif'         : "'ADMIN'",
    'MontAdh'          : 0.00, # (montant si adh normalement, mais on compte tout dans MontBL.)
    'MontBL'           : 0.00, # montant si pas provision (que si loc/vente normalement)
    'MontCaution'      : 0.00, # inutilisé ??
    'IdRemise'         : 'NULL',
    'IdReglIntitule'   : 0,
    'IdParent'         : 0,
    'Rejet'            : 0,
    'RejetDate'        : 'NULL',
    'RejetMontant'     : 0.00,
    'RejetMontAdh'     : 0.00,
    'RejetMontBL'      : 0.00,
    'RejetMontCaution' : 0.00,
    'RejetNumRemise'   : 'NULL',
    'RejetIdRemise'    : 'NULL',
    'Provision'        : 'NULL', # montant si provision
    'Detail'           : 0,
    'Recepisse'        : 'NULL', # recu si espèces
    'RecepisseCarte'   : 'NULL', # n° trx si CG
    'Export_Compta'    : 0,
    'IdParent2'        : 0,
    'IdParent2Origine' : 0,
    'NOrdre'           : 'NULL',
    'Solde'            : 0
}


# convertir en chaine compatible SQL
def quote(s):
    return "'" + s.replace("'", "''") + "'"


def insererReglement(
        cnx, testMode, idEleve,
        Type, Mode, Intitule, Montant, Date, Payeur, Banque, Numero, Reference):
    reglement = colonnesReglement.copy()
    reglement['CodeEnfant'] = idEleve
    reglement['Intitule'] = quote(Intitule)
    reglement['Type'] = quote(Type)
    reglement['Mode'] = quote(Mode)
    reglement['DateEnr'] = quote(Date)
    reglement['Tireur'] = quote(Payeur)
    if Type == "Provision":
        reglement['Provision'] = Montant
    else:
        reglement['Montant'] = Montant
        reglement['MontBL'] = Montant
    if Mode == 'Espèces':
        reglement['Recepisse'] = quote(Numero)
    elif Mode == 'Chèque':
        reglement['CodeCheque'] = quote(Numero)
        reglement['Banque'] = quote(Banque)
    elif Mode == 'Carte région':
        reglement['CodeCheque'] = quote(Numero)
        reglement['RecepisseCarte'] = quote(Reference)

    requete = f"""INSERT INTO `b_reglement` (
        {', '.join(reglement.keys())}
    ) VALUES (
        {', '.join([ str(v) for v in reglement.values() ])}
    );"""

    if testMode:
        info(requete)
    else:
        c = cnx.cursor()
        c.execute(requete)
        if c.rowcount != 1:
            c.close()
            return f"erreur lors de l'insertion : rowcount = {c.rowcount}"
        c.close()

    return "insertion OK"

def modifierReglement(
        cnx, testMode, idEleve,
        Type, Mode, Intitule, Montant, Date, Payeur, Banque, Numero, Reference):
    return "TODO"

def main(argv):
    testMode=True
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
    info(f"lecture des réglements à reporter dans BAL depuis le fichier {inputPath}")

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
        # sauter l'entête , les lignes commençant par '#' et les lignes vides.
        if count == 1:
            continue
        fields = line.strip('\n\r').split('\t')
        if line[0] == '#':
            setResult(report, fields, "ignoré")
            continue
        if len(fields) == 0:
            continue

        (Action, CodeBourse, Type, Mode, Intitule, Montant, Date, Payeur, Banque, Numero, Reference) = fields[0:NB_FIELDS]

        if Action == "":
            continue

        idEleve, message = chercherEleve(cnx, CodeBourse)
        if idEleve is None:
            setResult(report, fields[0:NB_FIELDS], message)
            continue

        if Action == "Ajout":
            result = insererReglement(
                cnx, testMode, idEleve,
                Type, Mode, Intitule, Montant, Date, Payeur, Banque, Numero, Reference)
        elif Action == "Mise à jour":
            result = modifierReglement(
                cnx, testMode, idEleve,
                Type, Mode, Intitule, Montant, Date, Payeur, Banque, Numero, Reference)
        setResult(report, fields, result)

        # if count == 3:
        #     break

    report.close()
    cnx.close()

if __name__ == "__main__":
    main(sys.argv[1:])