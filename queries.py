MAPPING = """
PREFIX apf: <http://jena.hpl.hp.com/ARQ/property#>
PREFIX fx: <http://sparql.xyz/facade-x/ns/>
PREFIX premis: <http://www.loc.gov/premis/rdf/v3/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xyz: <http://sparql.xyz/facade-x/data/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

CONSTRUCT {
    ?ont_iri a skos:ConceptScheme ;
                  skos:prefLabel {pref_label_placeholder} .
                  #skos:hasTopConcept ?topconcept .
    ?concept a skos:Concept ;
             #rdfs:subClassOf premis:StorageMedium ;
             skos:prefLabel ?preflabel_nl ;
             skos:prefLabel ?preflabel_en ;
             skos:prefLabel ?preflabel_fr ;
             skos:altLabel ?altlabel_nl ;
             skos:altLabel ?altlabel_en ;
             skos:altLabel ?altlabel_fr ;
             skos:definition ?definition_nl ;
             skos:definition ?definition_en ;
             skos:definition ?definition_fr ;
             skos:broader ?broader ;
             skos:narrower ?narrower ;
             skos:related ?related ;
             skos:example ?example_en ;
             skos:example ?example_nl ;
             skos:example ?example_fr ;
             skos:example ?example ;
             skos:inScheme ?ont_iri ;
             #skos:topConceptOf ?topconcept_of ;
             skos:exactmatch ?exact_match ;
             skos:notation ?notation ;
             rdfs:seeAlso ?see_also ;
             skos:note ?note_nl ;
             skos:note ?note_fr ;
             skos:note ?note_en .
}
WHERE {
    SERVICE <x-sparql-anything:csv.headers=true>
    {
        fx:properties   fx:location       ?_file ;
                        fx:media-type "text/csv" ;
                        fx:csv.null-string          "" .

        ?c xyz:concept_benaming ?concept_temp .
        OPTIONAL { ?c  xyz:voorkeursbenaming_en ?preflabel_en_temp. }
        OPTIONAL { ?c  xyz:voorkeursbenaming_nl ?preflabel_nl_temp. }
        OPTIONAL { ?c  xyz:voorkeursbenaming_fr ?preflabel_fr_temp. }
        OPTIONAL { ?c  xyz:definitie_en ?definition_en_temp. }
        OPTIONAL { ?c  xyz:definitie_nl ?definition_nl_temp. }
        OPTIONAL { ?c  xyz:definitie_fr ?definition_fr_temp. }
        OPTIONAL {
            ?c xyz:alternatieve_benaming_en ?altlabel_en_temp .
        }
        OPTIONAL {
            ?c xyz:alternatieve_benaming_nl ?altlabel_nl_temp .
        }
        OPTIONAL {
            ?c xyz:alternatieve_benaming_fr ?altlabel_fr_temp .
        }
        OPTIONAL {
            ?c xyz:heeft_algemener_concept ?broader_temp .
        }
        OPTIONAL {
            ?c xyz:heeft_specifieker_concept ?narrower_temp .
        }
        OPTIONAL {
            ?c xyz:heeft_gerelateerd_concept ?related_temp .
        }
        OPTIONAL {
            ?c xyz:voorbeeld_en ?example_en_temp .
        }
        OPTIONAL {
            ?c xyz:voorbeeld_nl ?example_nl_temp .
        }
        OPTIONAL {
            ?c xyz:voorbeeld_fr ?example_fr_temp .
        }
        OPTIONAL {
            ?c xyz:voorbeeld ?example_temp .
        }
        # notatie	collectie	heeft_exacte_match	zie_ook
        OPTIONAL {
            ?c xyz:notatie ?notatie_temp .
        }
        OPTIONAL {
            ?c xyz:collectie ?collectie_temp .
        }
        OPTIONAL {
            ?c xyz:heeft_exacte_match ?heeft_exacte_match_temp .
        }
        OPTIONAL {
            ?c xyz:zie_ook ?zie_ook_temp .
        }
        OPTIONAL {
            ?c xyz:notitie_nl ?note_nl_temp .
        }
        OPTIONAL {
            ?c xyz:notitie_fr ?note_fr_temp .
        }
        OPTIONAL {
            ?c xyz:notitie_en ?note_en_temp .
        }
        
        BIND (IRI({ont_iri_placeholder}) AS ?ont_iri)
        BIND (IRI(CONCAT(str(?ont_iri), "/", ?concept_temp)) AS ?concept)
        
        BIND (STRLANG(?preflabel_en_temp, "en") AS ?preflabel_en)
        BIND (STRLANG(?preflabel_nl_temp, "nl") AS ?preflabel_nl)
        BIND (STRLANG(?preflabel_fr_temp, "fr") AS ?preflabel_fr)
        BIND (STRLANG(?definition_en_temp, "en") AS ?definition_en)
        BIND (STRLANG(?definition_nl_temp, "nl") AS ?definition_nl)
        BIND (STRLANG(?definition_fr_temp, "fr") AS ?definition_fr)
        BIND (STRLANG(?note_en_temp, "en") AS ?note_en)
        BIND (STRLANG(?note_nl_temp, "nl") AS ?note_nl)
        BIND (STRLANG(?note_fr_temp, "fr") AS ?note_fr)
        
        BIND (IF(!bound(?broader), ?concept, 1/0) AS ?topconcept)
        BIND (IF(!bound(?broader), ?ont_iri, 1/0) AS ?topconcept_of)
    }
    OPTIONAL{
        ?member_altlabel_en_temp apf:strSplit    (?altlabel_en_temp ";") .
    }
    OPTIONAL{
        ?member_altlabel_nl_temp apf:strSplit    (?altlabel_nl_temp ";") .
    }
    OPTIONAL{
        ?member_altlabel_fr_temp apf:strSplit    (?altlabel_fr_temp ";") .
    }
    OPTIONAL{
        ?member_broader_temp apf:strSplit    (?broader_temp ";") .
    }
    OPTIONAL{
        ?member_narrower_temp apf:strSplit    (?narrower_temp ";") .
    }
    OPTIONAL{
        ?member_related_temp apf:strSplit    (?related_temp ";") .
    }
    OPTIONAL{
        ?member_example_en_temp apf:strSplit    (?example_en_temp ";") .
    }
    OPTIONAL{
        ?member_example_nl_temp apf:strSplit    (?example_nl_temp ";") .
    }
    OPTIONAL{
        ?member_example_fr_temp apf:strSplit    (?example_fr_temp ";") .
    }
    OPTIONAL{
        ?example apf:strSplit    (?example_temp ";") .
    }
    OPTIONAL{
        ?member_notatie_temp apf:strSplit    (?notatie_temp ";") .
    }
    OPTIONAL{
        ?member_heeft_exacte_match_temp apf:strSplit    (?heeft_exacte_match_temp ";") .
    }
    OPTIONAL{
        ?member_zie_ook_temp apf:strSplit    (?zie_ook_temp ";") .
    }
    
    BIND (STRLANG(?member_altlabel_en_temp, "en") AS ?altlabel_en)
    BIND (STRLANG(?member_altlabel_nl_temp, "nl") AS ?altlabel_nl)
    BIND (STRLANG(?member_altlabel_fr_temp, "fr") AS ?altlabel_fr)
    BIND (IRI(CONCAT(str(?ont_iri), "/", ?member_broader_temp)) AS ?broader)
    BIND (IRI(CONCAT(str(?ont_iri), "/", ?member_narrower_temp)) AS ?narrower)
    BIND (IRI(CONCAT(str(?ont_iri), "/", ?member_related_temp)) AS ?related)
    BIND (STRLANG(?member_example_en_temp, "en") AS ?example_en)
    BIND (STRLANG(?member_example_nl_temp, "nl") AS ?example_nl)
    BIND (STRLANG(?member_example_fr_temp, "fr") AS ?example_fr)

    BIND (STRDT(?member_notatie_temp, xsd:string) AS ?notation)
    BIND (IRI(?member_heeft_exacte_match_temp) AS ?exact_match)
    BIND (IRI(?member_zie_ook_temp) AS ?see_also)

    #BIND (IRI(CONCAT(str(?ont_iri), "/", ?collectie_temp)) AS ?collection)
}
"""
