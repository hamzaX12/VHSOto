from fastapi import FastAPI, Request,Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
import re

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load templates
templates = Jinja2Templates(directory="templates")

# Load RDF data
g = Graph()
g.parse("vh2.rdf", format="xml")

# Namespace
ns = {
    "ontolosafi": "http://www.semanticweb.org/mine/ontologies/2025/4/ontolosafi#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#"
}

def get_property(resource, prop):
    prop_uri = URIRef(ns["ontolosafi"] + prop)
    return g.value(subject=resource, predicate=prop_uri)

def get_heritage_sites():
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ontolosafi: <http://www.semanticweb.org/mine/ontologies/2025/4/ontolosafi#>

    SELECT ?site (SAMPLE(?description) AS ?desc) (SAMPLE(?location) AS ?loc)
                 (SAMPLE(?coordinates) AS ?coord) (SAMPLE(?image) AS ?img)
                 (SAMPLE(?typeAlt) AS ?type)
    WHERE {
        ?site rdf:type ontolosafi:SitePatrimonial .
        OPTIONAL { ?site ontolosafi:aPourDescription ?description . }
        OPTIONAL { ?site ontolosafi:aPourLocalisation ?location . }
        OPTIONAL { ?site ontolosafi:aPourCoordonnées ?coordinates . }
        OPTIONAL { ?site ontolosafi:imageURL ?image . }
        OPTIONAL {
            ?site rdf:type ?typeAlt .
            FILTER(?typeAlt != ontolosafi:SitePatrimonial)
        }
    }
    GROUP BY ?site
    """

    results = g.query(query)

    sites = []
    for row in results:
        iri = str(row.site)
        name = iri.split("#")[-1].replace("_", " ")
        description = str(row.desc) if row.desc else ""
        location = str(row.loc) if row.loc else ""
        if location.startswith("http://"):
            location = location.split("#")[-1].replace("_", " ")
        coordinates = str(row.coord) if row.coord else ""
        image = str(row.img) if row.img else ""
        site_type = str(row.type).split("#")[-1].replace("_", " ") if row.type else "Site Patrimonial"

        sites.append({
            "name": name,
            "description": description,
            "location": location,
            "coordinates": coordinates,
            "image": image,
            "type": site_type
        })

    return sites

def get_events():
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ontolosafi: <http://www.semanticweb.org/mine/ontologies/2025/4/ontolosafi#>

    SELECT ?event (SAMPLE(?date) AS ?d) (SAMPLE(?description) AS ?desc)
                  (SAMPLE(?organizer) AS ?org) (SAMPLE(?location) AS ?loc)
                  (SAMPLE(?coordinates) AS ?coord)
    WHERE {
        ?event rdf:type ontolosafi:ÉvénementCulturel .
        OPTIONAL { ?event ontolosafi:aPourDate ?date . }
        OPTIONAL { ?event ontolosafi:aPourDescription ?description . }
        OPTIONAL { ?event ontolosafi:organiséPar ?organizer . }
        OPTIONAL { ?event ontolosafi:aPourLocalisation ?location . }
        OPTIONAL { ?event ontolosafi:aPourCoordonnées ?coordinates . }
    }
    GROUP BY ?event
    """

    results = g.query(query)

    events = []
    for row in results:
        iri = str(row.event)
        name = iri.split("#")[-1].replace("_", " ")
        date = str(row.d) if row.d else ""
        description = str(row.desc) if row.desc else ""
        organizer = str(row.org) if row.org else ""
        location = str(row.loc) if row.loc else ""
        if location.startswith("http://"):
            location = location.split("#")[-1].replace("_", " ")
        coordinates = str(row.coord) if row.coord else ""

        events.append({
            "name": name,
            "date": date,
            "description": description,
            "organizer": organizer,
            "location": location,
            "coordinates": coordinates
        })

    return events


