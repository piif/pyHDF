from playwright.sync_api import sync_playwright, Playwright
from time import sleep
from myTools import info

class siteHDF:
    playwright = None
    page = None
    config = None

    def __init__(self, playwright, config, headless = True):
        self.config = config['hdf']
        info(f"Démarrage du navigateur ...")
        self.playwright = playwright
        browser = self.playwright.chromium.launch(headless = headless)
        self.page = browser.new_page()
        self.connectToSite()

    def connectToSite(self):
        info(f"Accès au site {self.config['url']} ...")
        self.page.goto(self.config['url'])

        # se débarasser de la popup des cookies
        sleep(1)
        self.page.get_by_role("button", name="✗ Tout refuser").click()
        # sleep(1)

        # se connecter
        info(f"Connexion ...")
        self.page.get_by_placeholder("Identifiant").fill(self.config['user'])
        self.page.get_by_placeholder("Mot de passe").fill(self.config['password'])
        self.page.get_by_role("button", name="Me connecter").click()
        info(f"Connexion OK")

    def doTransaction(self, testMode, nom, prenom, numero, naiss, montant):
        c = self.page.get_by_role("heading", name="Débiter une carte").count()
        if c == 0:
            info("Accès à la plage des débits")
            self.page.get_by_role("link", name="Transactions").click()
            self.page.get_by_role("link", name="Faire un débit").click()

        # info(f"{nom}, {prenom}, {numero}, {naiss}, {montant}")
        info(f"Recherche de {prenom} {nom}")

        # chercher la carte
        # saisie de la date de naissance pas à pas pour contourner le javascript du calendrier
        l = self.page.get_by_label("Date de naissance")
        l.fill('')
        l.click()
        self.page.keyboard.type(naiss.replace('/',''))

        n = self.page.get_by_label("Numéro")
        n.click()
        n.fill(numero)

        self.page.get_by_role("link", name="Rechercher").click()
        
        #sleep(2)
        # si introuvable, on zappe
        if self.page.get_by_text("Aucun résultat").count() != 0:
            return "carte non trouvée"

        # si le nom ne correspond pas, on zappe
        try:
            foundNom = self.page.get_by_label("Nom :", exact=True).input_value(timeout= 3000)
        except Exception as e:
            info(e)
            return "carte non trouvée"
        foundPrenom = self.page.get_by_label("Prénom :", exact=True).input_value()
        if foundNom.lower() != nom.lower() or foundPrenom.lower() != prenom.lower():
            return f"le nom ne correspond pas : attendu {nom.lower()},{prenom.lower()} / trouvé {foundNom.lower()},{foundPrenom.lower()}"

        self.page.get_by_label("Porte-monnaie :").select_option("Manuels et équipements - MANUEQUIP")
        self.page.get_by_role("link", name="Valider le PM").click()

        dispo = self.page.get_by_label("Solde disponible").input_value()
        dispo = float(dispo.strip(" €").replace(',', '.'))
        if dispo < float(montant):
            return f"Pas assez sur la carte : {dispo}"

        self.page.get_by_label("Montant à débiter").fill(montant)
        if testMode:
            return f"SIMULATION débit {montant} OK"
        else:
            self.page.get_by_role("button", name="Valider la transaction").click()
            e = self.page.locator('id=montantADebiter-error')
            if e.count() != 0:
                return e.text_content()

            self.page.get_by_role("button", name="Confirmer").click()
            self.page.get_by_role("link", name="Retour").click()
            return f"débit {montant} OK"

    def getTransactions(self, fromDate, toDate = None):
        c = self.page.get_by_role("heading", name="Rechercher par date de transaction :").count()
        if c == 0:
            info("Accès à la plage des transactions")
            self.page.get_by_role("link", name="Transactions").click()
            self.page.get_by_role("link", name="Historique").click()

        l = self.page.locator("#dateDebutRealisation")
        l.fill('')
        l.click()
        self.page.keyboard.type(fromDate.replace('/',''))

        l = self.page.locator("#dateFinRealisation")
        l.fill('')
        l.click()
        if toDate is not None:
            self.page.keyboard.type(toDate.replace('/',''))
        self.page.get_by_role("button", name="Rechercher").click()
        
        self.page.pause()

        result = []

        while True:
            result += self._scanArray()
            sleep(1)
            next = self.page.locator('a:has-text(">"):not(.disabled)')
            if next.count() == 0:
                break
            next.click()

        return result

    def _scanArray(self):
        result = []
        lines = self.page.locator("table#tabTransaction>tbody>tr")
        info(f"trouvé {lines.count()} lignes")
        for line in range(lines.count()):
            tds=lines.nth(line).locator("td")
            # N° de transaction
            # N° de carte
            # Nom Prenom
            # Date transaction
            # Origine transaction
            # Statut
            # Date remboursement
            # Montant
            # Action
            result.append([ tds.nth(i).inner_text() for i in (0, 1, 2, 3, 7) ])
        return result