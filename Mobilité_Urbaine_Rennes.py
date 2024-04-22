# Importation
from urllib import request
import numpy as np
import json
from pandas import DataFrame
from bokeh.io import show
from bokeh.models import CustomJS, Button, Column, Row, TabPanel, Tabs, Div, HoverTool, ColumnDataSource, BoxZoomTool, PanTool, ResetTool, Select
from bokeh.plotting import figure
from bokeh.layouts import layout 
import pandas as pd
from bokeh.transform import dodge
from bokeh.palettes import Blues3
from datetime import datetime

############################### Fonctions
# Fonction pour convertir les coordonnées en Web Mercator
def coor_wgs84_to_web_mercator(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x, y)

# Fonction pour charger les données depuis l'URL
def load_data_from_url(url):
    with request.urlopen(url) as response:
        data = json.load(response)
    return data["results"]

# Fonction pour charger les données depuis un fichier JSON
def load_data_from_json_file(file_path):
    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)
    return data

# Fonction pour analyser les données des stations
def analyse_data_reparation_velo(data):
    # Initialisation des listes vides pour stocker les données
    lieu = []
    etat = []
    gonflage = []
    reparation = []
    coordsx = []  
    coordsy = [] 
    # Parcourt de chaque station 
    for station in data:
        etat.append(station["etat"])
        lieu.append(station["gml_id"])
        gonflage.append(station["gonflage"])
        reparation.append(station["reparation"])
        # Extrait des coordonnées de la station (latitude, longitude)
        lat, lon = station["geo_shape"]["geometry"]["coordinates"][0][1], station["geo_shape"]["geometry"]["coordinates"][0][0]
        # Convertit les coordonnées WGS 84 en coordonnées Web Mercator
        x, y = coor_wgs84_to_web_mercator(lon, lat)
        coordsx.append(x)
        coordsy.append(y)

    # Crée un DataFrame à partir des listes de données
    df = DataFrame({'Lieu': lieu, 'gonflage': gonflage, 'etat': etat, 'x': coordsx, 'y': coordsy, "reparation": reparation})
    return df

# Fonction pour analyser les données sur les stations velos
def analyse_station_velo(data):
    # Initialisation de plusieurs listes vides pour stocker les informations extraites de chaque station
    nom = [] # Stocke les noms des stations de vélos
    total_possible = [] # Stocke le nombre total d'emplacements dans chaque station
    nbre_emplacement_vide =[] # Stocke le nombre d'emplacements vides dans chaque station
    nbre_de_velo_disponible= [] # Stocke le nombre de vélos disponibles dans chaque station
    coordsx = []
    coordsy = []
    # Parcourt de chaque station vélo
    for station in data:
        nom.append(station["nom"])
        total_possible.append(station["nombreemplacementsactuels"])
        nbre_emplacement_vide.append(station["nombreemplacementsdisponibles"])
        nbre_de_velo_disponible.append(station["nombrevelosdisponibles"])
        # Extrait les coordonnées (latitude, longitude) de la station
        lat, lon =station["coordonnees"]['lat'], station["coordonnees"]['lon'] 
        # Convertit les coordonnées en Web Mercator
        x,y = coor_wgs84_to_web_mercator(lon,lat)
        coordsx.append(x)
        coordsy.append(y)
    df = DataFrame({'nom': nom, 'total_possible': total_possible, 'nbre_emplacement_vide': nbre_emplacement_vide,'x':coordsx ,'y':coordsy ,"nbre_de_velo_disponible": nbre_de_velo_disponible})
    return df

# Fonction pour analyser les données des aménagements de pistes cyclables
def analyse_data_reparation_velo_pistes_cyclables(data):
    type_amenagement = [] # Stocke le type d'aménagement (réparation de vélo ou piste cyclable)
    position = []
    coordsx =[]
    coordsy = []
    for station in data:
        type_amenagement.append(station["type_amenagement"])
        position.append(station["rive"])
        coords = station["geo_shape"]["geometry"]["coordinates"][0]
        c_x=[]
        c_y=[]
        for c in coords:
            x,y = coor_wgs84_to_web_mercator(c[0],c[1])
            c_x.append(x)
            c_y.append(y)
        coordsx.append(c_x)
        coordsy.append(c_y)
    df = DataFrame({'type_amenagement': type_amenagement, 'position': position , 'x':coordsx ,'y':coordsy})
    return df

