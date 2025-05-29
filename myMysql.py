import mysql.connector

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
