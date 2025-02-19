# -*- coding: utf-8 -*- 

# external imports
import os
import csv
import re
from typing import Dict, List
from enum import Enum
from pymarc import Field, Indicators, Subfield

# -------------------- Property set-up --------------------
class Datasource_Term_Properties(Enum):
    ID = 0
    FRENCH = 1
    ENGLISH = 2

PROPERTIES_MAPPING = {
    Datasource_Term_Properties.ID:{"name":"_ID", "regexp":r"_ID$"},
    Datasource_Term_Properties.FRENCH:{"name":"_prefLabel@fr", "regexp":r"_prefLabel@fr$"},
    Datasource_Term_Properties.ENGLISH:{"name":"_prefLabel@en", "regexp":r"_prefLabel@en$"}
}

def get_property_name(prop:Datasource_Term_Properties) -> str:
    return PROPERTIES_MAPPING[prop]["name"]

def get_property_regexp(prop:Datasource_Term_Properties) -> str:
    return PROPERTIES_MAPPING[prop]["regexp"]

# -------------------- Classes --------------------

class Datasource_Term(object):
    def __init__(self, datasource:str):
        self.datasource = datasource
        self.id = None
        self.french = None
        self.english = None

    def load_all_properties(self, data:dict):
        for elem in Datasource_Term_Properties:
            self.def_proprety(elem, data[self.datasource + get_property_name(elem)])

    def def_proprety(self, prop:Datasource_Term_Properties, txt:str):
        """Adds a property and normalizes the """
        # Leave if prop is not defined
        if type(prop) != Datasource_Term_Properties:
            return
        txt = self.__normalize_input(txt)
        if prop == Datasource_Term_Properties.ID:
            self.id = txt
        elif prop == Datasource_Term_Properties.FRENCH:
            self.french = txt
        elif prop == Datasource_Term_Properties.ENGLISH:
            self.english = txt

    def __normalize_input(self, txt:str) -> str|None:
        if not txt:
            return None
        if str(txt).strip() == "":
            return None
        return str(txt).strip()

class Term(object):
    def __init__(self, data:dict):
        self.data = data
        # Get core data
        self.uri = self.data["URI"]
        self.ark_id = self.data["arkId"]
        self.fingerprint = self.data["fingerprint_prefLabel@fr"]
        # Identify all datasources
        self.datasources_names:List[str] = []
        self.datasources:Dict[str, Datasource_Term] = {}
        datasources = list(self.data.keys())
        datasources.remove("URI")
        datasources.remove("arkId")
        datasources.remove("fingerprint_prefLabel@fr")
        for col in datasources:
            col = re.sub(get_property_regexp(Datasource_Term_Properties.FRENCH), "",
                re.sub(get_property_regexp(Datasource_Term_Properties.ENGLISH), "",
                    re.sub(get_property_regexp(Datasource_Term_Properties.ID), "", col)
                ))
            if not col in self.datasources:
                self.datasources_names.append(col)
                self.datasources[col] = Datasource_Term(col)
        # Retrieve data for each data source
        for datasource in self.datasources_names:
            self.datasources[datasource].load_all_properties(self.data)
        # Define Archires Koha datasource name
        self.koha_archires_datasource_name = self.__get_archires_koha_datasource_name()

    def __get_archires_koha_datasource_name(self) -> str|None:
        if "Koha_Archires_Latest" in self.datasources_names:
            return "Koha_Archires_Latest"
        else:
            for name in self.datasources_names:
                if re.search(r"^Koha_Archires", name):
                    return name
        return None

    def get_archires_koha_term(self) -> Datasource_Term|None:
        """Returns the Datasource term for Koha Archires"""
        # There's a Koha value
        if self.koha_archires_datasource_name == None:
            return None
        return self.datasources[self.koha_archires_datasource_name]
    
    def get_datasource_term(self, datasource_name:str) -> Datasource_Term|None:
        """Returns the Datasource term for this datasource name"""
        if not datasource_name in self.datasources_names:
            return None
        return self.datasources[datasource_name]
    
    def get_term_as_archires_koha_UNM(self) -> Field|None:
        """Retrn a pymarc.Field object for this term"""
        if self.koha_archires_datasource_name == None:
            return None
        koha_term = self.get_archires_koha_term()
        subfields = [Subfield("a", koha_term.french)]
        if koha_term.english != None:
            subfields.append(Subfield("x", koha_term.english))
        subfields.append(Subfield("v", self.uri))
        subfields.append(Subfield("9", koha_term.id))
        return Field("610", indicators=Indicators(" ", " "), subfields=subfields)

