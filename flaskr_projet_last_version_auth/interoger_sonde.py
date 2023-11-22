from pysnmp.hlapi import *
import logging
from equiepement_class import Equipement  # Assurez-vous que le nom du fichier est correct

logger = logging.getLogger(__name__)

###########################################################################
##########################    Interoger SONDE  #############################
###########################################################################
def interroger_sonde(equipement):
    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(equipement.communaute_snmp),
                   UdpTransportTarget((equipement.adresse_ip, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(equipement.oid)),
                   timeout=10,  # Augmentez le timeout à 10 secondes ou plus
                   retries=1     # Nombre de réessais en cas d'échec
                   )
        )

        if errorIndication:
            logger.error(f"Erreur lors de l'interrogation de la sonde SNMP à {equipement.adresse_ip}: {errorIndication}")
            return None  # Retourne None en cas d'erreur
        elif errorStatus:
            logger.error(f"Réponse d'erreur de la sonde SNMP à {equipement.adresse_ip}: {errorStatus} à l'index {errorIndex}")
            return None  # Retourne None en cas d'erreur de statut
        else:
            for varBind in varBinds:
                logger.info(f"Réponse de la sonde SNMP à {equipement.adresse_ip}: {varBind.prettyPrint()}")
                # Extrait la valeur de la réponse SNMP
                _, value = varBind
                return value.prettyPrint()  # Retourne la valeur extraite
    except Exception as e:
        logger.error(f"Une erreur s'est produite lors de l'interrogation de la sonde: {e}")
        return None  # Retourne None en cas d'exception