# Fonction pour analyser les données des stations
def analyse_data_reparation_velo_parc_relais(data):
    nom = []
    place_dispo_vehicule_ordi = []
    capacity = []
    etat = []
    date = []
    place_dispo_vehicule_elec =[]
    place_dispo_covoit= []
    place_dispo_PMR=[]
    coordsx = []
    coordsy = []
    for station in data:
        nom.append(station["nom"])
        date.append(datetime.fromisoformat(station["lastupdate"]))
        capacity.append(station["capaciteparking"])
        etat.append(station["etatouverture"])
        place_dispo_vehicule_ordi.append(station["jrdinfosoliste"])
        place_dispo_vehicule_elec.append(station["jrdinfoelectrique"])
        place_dispo_covoit.append(station["jrdinfocovoiturage"])
        place_dispo_PMR.append(station["jrdinfopmr"])
        lat, lon =station["coordonnees"]['lat'], station["coordonnees"]['lon'] 
        x,y = coor_wgs84_to_web_mercator(lon,lat)
        coordsx.append(x)
        coordsy.append(y)
    df = DataFrame({'date': date,'etat':etat, 'nom': nom, 'place_dispo_voit_perso': place_dispo_vehicule_ordi, 'place_dispo_voit_elec': place_dispo_vehicule_elec, 'place_dispo_PMR': place_dispo_PMR,'x':coordsx ,'y':coordsy ,"place_dispo_covoit": place_dispo_covoit, 'capacity' : capacity})
    return df

# Analyse les données relatives aux stations de transports en commun
def analyse_data_reparation_velo_trans_comm(data):
    nom=[]
    coordsx =[]
    coordsy = []
    for station in data:
        nom.append(station["nom"])
        lat, lon =station["coordonnees"]['lat'], station["coordonnees"]['lon'] 
        x,y = coor_wgs84_to_web_mercator(lon,lat)
        coordsx.append(x)
        coordsy.append(y)
    df = DataFrame({'x':coordsx ,'y':coordsy, 'nom':nom  })
    return df

# Analyse les données relatives au trafic
def analyse_data_reparation_velo_trafic(data):
    max_averagevehiclespeed = [] # Stocke les vitesses de véhicules maximales
    min_averagevehiclespeed = [] # Stocke les vitesses de véhicules miniimales
    denomination = [] # Stocke les dénominations des stations
    for station in data:
        max_averagevehiclespeed.append(station["averagevehiclespeed"])
        min_averagevehiclespeed.append(station["averagevehiclespeed"])
        denomination.append(station["denomination"])
    df = DataFrame(
        {
            "max_averagevehiclespeed": max_averagevehiclespeed,
            "min_averagevehiclespeed": min_averagevehiclespeed,
            "denomination": denomination,
        }
    )
    return df

# fonctions pour créer des sous-onglets et des espaces réservés pour le contenu
def create_sub_tabs(title1, title2):
    sub_tab_1 = TabPanel(child=Column(), title=title1)
    sub_tab_2 = TabPanel(child=Column(), title=title2)
    return Tabs(tabs=[sub_tab_1, sub_tab_2])

def create_content_placeholder():
    return Column()

################################### Traitement de données

# Charger les données en temps réels sur les stations velos
STATIONS_DATA = load_data_from_url("https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-des-stations-le-velo-star-en-temps-reel/records?limit=-1")
stations_df = analyse_station_velo(STATIONS_DATA)
source1 = ColumnDataSource(stations_df)

