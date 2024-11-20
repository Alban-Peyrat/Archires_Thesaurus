# ArchiRès thesaurus

[![Active Development](https://img.shields.io/badge/Maintenance%20Level-Actively%20Developed-brightgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)

This repository uses **copy** of (usually) private repositories about the ArchiRès thesaurus.
Thus, some files might have an update delay.
If the explanation of a file does not states that it is based on another one, this repository is the source.

The thesaurus can be found on [IR* Huma-Num](https://www.huma-num.fr) instance of [Opentheso](https://github.com/miledrousset/Opentheso) : [direct link to ArchiRès thesaurus](https://opentheso.huma-num.fr/opentheso/?idt=th785).

## Repository content

* [Thesaurus changelog](#thesaurus-changelog)
* [ID mapping of different databases](#id-mapping-of-different-databases)
* [Deprecated ARK table](#deprecated-ark-table)
* [Python class to use the ID mapping](#python-class-to-use-the-id-mapping)

### Thesaurus changelog

The file [`thesaurus_CHANGLOG.md`](./thesaurus_CHANGELOG.md) contains the list of changes to the thesaurus (terms are referred to as their french preferred label).
History (should) be precise starting from november 2024, changes from 2024 should mostly be accurate.
Some changes before 2024 are also included.

*Note : this file is based on `Archires_Structure_Technique\Opentheso\CHANGELOG.md`*.

### ID mapping of different databases

The file [`mapping_known_DB.csv`](./mapping_known_DB.csv) contains a mapping of internal IDs from different databases with the ArchiRès thesaurus persistent identifiers.
To be considered part of the thesaurus, a term must be included in Opentheso.

#### File technical information

The file is a CSV delimited by `;`, here are the columns :

1. _URI_ : persistent ID
1. _arkId_ : ARK ID, only the NAAN + name part (ex : `99152/r5qql3d3-6`)
1. *fingerprint_prefLabel@fr* : Opentheso's french preferred labelled normalized using [GREL function `fingerprint()` in OpenRefine](https://openrefine.org/docs/manual/grelfunctions#fingerprints)
1. For each datasource, in the order defined below :
    1. *SourceName_ID* : internal ID
    1. *SourceName_prefLabel@fr* : french preferred labelled
    1. *SourceName_prefLabel@en* : english preferred labelled (empty if does not exist)

#### Supported datasource list

1. *Opentheso* : Opentheso export from  2024 june 26th
1. *Koha_Archires_Latest* : ArchiRès Koha latest export
1. *Koha_Archires_2024* : ArchiRès Koha export from 2024 july 11th
1. *Koha_Brise-es_2024* : BRISE-ES Koha export from 2024 july 11th (manual mapping is missing right now)
1. *Alexandrie_IPRAUS_2024* : IPRAUS Alexandrie export from 2024 november 14th

*Note : this file is based on `Archires_Structure_Technique\Opentheso\mapping_ids\mapping_thesaurus_archires_BDD_connues.csv`*.

### Deprecated ARK table

The file [`deprecated_ARK_table.csv`](./deprecated_ARK_table.csv) contains the list of deprecated published ARK.

Simple CSV (`;` delimited) file, with `old` & `current` column.
__Does not contain ARK published under the `fk` shoulder__ (though we have it private repositories if needed).

If a term was deleted (not depreciated) `current` will have the value `DELETED`
List of deleted terms :

* `https://n2t.net/ark:/99152/r5fd6pk6-n` (_test-rejeté_)

*Note : this file is based on `Archires_Structure_Technique\ARK\deprecated_tables\main.csv`*.

### Python class to use the ID mapping

The file [`cl_thes_archires.py`](./cl_thes_archires.py) provides a class to handle data inside the ID mapping (uses `pymarc` version 5.2.0, [`z_test_thes_archires.py`](./z_test_thes_archires.py) provides an example, the same as below).

#### Using the class

Call the class with the CSV file path as argument, then use methods :

* _Note : all of them return `None` if the term was not found_
* `get_term_by_URI()` to get a term using its URI as argument
* `get_term_by_ARK_id()` to get a term using its ARK ID (NAAN + name) as argument
* `get_term_by_fingerprint()` to get a term using its french preferred labelled normalized as argument
* `get_term_by_datasource_property()` to get a term using another property of the file, using as arguments :
  * `datasource` : one of the supported datasource name (see [list above](#supported-datasource-list))
  * `property` : `Datasource_Term_Properties` element (`ID`, `FRENCH` or `ENGLISH`)
  * `value` : the value used as a matching point

#### Working with returned terms

Terms are classes with the following properties :

* `uri` : URI of the term
* `ark_id` : ARK ID (NAAN + name) of the term
* `fingerprint` : french preferred labelled normalized of the term
* _Following propertie sare mostly for internal use_ :
  * `datasources_names` : list of datasource names found for this term
  * `datasources` : dict using the datasource name as key and a `Datasource_Term` instance as value
  * `koha_archires_datasource_name` : datasource name of ArchiRès Koha (either *Koha_Archires_Latest* or the first name starting with *Koha_Archires* if the former is not found)

The also include the following methods :

* _Note : all of them return `None` if the datasource was not found_
* `get_archires_koha_term()` : returns the `Datasource_Term` instance for ArchiRès Koha
* `get_datasource_term()` : returns the `Datasource_Term` for the datasource name provided as argument
* `get_term_as_archires_koha_UNM()` : returns a `pymarc.Field` of this field for ArchiRès Koha

`Datasource_Term` class contains the following properties :

* _Note : all of them are set to `None` if the data was incorrect or empty_
* `id` : internal ID of the term in this datasource
* `french` : preferred french label of the term in this datasource
* `english` : preferred english label of the term in this datasource

#### Example

``` Python
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

# ↓↓↓↓↓↓↓↓↓↓ Output ↓↓↓↓↓↓↓↓↓↓
# Koha ArchiRès 610 for Chinese garden : 610   $aJardin chinois$xChinese garden$0https://n2t.net/ark:/99152/r5n6md48-t$960402
# Opentheso ID 67717/T990-1154 : Jardin anglo-chinois (@en : Anglo-chinese garden)
# BRISE-ES : STRUCTURE SUSPENDUE (authid : 377252)
```