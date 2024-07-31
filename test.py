import os, sys, getopt, time
import playwright
import config

def info(message, **kwargs):
    kwargs["file"] = sys.stderr
    print(message, **kwargs)


def usage(message = None):
    if message is not None:
        info(message)
    info(f"""
Utilisation :
    {sys.argv[0]} -i fichier_d_entree [ -o fichier_de_rapport ] [ -c fichier_de_config ] [ -r ]
ou :
    {sys.argv[0]} --input fichier_d_entree [ --output fichier_de_rapport ] [ --config fichier_de_config ] [ --run ]

fichier_d_entree : fichier avec une ligne d'entête et des colonnes séparées par des tabulations : nom, prénom, n° carte, data naissance, montant
fichier_de_rapport : même format avec une colonne supplémentaire indiquant le résultat de l'opération
option -r ou --run : effectue les débits (par défaut on ne fait qu'une simulation)
""")
    sys.exit(1)


testMode=True
configPath = os.path.dirname(__file__) + "/config.yml"
inputPath = None
outputPath = None

try:
    opts, args = getopt.getopt(sys.argv[1:], "c:i:o:r", [ "config=", "input=", "output=", "run" ])
except getopt.GetoptError as err:
    print(err)
    usage()

for o, a in opts:
    if o in ("-i", "--input"):
        inputPath = a
    elif o in ("-o", "--output"):
        outputPath = a
    elif o in ("-c", "--config"):
        configPath = a
    elif o in ("-r", "--run"):
        testMode = False
    else:
        usage("option {o} inattendue")

if inputPath is None:
    usage("fichier d'entrée obligatoire")

cfg=config.readConfig(configPath)

# launch browser
browser = playwright.chromium.launch(headless=False)
# create a new incognito browser context.
context = browser.new_context()
# create a new page in a pristine context.
page = context.new_page()
page.goto(cfg['hdf']['url'])

time.sleep(10)

# gracefully close up everything
context.close()
browser.close()

with open(inputPath, 'r') as input:
    dummy = input.readline()
    for line in input.readlines():
        fields = line.strip('\n\r').split('\t')
        if len(fields) == 0:
            continue
        # info(f"line '{line}' -> {len(fields)} fields '{fields}'")
        (nom, prenom, num, naiss, montant) = fields
        info(f"TODO {nom},{prenom}")