# Charger les données des sur les aménagements de pistes cyclables
AMENAGEMENT_DATA = load_data_from_json_file("amenagement_cyclable.json")
amenagement_df = analyse_data_reparation_velo_pistes_cyclables(AMENAGEMENT_DATA)
source2 = ColumnDataSource(amenagement_df)

#Chargement des donnees des stations de reparation
data = load_data_from_json_file("stations-reparation-velo.json")
reparation = analyse_data_reparation_velo(data)
source = ColumnDataSource(reparation)

#Chargement des données pour les accidents corporels
df_accidents = pd.read_json("accidents_corporels.json", encoding='utf-8')
df_accidents['wms_time'] = pd.to_datetime(df_accidents['wms_time'], utc=True)
df_accidents['year'] = df_accidents['wms_time'].dt.year
df_grouped = df_accidents.groupby('year').agg({'ntu': 'sum', 'nbh': 'sum', 'nbnh': 'sum'}).reset_index()
# Calcul de la moyenne du nombre de personne tué, blessé hospitalisées et blessé non hospitalisées pour chaque année
df_grouped['ntu_mean'] = df_accidents.groupby('year')['ntu'].mean().values
df_grouped['nbh_mean'] = df_accidents.groupby('year')['nbh'].mean().values
df_grouped['nbnh_mean'] = df_accidents.groupby('year')['nbnh'].mean().values
df_grouped['ntu_orig'] = df_grouped['ntu']
df_grouped['nbh_orig'] = df_grouped['nbh']
df_grouped['nbnh_orig'] = df_grouped['nbnh']
source_accidents = ColumnDataSource(df_grouped)
years = df_grouped['year']

# Importation des données sur l'etat-des-parcs relai
data_relais = load_data_from_url("https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/tco-parcsrelais-star-etat-tr/records?limit=20")
df_parc_relais = analyse_data_reparation_velo_parc_relais(data_relais)
first_date = df_parc_relais['date'].iloc[0]
# Formater la date pour le titre
title_date = first_date.strftime("%d/%m/%Y à %Hh%M")
#Conversion en format Bokeh
source_parc_relais = ColumnDataSource(df_parc_relais)

#Traitement de données pour les transports en commun
bus = load_data_from_json_file("topologie_arret_bus.json")
noms_bus = analyse_data_reparation_velo_trans_comm(bus)
#Conversion en format Bokeh
source_bus_metro = ColumnDataSource(noms_bus)

#Traitement de données pour le trafic
data_trafic = analyse_data_reparation_velo_trafic(load_data_from_url("https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/records?where=insee%3D35238&limit=-1"))
# Regroupement des données par dénomination et calcul de la vitesse moyenne maximale et minimale des véhicules
grouped_data = data_trafic.groupby("denomination").agg(
    {"max_averagevehiclespeed": "max", "min_averagevehiclespeed": "min"}
)
#Index pour l'axe des x
denominations = grouped_data.index.tolist()
max_speed = grouped_data["max_averagevehiclespeed"].tolist()
min_speed = grouped_data["min_averagevehiclespeed"].tolist()

# Création de la source de données
source_trafic = ColumnDataSource(data=dict(denominations=denominations, max_speed=max_speed, min_speed=min_speed))

########################################## Mise en page

# Création de l'entête
header = Div(text="""<h1>MOBILITE URBAINE A RENNES</h1>""")
logo = Div(text="""<img src="https://www.aft-dev.com/sites/default/files/styles/actualites_intro/public/actualites/mobilite.jpeg?itok=I4mwEkRZ" width=100>""")

sub_tabs_station_velo = create_sub_tabs("Stations de Vélos et Pistes cyclables", "Stations de reparation de Vélos")
sub_tabs_transport_comm = create_sub_tabs("Emplacement de arrêts de Bus et Metro", "Etat du trafic par voies")
sub_tabs_autres_transports = create_sub_tabs("Fréquence des accidents", "Emplacement des parcs relais STAR")

