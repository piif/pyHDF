import sys, os, getopt

from myTools import info
from config import readConfig
from siteHDF import siteHDF

def usage(message = None):
    if message is not None:
        info(message)
    info(f"""
Utilisation :
    {sys.argv[0]} --visible --entree fichier_d_entree [ --rapport fichier_de_rapport ] [ --config fichier_de_config ] [ --execution ]

fichier_d_entree : fichier avec une ligne d'entête et des colonnes séparées par des tabulations : nom, prénom, n° carte, data naissance, montant
fichier_de_rapport : même format avec une colonne supplémentaire indiquant le résultat de l'opération
option --execution : effectue les débits (par défaut on ne fait qu'une simulation)
""")
    sys.exit(1)


def setResult(report, fields, result):
    resultLine = '\t'.join(fields + [ result ])
    info(result)
    print(resultLine, file=report)


def main(argv):
    testMode=True
    headless=True
    configPath = os.path.dirname(__file__) + "/config.yml"
    inputPath = None
    reportPath = None

    try:
        opts, args = getopt.getopt(argv, "c:i:o:rv", [ "config=", "entree=", "rapport=", "execution", "visible" ])
    except getopt.GetoptError as err:
        info(err)
        usage()

    for o, a in opts:
        if o in ("-i", "--entree"):
            inputPath = a
        elif o in ("-o", "--rapport"):
            reportPath = a
        elif o in ("-c", "--config"):
            configPath = a
        elif o in ("-r", "--execution"):
            testMode = False
        elif o in ("-v", "--visible"):
            headless = False
        else:
            usage("option {o} inattendue")

    if inputPath is None:
        usage("fichier d'entrée obligatoire")
    info(f"lecture des débits à effectuer depuis le fichier {inputPath}")

    cfg=readConfig(configPath)

    if reportPath is None:
        report = sys.stdout
        info("Pas de destination pour le rapport, il sera affiché sur la console")
    else:
        report = open(reportPath, 'w', encoding=cfg['encoding'])
        info(f"Le rapport sera envoyé dans le fichier {reportPath}")

    with open(inputPath, 'r', encoding=cfg['encoding']) as input:
        HDF = siteHDF(cfg, headless)

        dummy = input.readline()
        for line in input.readlines():
            fields = line.strip('\n\r').split('\t')
            if line[0] == '#':
                setResult(report, fields, "ignoré")
                continue
            if len(fields) == 0:
                continue
            (nom, prenom, numero, naiss, montant) = fields[0:5]

            result = HDF.doTransaction(testMode, nom, prenom, numero, naiss, montant)
            setResult(report, fields, result)

        report.close()

if __name__ == "__main__":
    main(sys.argv[1:])