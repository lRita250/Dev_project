import json

class Equipement:
    equipements_list = []  # Class variable to maintain a list of equipment instances

    def __init__(self, nom_equipement, adresse_ip, communaute_snmp, interface, oid):
        self.nom_equipement = nom_equipement
        self.adresse_ip = adresse_ip
        self.communaute_snmp = communaute_snmp
        self.interface = interface
        self.oid = oid
        Equipement.equipements_list.append(self)  # Add the instance to the list

    def to_dict(self):
        return {
            "nom_equipement": self.nom_equipement,
            "adresse_ip": self.adresse_ip,
            "communaute_snmp": self.communaute_snmp,
            "interface": self.interface,
            "oid": self.oid,
        }

    @classmethod
    def save_to_json(cls, file_path):
        equipment_data = [equipement.to_dict() for equipement in cls.equipements_list]
        with open(file_path, 'w') as json_file:
            json.dump(equipment_data, json_file, indent=4)

    @classmethod
    def load_from_json(cls, file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            cls.equipements_list = [cls(**equip_data) for equip_data in data]
    
    @classmethod
    def delete_equipment(cls, name):
        for equip in cls.equipements_list:
            if equip.nom_equipement == name:
                cls.equipements_list.remove(equip)

    @classmethod
    def get_equipment_by_name(cls, name):
        for equip in cls.equipements_list:
            if equip.nom_equipement == name:
                return equip
        return None
    
    def update_equipment(self, adresse_ip, communaute_snmp, interface, oid):
        self.adresse_ip = adresse_ip
        self.communaute_snmp = communaute_snmp
        self.interface = interface
        self.oid = oid