#Page1 
div1_1=Div(text="""
    <style>
        .spacer {
            margin-bottom: 20px; /* Espacement entre les éléments */
        }
    </style>
    <h2>Gyldano DADJEDJI - Marc TANO - Kwami NOUCHET</h2>
    <p>La ville de Rennes, capitale bretonne est une ville en pleine expansion. Pour répondre aux défis de la congestion routière et de la pollution, la mobilité urbaine est au cœur des préoccupations.</p>
    <p class="spacer">Malgré ces options de transport en commun, les voitures restent un moyen de déplacement prédominant pour de nombreux habitants de Rennes. La mobilité urbaine représente donc un aspect crucial pour le développement de la ville.</p>
    <p class="spacer"><strong>OBJECTIF:</strong> Ce projet vise à explorer et visualiser les données relatives à la dynamique de la mobilité urbaine à Rennes. De façon plus précise, il consiste à comprendre et accéder aux données du trafic, notamment la fréquentation, les performances des lignes de transport en commun, ainsi que les flux de circulation des voitures, pour mieux comprendre le fonctionnement du système et améliorer l'expérience des usagers, qu'ils soient résidents ou nouveaux arrivants à Rennes.</p>
    <p>Ci-dessous, une présentation visuelle des différents modes de transport considérés dans le cadre de ce projet:</p>
""")

div1_2=Div(text="""
    <div style="text-align: center;">
        <h2>Stations vélos</h2>  <img src="https://www.star.fr/fileadmin/_processed_/9/3/csm_Station_VLS-_Nicolas_Joubard_c5ddddaea2.jpg" width=250>
    </div>
""")
div1_3=Div(text="""
    <div style="text-align: center;">
        <h2>Transports en commun</h2>  <img src="https://www.mce-info.org/wp-content/uploads/2024/03/bus_et_metro_rennes_resultat.webp" width=225>
    </div>
""")
div1_4=Div(text="""
    <div style="text-align: center;">
        <h2>Autres types de transports</h2>   <img src="https://images.caradisiac.com/images/9/1/0/5/189105/S0-faut-il-interdire-la-moto-dans-les-bouchons-668061.jpg" width=340>
    </div>
""")   
div_1_5=Div(text="""
    <div>
    <p><b>Remarque : Pour chaque onglet en déhors de la présentation, vous avez le choix entre deux sous-onglets pour explorer cette page web.</b></p>
    </div>
""")
#Page2
div_station_velo = Div(text="""
    <style>
        .spacer {
            margin-bottom: 20px; /* Espacement entre les éléments */
        }
        .information-text {
            font-size: 18px; /* Taille de police pour le texte d'information */
        }
        .custom-text {
            font-size: 14px; /* Taille de police pour le texte de commentaire */
            font-style: italic; /* Police en italique pour le texte de commentaire */
        }
    </style>
    <div style="text-align: left;">
        <p class="information-text"><strong>Information</strong></p>
        <p class="custom-text">Explorez le graphique ci-dessous pour accéder aux données concernant les vélos en libre-service et les pistes cyclables en Bretagne. En cliquant sur la légende "Pistes cyclables" du graphique, découvrez les directions disponibles en fonction du type de voie et les sens possibles, tandis qu'en sélectionnant la légende "Emplacement des stations vélos", vous obtiendrez des informations en temps réel sur l'état de la station : nom de la station, disponibilité des vélos, places de stationnement, etc.</p>
    </div>
""")

div_reparation_velo = Div(text="""
    <style>
        .spacer {
            margin-bottom: 20px; /* Espacement entre les éléments */
        }
        .information-text {
            font-size: 18px; /* Taille de police pour le texte d'information */
        }
        .custom-text {
            font-size: 14px; /* Taille de police pour le texte de commentaire */
            font-style: italic; /* Police en italique pour le texte de commentaire */
        }
    </style>
    <div style="text-align: left;">
        <p class="information-text"><strong>Information</strong></p>
        <p class="custom-text">Découvrez les stations de réparation de vélos en Bretagne en explorant le graphique ci-dessous. En cliquant sur une station, accédez aux services offerts, tels que les options de réparation, de gonflage de pneus, etc.</p>
    </div>
""")

