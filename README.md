# CuriosityCollectionManager
Script for organizing a collection of wildlife observations (represented as strings) by taxonomic relationship

* Entries are parsed out of a json file (exported from the DayOne app)
* Entry text is searched for classifications (e.g. "F: Libellulidae" for Family: Libellulidae)
* Taxonomy (KPCOFGS) is fetched for each classification using the <a href="https://www.gbif.org/developer/summary">GBIF API</a> via the <a href="https://github.com/sckott/pygbif">pygbif</a> module
* List of entries is sorted by taxonomy
