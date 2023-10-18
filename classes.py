class Equipement:
    def __init__(self, nom_equipement, adresse_ip, communaute_snmp):
        self.nom_equipement = nom_equipement
        self.adresse_ip = adresse_ip
        self.communaute_snmp = communaute_snmp
        self.sondes = []  # une liste pour stocker les sondes associées à cet équipement

class Sonde:
    def __init__(self, name, oid):
        self.name = name
        self.oid = oid