#Page3 
div_arret_busmetro = Div(text="""
    <style>
        .spacer {
            margin-bottom: 20px; /* Espacement entre les éléments */
        }
        .information-text {
            font-size: 18px; /* Taille de police pour le texte d'information */
        }
        .custom-text {
            font-size: 14px; /* Taille de police pour le texte de commentaire */
            font-style: italic; /* Police en italique pour le texte de commentaire */
        }
    </style>
    <div style="text-align: left;">
        <p class="information-text"><strong>Information</strong></p>
        <p class="custom-text">Explorez la carte ci-dessous pour découvrir l'ensemble des arrêts de bus et de métro de la métropole bretonne. Veuillez noter que les données disponibles sur le site de Rennes Métropole sont limitées et ne fournissent pas une représentation exhaustive des arrêts de transport en commun, permettant de visualiser l'ensemble des bus et métros disponibles pour chaque arrêt. Cependant, vous pouvez zoomer pour obtenir un aperçu des points de transport disponibles dans votre commune ou votre quartier. Cliquez sur un arrêt pour afficher son nom, avec la possibilité de voir la position de l'arrêt dans les deux sens de circulation.</p>
    </div>
""")

div_etat_trafic = Div(text="""
    <style>
        .spacer {
            margin-bottom: 20px; /* Espacement entre les éléments */
        }
        .information-text {
            font-size: 18px; /* Taille de police pour le texte d'information */
        }
        .custom-text {
            font-size: 14px; /* Taille de police pour le texte de commentaire */
            font-style: italic; /* Police en italique pour le texte de commentaire */
        }
    </style>
    <div style="text-align: left;">
        <p class="information-text"><strong>Information</strong></p>
        <p class="custom-text">Pour obtenir une vision globale du trafic à Rennes, nous vous proposons un diagramme interactif, afin de visualiser en temps réel les intervalles de vitesse sur chaque route. Ainsi, pour une route donnée, des valeurs minimales et maximales élevées indiquent un trafic fluide, tandis que des valeurs basses révèlent un trafic dense. De plus, vous avez la possibilité de consulter des diagrammes basés soit sur les vitesses minimales observées uniquement, soit sur les vitesses maximales observées.</p>
    </div>
""")

#Page4 
div_accident = Div(text="""
    <style>
        .spacer {
            margin-bottom: 20px; /* Espacement entre les éléments */
        }
        .information-text {
            font-size: 18px; /* Taille de police pour le texte d'information */
        }
        .custom-text {
            font-size: 14px; /* Taille de police pour le texte de commentaire */
            font-style: italic; /* Police en italique pour le texte de commentaire */
        }
    </style>
    <div style="text-align: left;">
        <p class="information-text"><strong>Information</strong></p>
        <p class="custom-text">Ce sous-onglet permet de visualiser le nombre de personnes tuées, de blessés hospitalisés et de blessés non hospitalisés par année. Il offre également la possibilité de choisir entre les données brutes et les données moyennes. L'analyse des graphiques montre une diminution significative des accidents en 2020, probablement liée aux mesures de confinement dues à la COVID-19.</p>
    </div>
""")

div_parc = Div(text="""
    <style>
        .spacer {
            margin-bottom: 20px; /* Espacement entre les éléments */
        }
        .information-text {
            font-size: 18px; /* Taille de police pour le texte d'information */
        }
        .custom-text {
            font-size: 14px; /* Taille de police pour le texte de commentaire */
            font-style: italic; /* Police en italique pour le texte de commentaire */
        }
    </style>
    <div style="text-align: left;">
        <p class="information-text"><strong>Information</strong></p>
        <p class="custom-text">Le sous-onglet "Emplacement des parcs relais STAR" offre une visualisation de l'emplacement des parkings du reseau STAR dans la ville de Rennes. Il permet un accès en temps réel à des informations détaillées telles que la capacité actuelle du parking, sa disponibilité, le nombre de places disponibles pour les covoiturages, ainsi que la répartition des véhicules selon leur type (électriques ou non).</p>
    </div>
""")

