from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF

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
    sites = []
    site_class = URIRef(ns["ontolosafi"] + "SitePatrimonial")
    
    for site in g.subjects(predicate=RDF.type, object=site_class):
        name = site.split("#")[-1].replace("_", " ")
        description = str(get_property(site, "aPourDescription") or "")
        
        # Handle different location types
        location_obj = get_property(site, "aPourLocalisation")
        location = ""
        if isinstance(location_obj, Literal):
            location = str(location_obj)
        elif isinstance(location_obj, URIRef):
            location = location_obj.split("#")[-1].replace("_", " ")

        coordinates = str(get_property(site, "aPourCoordonnées") or "")
        image = str(get_property(site, "imageURL") or "")
        
        site_type = "Site Patrimonial"
        for type_ in g.objects(subject=site, predicate=RDF.type):
            if type_ != site_class and str(type_).startswith(ns["ontolosafi"]):
                site_type = type_.split("#")[-1].replace("_", " ")
                break
        
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
    events = []
    event_class = URIRef(ns["ontolosafi"] + "ÉvénementCulturel")
    
    for event in g.subjects(predicate=RDF.type, object=event_class):
        name = event.split("#")[-1].replace("_", " ")
        date = str(get_property(event, "aPourDate") or "")
        description = str(get_property(event, "aPourDescription") or "")
        organizer = str(get_property(event, "organiséPar") or "")

        location_obj = get_property(event, "aPourLocalisation")
        location = ""
        if isinstance(location_obj, Literal):
            location = str(location_obj)
        elif isinstance(location_obj, URIRef):
            location = location_obj.split("#")[-1].replace("_", " ")

        coordinates = str(get_property(event, "aPourCoordonnées") or "")
        
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
    crafts = []
    craft_class = URIRef(ns["ontolosafi"] + "Artisanat")
    artisan_class = URIRef(ns["ontolosafi"] + "Artisan")
    
    # Get craft types
    for craft in g.subjects(predicate=RDF.type, object=craft_class):
        craft_name = craft.split("#")[-1].replace("_", " ")
        description = str(get_property(craft, "aPourDescription") or "")
        image = str(get_property(craft, "imageURL") or "")
        coordinates = str(get_property(craft, "aPourCoordonnées") or "")
        
        crafts.append({
            "type": "craft",
            "name": craft_name,
            "description": description,
            "image": image,
            "coordinates": coordinates
        })
    
    # Get artisans
    for artisan in g.subjects(predicate=RDF.type, object=artisan_class):
        name = artisan.split("#")[-1].replace("_", " ")
        profession = str(get_property(artisan, "aPourProfession") or "")
        specialty = str(get_property(artisan, "aPourSpécialité") or "")
        workshop = str(get_property(artisan, "aPourAtelier") or "")
        coordinates = str(get_property(artisan, "aPourCoordonnées") or "")
        
        crafts.append({
            "type": "artisan",
            "name": name,
            "profession": profession,
            "specialty": specialty,
            "workshop": workshop,
            "coordinates": coordinates
        })
    
    return crafts

def get_services():
    services = []
    
    def extract_location(resource):
        location_obj = get_property(resource, "aPourLocalisation")
        if isinstance(location_obj, Literal):
            return str(location_obj)
        elif isinstance(location_obj, URIRef):
            return location_obj.split("#")[-1].replace("_", " ")
        return ""
    
    # Get accommodations
    accommodation_class = URIRef(ns["ontolosafi"] + "Hébergement")
    for acc in g.subjects(predicate=RDF.type, object=accommodation_class):
        name = acc.split("#")[-1].replace("_", " ")
        service_type = str(get_property(acc, "aPourType") or "Hébergement")
        location = extract_location(acc)
        description = str(get_property(acc, "aPourDescription") or "")
        image = str(get_property(acc, "imageURL") or "")
        coordinates = str(get_property(acc, "aPourCoordonnées") or "")
        
        services.append({
            "category": "hébergement",
            "name": name,
            "type": service_type,
            "location": location,
            "description": description,
            "image": image,
            "coordinates": coordinates
        })
    
    # Get restaurants
    restaurant_class = URIRef(ns["ontolosafi"] + "Restauration")
    for rest in g.subjects(predicate=RDF.type, object=restaurant_class):
        name = rest.split("#")[-1].replace("_", " ")
        service_type = str(get_property(rest, "aPourType") or "Restauration")
        location = extract_location(rest)
        image = str(get_property(rest, "imageURL") or "")
        coordinates = str(get_property(rest, "aPourCoordonnées") or "")
        
        services.append({
            "category": "restauration",
            "name": name,
            "type": service_type,
            "location": location,
            "image": image,
            "coordinates": coordinates
        })
    
    # Get transports
    transport_class = URIRef(ns["ontolosafi"] + "Transport")
    for trans in g.subjects(predicate=RDF.type, object=transport_class):
        name = trans.split("#")[-1].replace("_", " ")
        service_type = str(get_property(trans, "aPourType") or "Transport")
        zone = str(get_property(trans, "zoneDesservie") or "")
        coordinates = str(get_property(trans, "aPourCoordonnées") or "")
        
        services.append({
            "category": "transport",
            "name": name,
            "type": service_type,
            "zone": zone,
            "coordinates": coordinates
        })
    
    # Get guides
    guide_class = URIRef(ns["ontolosafi"] + "GuideTouristique")
    for guide in g.subjects(predicate=RDF.type, object=guide_class):
        name = guide.split("#")[-1].replace("_", " ")
        profession = str(get_property(guide, "aPourProfession") or "Guide Touristique")
        languages = str(get_property(guide, "parleLangue") or "")
        zone = str(get_property(guide, "zoneCouverte") or "")
        coordinates = str(get_property(guide, "aPourCoordonnées") or "")
        
        services.append({
            "category": "guide",
            "name": name,
            "profession": profession,
            "languages": languages,
            "zone": zone,
            "coordinates": coordinates
        })
    
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
