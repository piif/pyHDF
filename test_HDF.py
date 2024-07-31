# module importé par pytest pour effectuer les traitements
# ce module permet de boucler sur une liste de cartes HDF pour effectuer des prélèvements dessus
# il attend dans la ligne de commande un nom de fichier listant les cartes, et éventuellement un fichier de rapport
# le rapport reprend les lignes du fichier d'entrée et y ajoute une colonne permettant de savoir si le prélèvement c'est bien passé

import os, sys, getopt, time, re
from playwright.sync_api import Page, expect

import config

def info(message, **kwargs):
    kwargs["file"] = sys.stderr
    print(message, **kwargs)

def usage(message = None):
    if message is not None:
        info(message)
    info(f"""
Utilisation :
    {sys.argv[0]} --entree fichier_d_entree [ --rapport fichier_de_rapport ] [ --config fichier_de_config ] [ --execution ]

fichier_d_entree : fichier avec une ligne d'entête et des colonnes séparées par des tabulations : nom, prénom, n° carte, data naissance, montant
fichier_de_rapport : même format avec une colonne supplémentaire indiquant le résultat de l'opération
option --execution : effectue les débits (par défaut on ne fait qu'une simulation)
""")
    assert False

def setResult(report, fields, result):
    resultLine = '\t'.join(fields + [ result ])
    info(result)
    print(resultLine, file=report)

def connectToSite(page, cfg):
    info(f"Accès au site {cfg['hdf']['url']} ...")
    page.goto(cfg['hdf']['url'])

    # se débarasser de la popup des cookies
    time.sleep(1)
    page.get_by_role("button", name="✗ Tout refuser").click()
    time.sleep(1)

    # se connecter
    info(f"Connexion ...")
    page.get_by_placeholder("Identifiant").fill(cfg['hdf']['user'])
    page.get_by_placeholder("Mot de passe").fill(cfg['hdf']['password'])
    page.get_by_role("button", name="Me connecter").click()
    info(f"Connexion OK")

def doTransaction(page, cfg, testMode, fields):

    # info(f"line '{line}' -> {len(fields)} fields '{fields}'")
    (nom, prenom, numero, naiss, montant) = fields[0:5]
    info(f"Recherche de {prenom} {nom}")

    # chercher la carte
    # saisie de la date de naissance pas à pas pour contourner le javascript du calendrier
    l = page.get_by_label("Date de naissance")
    l.fill('')
    l.click()
    page.keyboard.type(naiss.replace('/',''))

    n = page.get_by_label("Numéro")
    n.click()
    n.fill(numero)

    page.get_by_role("link", name="Rechercher").click()
    
    #time.sleep(2)
    # si introuvable, on zappe
    if page.get_by_text("Aucun résultat").count() != 0:
        return "carte non trouvée"

    # si le nom ne correspond pas, on zappe
    try:
        foundNom = page.get_by_label("Nom :", exact=True).input_value(timeout= 3000)
    except Exception as e: # todo : module name ?
        info(e)
        return "carte non trouvée"
    foundPrenom = page.get_by_label("Prénom :", exact=True).input_value()
    if foundNom.lower() != nom.lower() or foundPrenom.lower() != prenom.lower():
        return f"le nom ne correspond pas : attendu {nom.lower()},{prenom.lower()} / trouvé {foundNom.lower()},{foundPrenom.lower()}"

    page.get_by_label("Porte-monnaie :").select_option("Manuels et équipements - MANUEQUIP")
    page.get_by_role("link", name="Valider le PM").click()

    dispo = page.get_by_label("Solde disponible").input_value()
    dispo = float(dispo.strip(" €").replace(',', '.'))
    if dispo < float(montant):
        return f"Pas assez sur la carte : {dispo}"

    page.get_by_label("Montant à débiter").fill(montant)
    if testMode:
        return f"SIMULATION débit {montant} OK"
    else:
        page.get_by_role("button", name="Valider la transaction").click()
        e = page.locator('id=montantADebiter-error')
        if e.count() != 0:
            return e.text_content()

        page.get_by_role("button", name="Confirmer").click()
        page.get_by_role("link", name="Retour").click()
        return f"débit {montant} OK"


def test_HDF(page: Page):
    # info(f"from {__file__}, argv = {sys.argv}")

    testMode=True
    configPath = os.path.dirname(__file__) + "/config.yml"
    inputPath = None
    reportPath = None

    base = os.path.basename(__file__)
    lastArg = None
    for i, arg in enumerate(sys.argv):
        if arg.endswith(base):
            lastArg = i + 1
            break
    if lastArg is None:
        info("Can't find arglist beginning")
        assert False

    argv = sys.argv[lastArg:]
    # info(f"Argv starts at {lastArg} -> {argv}")
    try:
        opts, args = getopt.getopt(argv, "c:i:o:r", [ "config=", "entree=", "rapport=", "execution" ])
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
        else:
            usage("option {o} inattendue")

    if inputPath is None:
        usage("fichier d'entrée obligatoire")
    info(f"lecture des débits à effectuer depuis le fichier {inputPath}")

    if reportPath is None:
        report = sys.stdout
        info("Pas de destination pour le rapport, il sera affiché sur la console")
    else:
        report = open(reportPath, 'w', encoding='utf-8')
        info(f"Le rapport sera envoyé dans le fichier {reportPath}")

    cfg=config.readConfig(configPath)

    connectToSite(page, cfg)

    # se rendre sur la page des débits
    page.get_by_role("link", name="Faire une transaction").click()

    with open(inputPath, 'r', encoding='utf-8') as input:
        dummy = input.readline()
        for line in input.readlines():
            if line[0] == '#':
                continue
            fields = line.strip('\n\r').split('\t')
            if len(fields) == 0:
                continue

            result = doTransaction(page, cfg, testMode, fields)
            setResult(report, fields, result)

    report.close()