# Création des onglets pour les éléments du menu principal avec des sous-onglets
tab_present = TabPanel(child=Column(div1_1, Row(div1_2,div1_3,div1_4), div_1_5), title="Présentation de la page web")
tab_station_velo = TabPanel(child=sub_tabs_station_velo, title="Informations sur les stations vélo en libre service")
tab_transport_comm = TabPanel(child=sub_tabs_transport_comm, title="Informations sur les transports en commun")
tab_autres_transports = TabPanel(child=sub_tabs_autres_transports, title="Informations sur les autres types de transport")

################################################Graphiques

# Création des figures pour chaque sous-panneau
# Graphique des stations velo avec les pistes cyclables
plot_sub_tabs_station_velo = figure(x_axis_type="mercator", y_axis_type="mercator",title="Stations de Vélos Graph",
                    active_scroll="wheel_zoom", width=1200, height=360)

plot_sub_tabs_station_velo.add_tile('CartoDB Positron')

stations_circle = plot_sub_tabs_station_velo.circle(x="x", y="y", size=9, fill_color="orange", line_color="green", fill_alpha=0.8, source=source1,legend_label="Emplacement des stations de vélos")

amenagements_lines = plot_sub_tabs_station_velo.multi_line(xs='x', ys='y', source=source2, color="green", line_width=2, legend_label="Pistes cyclables")

# Outils de survol 
hover_tool_stations = HoverTool(tooltips=[('Nom de station', '@nom'),
                                          ('Total vélos disponibles', '@total_possible'),
                                          ('Emplacement vide actuelle', '@nbre_emplacement_vide'),
                                          ('Nombre de vélos disponibles', '@nbre_de_velo_disponible')],
                                renderers=[stations_circle])
plot_sub_tabs_station_velo.add_tools(hover_tool_stations)

hover_tool_amenagements = HoverTool(tooltips=[('Type de voie', '@type_amenagement'),
                                             ('Sens possibles', '@position')],
                                   renderers=[amenagements_lines])
plot_sub_tabs_station_velo.add_tools(hover_tool_amenagements)

# Ajout d'autres outils de navigation 
plot_sub_tabs_station_velo.add_tools(BoxZoomTool())
plot_sub_tabs_station_velo.add_tools(PanTool())
plot_sub_tabs_station_velo.add_tools(ResetTool())

# Ajout de legende
plot_sub_tabs_station_velo.legend.location = "top_right"
plot_sub_tabs_station_velo.legend.click_policy="hide"
plot_sub_tabs_station_velo.title.text = "Station velo en libre service et pistes cyclables"
plot_sub_tabs_station_velo.title.align = "center"

# Affichage
plot_station_velo = Column(plot_sub_tabs_station_velo, div_station_velo)

# Graphique des stations de réparation de velos
plot_sub_tabs_reparation_velo= figure(x_axis_type="mercator", y_axis_type="mercator",
           active_scroll="wheel_zoom", width=1200, height=365)

plot_sub_tabs_reparation_velo.add_tile('CartoDB Positron')

plot_sub_tabs_reparation_velo.triangle(x="x", y="y", size=10, fill_color="blue", fill_alpha=0.8, source=source)

hover_tool = HoverTool(tooltips=[('Lieu', '@Lieu'),
                                 ('Etat', '@etat'),
                                 ('Propose des services de gonflage', '@gonflage'),
                                 ('Propose des services de réparation', '@reparation')])
plot_sub_tabs_reparation_velo.add_tools(hover_tool)

plot_sub_tabs_reparation_velo.add_tools(BoxZoomTool())
plot_sub_tabs_reparation_velo.add_tools(PanTool())
plot_sub_tabs_reparation_velo.add_tools(ResetTool())

