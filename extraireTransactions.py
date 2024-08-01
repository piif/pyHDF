import sys, os, getopt

from myTools import info
from config import readConfig
from siteHDF import siteHDF

def usage(message = None):
    if message is not None:
        info(message)
    info(f"""
Utilisation :
    {sys.argv[0]} --visible --debut jjmmaaaa [ --fin jjmmaaaa ] [ --config fichier_de_config ] [ --rapport nom_fichier_de_sortie ]
    Génère un rapport de toutes les transactions entre les dates demandées
""")
    sys.exit(1)


def setResult(report, fields):
    resultLine = '\t'.join(fields)
    print(resultLine, file=report)


def main(argv):
    headless=True
    configPath = os.path.dirname(__file__) + "/config.yml"
    fromDate = None
    toDate = None
    reportPath = None

    try:
        opts, args = getopt.getopt(argv, "c:d:f:rv", [ "config=", "debut=", "fin=", "rapport=", "visible" ])
    except getopt.GetoptError as err:
        info(err)
        usage()

    for o, a in opts:
        if o in ("-d", "--debut"):
            fromDate = a
        elif o in ("-f", "--fin"):
            toDate = a
        elif o in ("-c", "--config"):
            configPath = a
        elif o in ("-r", "--rapport"):
            reportPath = a
        elif o in ("-v", "--visible"):
            headless = False
        else:
            usage("option {o} inattendue")

    if fromDate is None:
        usage("Date de début obligatoire")

    cfg=readConfig(configPath)

    if reportPath is None:
        report = sys.stdout
        info("Pas de destination pour le rapport, il sera affiché sur la console")
    else:
        report = open(reportPath, 'w', encoding=cfg['encoding'])
        info(f"Le rapport sera envoyé dans le fichier {reportPath}")

    HDF = siteHDF(cfg, headless)

    results = HDF.getTransactions(fromDate, toDate)
    for result in results:
        setResult(report, result)

    report.close()
    HDF.close()

if __name__ == "__main__":
    main(sys.argv[1:])