def get_handicrafts():
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ontolosafi: <http://www.semanticweb.org/mine/ontologies/2025/4/ontolosafi#>

    SELECT ?entity (SAMPLE(?typeVal) AS ?type) (SAMPLE(?description) AS ?desc) 
                   (SAMPLE(?image) AS ?img) (SAMPLE(?coordinates) AS ?coord)
                   (SAMPLE(?profession) AS ?prof) (SAMPLE(?specialty) AS ?spec) 
                   (SAMPLE(?workshop) AS ?work)
    WHERE {
        { 
          ?entity rdf:type ontolosafi:Artisanat .
          BIND("craft" AS ?typeVal)
          OPTIONAL { ?entity ontolosafi:aPourDescription ?description . }
          OPTIONAL { ?entity ontolosafi:imageURL ?image . }
          OPTIONAL { ?entity ontolosafi:aPourCoordonnées ?coordinates . }
        }
        UNION
        {
          ?entity rdf:type ontolosafi:Artisan .
          BIND("artisan" AS ?typeVal)
          OPTIONAL { ?entity ontolosafi:aPourProfession ?profession . }
          OPTIONAL { ?entity ontolosafi:aPourSpécialité ?specialty . }
          OPTIONAL { ?entity ontolosafi:aPourAtelier ?workshop . }
          OPTIONAL { ?entity ontolosafi:aPourCoordonnées ?coordinates . }
        }
    }
    GROUP BY ?entity
    """

    results = g.query(query)

    crafts = []
    for row in results:
        iri = str(row.entity)
        name = iri.split("#")[-1].replace("_", " ")
        type_ = str(row.type) if row.type else ""

        craft = {
            "type": type_,
            "name": name,
            "coordinates": str(row.coord) if row.coord else ""
        }

        if type_ == "craft":
            craft["description"] = str(row.desc) if row.desc else ""
            craft["image"] = str(row.img) if row.img else ""
        elif type_ == "artisan":
            craft["profession"] = str(row.prof) if row.prof else ""
            craft["specialty"] = str(row.spec) if row.spec else ""
            craft["workshop"] = str(row.work) if row.work else ""

        crafts.append(craft)

    return crafts

def get_services():
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ontolosafi: <http://www.semanticweb.org/mine/ontologies/2025/4/ontolosafi#>

    SELECT ?entity (SAMPLE(?category) AS ?cat) (SAMPLE(?type) AS ?typ) (SAMPLE(?location) AS ?loc)
                   (SAMPLE(?description) AS ?desc) (SAMPLE(?image) AS ?img) (SAMPLE(?coord) AS ?coord)
                   (SAMPLE(?zone) AS ?zone) (SAMPLE(?langue) AS ?langue) (SAMPLE(?profession) AS ?profession)
    WHERE {
        {
            ?entity rdf:type ontolosafi:Hébergement .
            BIND("hébergement" AS ?category)
            OPTIONAL { ?entity ontolosafi:aPourType ?type . }
            OPTIONAL { ?entity ontolosafi:aPourDescription ?description . }
            OPTIONAL { ?entity ontolosafi:imageURL ?image . }
            OPTIONAL { ?entity ontolosafi:aPourCoordonnées ?coord . }
            OPTIONAL { ?entity ontolosafi:aPourLocalisation ?location . }
        }
        UNION {
            ?entity rdf:type ontolosafi:Restauration .
            BIND("restauration" AS ?category)
            OPTIONAL { ?entity ontolosafi:aPourType ?type . }
            OPTIONAL { ?entity ontolosafi:imageURL ?image . }
            OPTIONAL { ?entity ontolosafi:aPourCoordonnées ?coord . }
            OPTIONAL { ?entity ontolosafi:aPourLocalisation ?location . }
        }
        UNION {
            ?entity rdf:type ontolosafi:Transport .
            BIND("transport" AS ?category)
            OPTIONAL { ?entity ontolosafi:aPourType ?type . }
            OPTIONAL { ?entity ontolosafi:zoneDesservie ?zone . }
            OPTIONAL { ?entity ontolosafi:aPourCoordonnées ?coord . }
        }
        UNION {
            ?entity rdf:type ontolosafi:GuideTouristique .
            BIND("guide" AS ?category)
            OPTIONAL { ?entity ontolosafi:aPourProfession ?profession . }
            OPTIONAL { ?entity ontolosafi:parleLangue ?langue . }
            OPTIONAL { ?entity ontolosafi:zoneCouverte ?zone . }
            OPTIONAL { ?entity ontolosafi:aPourCoordonnées ?coord . }
        }
    }
    GROUP BY ?entity
    """

    results = g.query(query)

    services = []
    for row in results:
        iri = str(row.entity)
        name = iri.split("#")[-1].replace("_", " ")
        category = str(row.cat)
        service = {
            "category": category,
            "name": name,
            "type": str(row.typ) if row.typ else "",
            "location": str(row.loc).split("#")[-1].replace("_", " ") if row.loc and str(row.loc).startswith("http") else str(row.loc or ""),
            "description": str(row.desc) if row.desc else "",
            "image": str(row.img) if row.img else "",
            "coordinates": str(row.coord) if row.coord else "",
            "zone": str(row.zone) if row.zone else "",
            "languages": str(row.langue) if row.langue else "",
            "profession": str(row.profession) if row.profession else ""
        }

        services.append(service)

    return services

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "heritage_sites": get_heritage_sites(),
        "events": get_events(),
        "handicrafts": get_handicrafts(),
        "services": get_services()
    })

def extract_month_from_date(date_str):
    match = re.search(r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)", date_str, re.IGNORECASE)
    return match.group(0).lower() if match else None

@app.get("/filter-events")
async def filter_events(month: str = Query(..., description="Mois en français, minuscule")):
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ontolosafi: <http://www.semanticweb.org/mine/ontologies/2025/4/ontolosafi#>

    SELECT ?evenement ?date ?organisateur ?description
    WHERE {{
      ?evenement rdf:type ontolosafi:ÉvénementCulturel .
      OPTIONAL {{ ?evenement ontolosafi:aPourDate ?date . }}
      OPTIONAL {{ ?evenement ontolosafi:organiséPar ?organisateur . }}
      OPTIONAL {{ ?evenement ontolosafi:aPourDescription ?description . }}

      FILTER(CONTAINS(LCASE(STR(?date)), "{month}"))
    }}
    """

    results = g.query(query)

    filtered_events = []
    for row in results:
        iri = str(row.evenement)
        name = iri.split("#")[-1].replace("_", " ")
        filtered_events.append({
            "name": name,
            "date": str(row.date) if row.date else "",
            "organizer": str(row.organisateur) if row.organisateur else "",
            "description": str(row.description) if row.description else ""
        })

    return JSONResponse(filtered_events)
