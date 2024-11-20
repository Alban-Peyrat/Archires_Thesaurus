# -*- coding: utf-8 -*- 
from cl_thes_archires import Archires_Thesaurus, Datasource_Term_Properties as Property
thesaurus = Archires_Thesaurus("mapping_known_DB.csv")

# Get chinese garden by URI keyword in UNIMARC for ArchiRès Koha
term = thesaurus.get_term_by_URI("https://n2t.net/ark:/99152/r5n6md48-t")
if term != None:
    unm = term.get_term_as_archires_koha_UNM()
    if unm != None:
        print(f"Koha ArchiRès 610 for Chinese garden : {unm.tag} {unm.indicator1}{unm.indicator2}{"".join(['$' + sub.code + sub.value for sub in unm.subfields])}")

# Get anglo chinese garden Opentheso data by ARK ID
term = thesaurus.get_term_by_ARK_id("99152/r5g2wl64-3")
if term != None:
    opentheso = term.get_datasource_term("Opentheso")
    if opentheso != None:
        print(f"Opentheso ID {opentheso.id} : {opentheso.french} (@en : {opentheso.english})")

# Get Suspended structure Koha BRISE-ES data by IPRAUS Alexandrie value
term = thesaurus.get_term_by_datasource_property("Alexandrie_IPRAUS_2024", Property.FRENCH, "Structure suspendue")
if term != None:
    brise_es_term = term.get_datasource_term("Koha_Brise-es_2024")
    if brise_es_term != None:
        print(f"BRISE-ES : {brise_es_term.french} (authid : {brise_es_term.id})")