# Titre
plot_sub_tabs_reparation_velo.title.text = "Stations de réparation de vélo"
plot_sub_tabs_reparation_velo.title.align = "center"

# Affichage
plot_station_reparation_velo = Column(plot_sub_tabs_reparation_velo, div_reparation_velo)

# Graphique pour les arrêts de bus et métro
plot_bus_metro= figure(x_axis_type="mercator", y_axis_type="mercator",
           active_scroll="wheel_zoom", width=1200, height=360)
plot_bus_metro.add_tile('CartoDB Positron')

plot_bus_metro.circle(x="x", y="y", size=3, fill_color="red", fill_alpha=0.8, source=source_bus_metro)

hover_tool_arret_bus = HoverTool(tooltips=[('Nom de station', '@nom')])
plot_bus_metro.add_tools(hover_tool_arret_bus)

plot_bus_metro.title.text = "Visualisation des arrêts de Bus et Metro"
plot_bus_metro.title.align = "center"

plot_sub_transport_bus_metro = Column(plot_bus_metro, div_arret_busmetro)

# Diagramme sur l'état du trafic en temps réel
plot_sub_trafic= figure(
    x_range=denominations,
    y_range=(0, max(max_speed) + 10),
    height=400,
    width=1100,
    toolbar_location=None,
    tools=""
)

# Création des barres pour les vitesses maximales
max_speed_bars = plot_sub_trafic.vbar(
    x=dodge("denominations", -0.2, range=plot_sub_trafic.x_range),
    top="max_speed",
    width=0.4,
    source=source_trafic,
    color="blue",
    legend_label="Vitesse maximale",
)

# Création des barres pour les vitesses minimales
min_speed_bars = plot_sub_trafic.vbar(
    x=dodge("denominations", 0.2, range=plot_sub_trafic.x_range),
    top="min_speed",
    width=0.4,
    source=source_trafic,
    color="orange",
    legend_label="Vitesse minimale",
)

# Personnalisation de l'apparence du graphique
plot_sub_trafic.x_range.range_padding = 0.1
plot_sub_trafic.xgrid.grid_line_color = None
plot_sub_trafic.xaxis.major_label_orientation = np.pi / 4
plot_sub_trafic.yaxis.axis_label = "Vitesse moyenne du véhicule (km/h)"
plot_sub_trafic.legend.location = "top_left"
plot_sub_trafic.legend.title = "Légende"

# Ajout d'outils de survol
hover = HoverTool()
hover.tooltips = [
    ("Route", "@denominations"),
    ("Vitesse maximale", "@max_speed"),
    ("Vitesse minimale", "@min_speed"),
]
plot_sub_trafic.add_tools(hover)

plot_sub_trafic.title.text = "Vitesse moyenne maximale et minimale des véhicules en temps réel par route sur Rennes"
plot_sub_trafic.title.align = "center"

# Création du menu déroulant pour sélectionner l'option d'affichage
select_trafic = Select(title="Afficher", options=["Vitesse max/min", "Vitesse maximale", "Vitesse minimale"], value="Les deux")
select_trafic.js_on_change("value", CustomJS(args=dict(max_speed_bars=max_speed_bars, min_speed_bars=min_speed_bars), code="""
    const value = cb_obj.value;
    if (value === 'Vitesse max/min') {
        max_speed_bars.visible = true;
        min_speed_bars.visible = true;
    } else if (value === 'Vitesse maximale') {
        max_speed_bars.visible = true;
        min_speed_bars.visible = false;
    } else if (value === 'Vitesse minimale') {
        max_speed_bars.visible = false;
        min_speed_bars.visible = true;
    }
"""))

# Affichage du graphique et du menu déroulant
plot_sub_etat_trafic = Column(Row(plot_sub_trafic, select_trafic), div_etat_trafic)