class Archires_Thesaurus(object):
    def __init__(self, file_path:str):
        self.file_path = os.path.normpath(file_path)
        self.terms:Dict[str, Term] = {}
        self.ark_to_uri_index:Dict[str,str] = {}
        self.fingerprint_to_uri_index:Dict[str,str] = {}
        self.other_indexes:Dict[str, Dict[str: Dict[Datasource_Term_Properties, Dict[str, str]]]] = {}
        # ex : self.other_indexes{"Koha_Archires_Latest":{Datasource_Term_Properties.FRENCH:{"jardin chinois":"URI"}}}
        # Other indexes are not created by default, only when a search is needed

        # Get all terms
        with open(self.file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for line in reader:
                term = Term(line)
                self.terms[term.uri] = term
                self.ark_to_uri_index[term.ark_id] = term.uri
                self.fingerprint_to_uri_index[term.fingerprint] = term.uri

    def get_term_by_URI(self, uri:str) -> Term|None:
        """Returns the term for this URI (None if no match)"""
        if uri in list(self.terms.keys()):
            return self.terms[uri]
        return None

    def get_term_by_ARK_id(self, ark_id:str) -> Term|None:
        """Returns the term for this ark_id (None if no match)"""
        if ark_id in list(self.ark_to_uri_index.keys()):
            return self.terms[self.ark_to_uri_index[ark_id]]
        return None

    def get_term_by_fingerprint(self, fingerprint:str) -> Term|None:
        """Returns the term for this fingerprint (None if no match)"""
        if fingerprint in list(self.fingerprint_to_uri_index.keys()):
            return self.terms[self.fingerprint_to_uri_index[fingerprint]]
        return None

    def __build_other_index(self, datasource:str, prop:Datasource_Term_Properties):
        """Internal function used to build an index for this prop inside this datasource"""
        # Create the datasource if inexistent
        if not datasource in self.other_indexes:
            self.other_indexes[datasource] = {}
        # Leave if the index already exists
        if prop in self.other_indexes[datasource]:
            return
        else:
            self.other_indexes[datasource][prop] = {}
        # Iterate through each term
        for uri in self.terms:
            term = self.terms[uri]
            # Safety check
            if not datasource in term.datasources_names:
                pass
            # Get the index key
            key = None
            if prop == Datasource_Term_Properties.ID:
                key = term.datasources[datasource].id
            elif prop == Datasource_Term_Properties.FRENCH:
                key = term.datasources[datasource].french
            elif prop == Datasource_Term_Properties.ENGLISH:
                key = term.datasources[datasource].english
            # Safety check
            if key == None:
                pass
            self.other_indexes[datasource][prop][key] = term.uri

    def get_term_by_datasource_property(self, datasource:str, property:Datasource_Term_Properties, value:str) -> Term|None:
        """Returns the term for this value in htis property for this datasource (None if no match)"""
        self.__build_other_index(datasource, property)
        # Safety check 1
        if not datasource in self.other_indexes:
            return None
        # Safety check 2
        if not property in self.other_indexes[datasource]:
            return None
        # Safety check 3
        if not value in self.other_indexes[datasource][property].keys():
            return None
        # Safety check 4 is in next function
        return self.get_term_by_URI(self.other_indexes[datasource][property][value])
