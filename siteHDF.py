from playwright.sync_api import sync_playwright
from time import sleep
from myTools import info

class siteHDF:
    playwright = None
    page = None
    config = None

    def __init__(self, config, headless = True):
        self.config = config['hdf']
        info(f"Démarrage du navigateur ...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless = headless)
        self.page = self.browser.new_page()
        self.connectToSite()

    def close(self):
        self.playwright.stop()

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
            info("Accès à la page des débits")
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
            info("Accès à la page des transactions")
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
        
        nbTrx = self.page.get_by_text("Transaction(s) trouvée(s)").inner_text()
        info(nbTrx)    
        if nbTrx.startswith("0 "):
            info("Pas de transaction pour ces dates")
            return []

        # la recherche retourne une page avec une barre de pagination "<" "1" "2" ... "12" ">"
        # chacun de ces item a la classe .pagination_button
        # s'il y en a 2, (que < et >) c'est qu'il n'y a pas de résultats
        # sinon il faut regarder le contenu de l'avant dernier bouton pour savoir combien il
        # y a de page (ici 12) et en déduire combien de fois il faut cliquer sur le dernier
        # self.page.get_by_label(">")
        pagination = self.page.locator('.paginate_button')

        last = int(pagination.nth(pagination.count()-2).inner_text())
        info(f"Trouvé {last} pages de résultats")
        next = pagination.nth(pagination.count()-1)

        # TODO : passer par un itérateur plutôt que des concat de tableaux
        result = self._scanArray()
        for p in range(1, last):
            next.click()
            sleep(1)
            result += self._scanArray()

        return result

    def _scanArray(self):
        result = []
        lines = self.page.locator("table#tabTransaction>tbody>tr")
        info(f"trouvé {lines.count()} lignes")
        for line in lines.all():
            tds=line.locator("td").all_inner_texts()
            # 0: N° de transaction
            # 1: N° de carte
            # 2: Nom Prenom
            # 3: Date transaction
            # 4: Origine transaction
            # 5: Statut
            # 6: Date remboursement
            # 7: Montant
            # 8: Action
            if len(tds) == 0:
                info("tds vide ?")
                continue
            info(tds[0])
            result.append([ tds[0], tds[1], tds[2], tds[3], tds[7].strip(" €").replace(',', '.') ])
        return result