#Diagramme pour le bilan des accidents corporels
p1  = figure(x_axis_label="Année", y_axis_label="Valeurs", width=1100, height=365)
p1.vbar_stack(['ntu', 'nbh', 'nbnh'], x='year', width=0.5, color=Blues3, legend_label=['NTU: Nombre de personnes tuées', 'NBH: Nombre de blessés hospitalisés', 'NBNH: Nombre de blessés non hospitalisés'], source=source_accidents)
p1.title.text = "Visualisation du bilan d'accidents corporels par année dans la ville de Rennes"
p1.title.align = "center"

hover = HoverTool(tooltips=[('Année', '@year'), ('NTU', '@ntu'), ('NBH', '@nbh'), ('NBNH', '@nbnh')])
p1.add_tools(hover)

select_accident = Select(title="Type de données:", value="Nombre réel", options=["Nombre réel", "Moyenne"])

callback = CustomJS(args=dict(source_accidents=source_accidents, select=select_accident), code="""
    var data = source_accidents.data;
    var type = select.value;
    var year = data['year'];

    if (type == "Moyenne") {
        source_accidents.data['ntu'] = source_accidents.data['ntu_mean'];
        source_accidents.data['nbh'] = source_accidents.data['nbh_mean'];
        source_accidents.data['nbnh'] = source_accidents.data['nbnh_mean'];
    } else {
        source_accidents.data['ntu'] = source_accidents.data['ntu_orig'];
        source_accidents.data['nbh'] = source_accidents.data['nbh_orig'];
        source_accidents.data['nbnh'] = source_accidents.data['nbnh_orig'];
    }
    
    source_accidents.change.emit();
""")

select_accident.js_on_change('value', callback)

plot_sub_autres_transport_accidents = Column(Row(p1 , select_accident), div_accident)

plot_sub_parc = figure(x_axis_type="mercator", y_axis_type="mercator",
           active_scroll="wheel_zoom", width=1100, height=365)

 
plot_sub_parc.add_tile('CartoDb Positron')

plot_sub_parc.diamond(x="x", y="y", size=15, fill_color="blue", fill_alpha=0.8, source=source_parc_relais)

hover_tool = HoverTool(tooltips=[('Nom', '@nom'),
                                 ('Etat', '@etat'),
                                 ('Capacité', '@capacity'),
                                 ('Places disponibles vehicule soliste', '@place_dispo_voit_perso'),
                                 ('Places disponibles vehicule electriques', '@place_dispo_voit_elec'),
                                 ('Places disponibles covoiturage', '@place_dispo_covoit'),
                                 ('Places disponibles PMR', '@place_dispo_PMR')])


plot_sub_parc.add_tools(hover_tool)
plot_sub_parc.title.text = f"Etat des Parcs Relais STAR le {title_date}"
plot_sub_parc.title.align = "center"
plot_sub_autres_transport_parc = Column(plot_sub_parc , div_parc)



# Ajouter les figures aux panneaux des sous-onglets
sub_tabs_station_velo.tabs[0].child.children.append(plot_station_velo)
sub_tabs_station_velo.tabs[1].child.children.append(plot_station_reparation_velo)

sub_tabs_transport_comm.tabs[0].child.children.append(plot_sub_transport_bus_metro)
sub_tabs_transport_comm.tabs[1].child.children.append(plot_sub_etat_trafic)

sub_tabs_autres_transports.tabs[0].child.children.append(plot_sub_autres_transport_accidents)
sub_tabs_autres_transports.tabs[1].child.children.append(plot_sub_autres_transport_parc)

# Créer une fonction pour mettre à jour le sous-onglet actif en fonction du bouton cliqué
callback = CustomJS(args=dict(tabs=Tabs(tabs=[tab_present,tab_station_velo, tab_transport_comm, tab_autres_transports])), code="""
    var active_index = cb_obj.active;
    tabs.active = active_index;
""")


# Création de la mise en page finale avec des boutons et des onglets
main_layout = Column(Row(logo,header),Tabs(tabs=[tab_present,tab_station_velo, tab_transport_comm, tab_autres_transports]))

# Affichage de la mise en page
show(main_layout)
