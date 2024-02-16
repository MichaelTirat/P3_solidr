import dash
from dash import html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import geopandas as gpd
import folium

urldf = r'datasets/solidR_dataset_final_V2.csv'
df = pd.read_csv(urldf)
df = df.rename(columns={"tx_pauvrete_monaitaire": "tx_pauvrete_monetaire"})
dataset_file = r"datasets/carte_region.csv"
dataset = pd.read_csv(dataset_file, sep=';')
dataset = dataset.rename(columns={"tx_pauvrete_monaitaire": "tx_pauvrete_monetaire"})
df['pauvres'] = df['tx_pauvrete_monetaire'] * df['population'] / 100
default_year = 2022
default_region = 'Nouvelle-Aquitaine'
default_departement = 'Gironde'

# génération des options années dans le df :
options = [{'label': str(annee), 'value': annee} for annee in df['annee'].unique()]
options_annees_region = [{'label': str(annee), 'value': annee} for annee in df['annee'].unique()]
options_regions = [{'label': str(region), 'value': str(region)} for region in df['nom_region'].unique()]
options_national = [{'label': 'Taux de pauvreté', 'value': 'tx_pauvrete_monetaire'},
                    {'label': 'Salaire Net moyen', 'value': 'salaire_net_annuel_moyen'},
                    {'label': 'Taux de pauvreté (60%)', 'value': 'tx_pauvrete_monetaire'},
                    {'label': 'Taux de pauvreté actifs moins 30 ans', 'value': 'tx_pauvrete_30'},
                    {'label': 'Taux de pauvreté des plus 75 ans', 'value': 'tx_pauv_75'},
                    {'label': 'Taux de natalité', 'value': 'tx_natalite'},
                    {'label': 'Taux de mortalité infantile', 'value': 'tx_mortalite_infantile'},
                    {'label': 'Taux de mortalité', 'value': 'tx_mortalite'},
                    {'label': 'Taux ménages fiscaux imposés', 'value': 'tx_menages_fiscaux_imposes'},
                    {'label': 'Taux de logements suroccupés', 'value': 'tx_logements_suroccupes'},
                    {'label': 'Taux de locataires', 'value': 'tx_locataires'},
                    {'label': 'Taux de chomeurs moins 25 ans', 'value': 'tx_chomeurs_25'},
                    {'label': 'Taux de chômeurs + 25 ans', 'value': 'tx_chomeurs_50'},
                    {'label': 'Population des quartiers prioritaires', 'value': 'pop_quartiers_prioritaires'},
                    {'label': 'Part des familles monoparentales', 'value': 'part_familles_mono'},
                    {'label': "Nombre de demandeurs d'emplois", 'value': 'nb_demandeurs_emplois'},
                    {'label': 'Niveau de vie médian', 'value': 'niveau_vie_median'},
                    {'label': "Nombre d'allocataires RSA", 'value': 'nb_allocataires_rsa'},
                    {'label': "Nombre de bénéficiaires CMU(CSS)", 'value': 'nb_cmu_css'},
                    {'label': "Espérance de vie naissance", 'value': 'esperance_vie_naissance'},
                    {'label': "Nombre d'allocataires Prime d'Activité", 'value': 'nb_alloc_prime_activite'},
                    {'label': "Salaire net des femmes", 'value': 'salaire_net_femmes'},
                    {'label': "Nombre de logements", 'value': 'nb_logements'}]
options_national2 = [{'label': colonne, 'value': colonne} for colonne in
                     df.drop(columns=['annee', 'code_dep', 'departements', 'code_region', 'nom_region']).columns]
options_choro = [{'label': colonne, 'value': colonne} for colonne in
                 dataset.drop(columns=['annee', 'code_dep', 'departements', 'code_region', 'nom_region']).columns]
nb_select = [{'label': num, 'value': num} for num in range(5, 31)]
options_carte_regions = [{'label': str(region), 'value': str(region)} for region in dataset['nom_region'].unique()]
options_carte_departement = [{'label': str(departement), 'value': str(departement)} for departement in
                             dataset['departements'].unique()]
# conf tabs :
tab1_regions = html.Div([
    dbc.Row([

        dbc.Col(html.H6('Année :', style={'text-align': 'right'}, className="smallpadding")),

        dbc.Col(dcc.Dropdown(id='annee_region',
                             options=options_annees_region,
                             value=default_year,
                             style={'text-align': 'center'}, className="smallpadding")),
        dbc.Col(html.H6('Région :', style={'text-align': 'right'}, className="smallpadding")),

        dbc.Col(dcc.Dropdown(id='region_selection',
                             options=options_carte_regions,
                             value=default_region,
                             style={'text-align': 'center'}, className="smallpadding")),
    ]),

    dbc.Row([
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Population', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='Output-region-population', style={'text-align': 'center'})])),
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Taux de pauvreté', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='output_region_tx_pauvrete', style={'text-align': 'center'})])),
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Variation du taux de pauvreté (N-1)', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='output_region_tx_pauvrete_reg', style={'text-align': 'center'})])),
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Taux de chômage', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='output_region_tx_chom', style={'text-align': 'center'})])),

    ], className="padding_haut_bas"),

    dbc.Row([
        dbc.Col([html.P('Sélection de la région', style={'text-align': 'center'}),
                 dcc.Dropdown(id='menu_regions', options=options_regions,
                              value=default_region,
                              ),
                 html.P('Sélection de la variable de dégradé', style={'text-align': 'center', "padding-top": "10px"}),
                 dcc.Dropdown(id='choro_value', options=options_choro, value='tx_pauvrete_monetaire'),
                 html.P('Sélection de la variable des bulles', style={'text-align': 'center', "padding-top": "10px"}),
                 dcc.Dropdown(id='circle_value', options=options_choro, value='population')
                 ], width=2),
        dbc.Col(html.Div(id='graph_region'), width=10)], className="padding_haut_bas")

])

tab2_content = html.Div([
    dbc.Row([

        dbc.Col(html.H6('Année :', style={'text-align': 'right'})),

        dbc.Col(dcc.Dropdown(id='annee_departement',
                             options=options_annees_region,
                             value=default_year,
                             style={'text-align': 'center'})),
        dbc.Col(html.H6('Département :', style={'text-align': 'right'})),

        dbc.Col(dcc.Dropdown(id='departement_selection',
                             options=options_carte_departement,
                             value=default_departement,
                             style={'text-align': 'center'})),
    ]),

    dbc.Row([
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Population', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='Output-departement-population', style={'text-align': 'center'})])),
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Taux de pauvreté', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='output_departement_tx_pauvrete', style={'text-align': 'center'})])),
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Variation du taux de pauvreté (N-1)', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='output_departement_tx_pauvrete_reg', style={'text-align': 'center'})])),
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Taux de chômage', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='output_departement_tx_chom', style={'text-align': 'center'})])),

    ], className="padding_haut_bas"),

    dbc.Row([
        dbc.Col([
            html.P('Sélection du département', style={'text-align': 'center'}),
            dcc.Dropdown(id='menu_departement', options=options_carte_departement,
                         value=default_departement,
                         style={'text-align': 'center'}),
            html.P('Sélection de la variable du dégradé', style={'text-align': 'center', "padding-top": "10px"}),
            dcc.Dropdown(id='choro_value_departement', options=options_choro, value='tx_pauvrete_monetaire'),
            html.P('Sélection de la variable des bulles', style={'text-align': 'center', "padding-top": "10px"}),
            dcc.Dropdown(id='circle_value_departement', options=options_choro, value='population')
        ], width=2),
        dbc.Col(html.Div(id='graph_departement'), width=10)], className="padding_haut_bas")

])
# fin conf Tabs

dash.register_page(__name__, path="/")

layout = html.Div([
    dbc.Row(html.H1("Analyse du territoire français"), style={'text-align': 'center', 'padding-bottom': "2em"}),

    # sélection des années :
    dbc.Row(" ", style={"padding-top": '5em'}),

    dbc.Row([

        # population totale
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Population totale', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='output-annee-population', style={'text-align': 'center'})])),
        # taux de pauvreté
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Taux de pauvreté', style={'text-align': 'center', "font-size": "15px"}),
             dbc.CardBody(id='output-annee-taux-pauvrete', style={'text-align': 'center'})])),
        # VARIATION taux de pauvreté
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Variation du taux de pauvreté (N-1)', style={'text-align': 'center', "font-size": "15px"}),
             dbc.CardBody(id='output-annee-variation-taux-pauvrete', style={'text-align': 'center'})])),
        # Population pauvre
        dbc.Col(dbc.Card(
            [dbc.CardHeader('Population précaire', style={'text-align': 'center', 'font-size': '14px'}),
             dbc.CardBody(id='output-annee-pauvres', style={'text-align': 'center'})])),

    ]),

    # graphiques données nationales avec le top des régions :

    dbc.Card(dbc.Row([
        dbc.Col([
            html.H6("Année :", className='texte_soulign', style={'margin-top': '3em'}),
            dcc.Dropdown(id='annee_selection',
                         options=options,
                         value=default_year,
                         className='menus_centres'),
            html.H6("Donnée sociale :", className='texte_soulign'),
            dcc.Dropdown(
                id='menu_national',
                options=options_national,
                value='nb_demandeurs_emplois',
                className='menus_centres',
            ),
            html.H6("Nombre de départements à classer :", className='texte_soulign'),
            dcc.Dropdown(id='top_selection',
                         options=nb_select,
                         value=10,
                         className='menus_centres'),

            html.H6("Comparer avec :", className='texte_soulign'),
            dcc.Dropdown(id='line_selection',
                         options=[
                             {'label': 'Désactiver', 'value': 'desactiver'},
                             {'label': 'Taux de pauvreté', 'value': 'tx_pauvrete_monetaire'},
                             {'label': 'Nombre de personnes précaires', 'value': 'Nb pers. précaires'}
                         ],

                         value="Nb pers. précaires",
                         className='menus_centres'),

            html.H6("Inclure les DOM-TOM :", className='texte_soulign'),
            dcc.Dropdown(id='exclu_dom',
                         options=[
                             {'label': 'Oui', 'value': True},
                             {'label': 'Non', 'value': False},
                         ],
                         value=False,
                         className='menus_centres')

        ], width=4),

        dbc.Col([dcc.Graph(id='graph_national', style={'margin': '1em'})], width=8)

    ]), style={'margin-top': '4em'}),

    dbc.Row(html.P(f"Sources : Insee, France Travail, DREES", style={"font-size": "10px"})),

    # DEBUT DES TABS
    dbc.Tabs([
        dbc.Tab(tab1_regions, label="Données régionales"),
        dbc.Tab(tab2_content, label="Données départementales")
    ],
        style={'padding-top': '6em'}),
    # FIN DES TABS

], style={"padding": "2em"})


# callbask cards nationales :
@callback(
    [
        Output('output-annee-population', 'children'),
        Output('output-annee-taux-pauvrete', 'children'),
        Output('output-annee-variation-taux-pauvrete', 'children'),
        Output('output-annee-pauvres', 'children'),

    ],
    [
        Input('annee_selection', 'value'),
    ]
)
def update_df(annee_selection):
    df = pd.read_csv(urldf)
    df['pauvres'] = df['tx_pauvrete_monetaire'] * df['population'] / 100
    arrow_icon = html.I(className="fa fa-arrow-up", style={'color': 'red'})

    kpi_poptotale = f"{df[df['annee'] == annee_selection]['population'].sum(): ,} ".replace(',', ' ')
    kpi_tx_pauvrete = f"{round(df[df['annee'] == annee_selection]['tx_pauvrete_monetaire'].mean(), 2)} %"
    kpi_variation_tx_pauvrete = round(
        df[df['annee'] == annee_selection]['tx_pauvrete_monetaire'].mean() - df[df['annee'] == annee_selection - 1][
            'tx_pauvrete_monetaire'].mean(), 2)
    kpi_pauvres = f"{int(df[df['annee'] == annee_selection]['pauvres'].sum()): ,}".replace(',', ' ')

    if kpi_variation_tx_pauvrete < 0:
        arrow_icon = html.I(className="fa fa-arrow-down", style={'color': 'green'})

    return f"{kpi_poptotale[0:3]},{kpi_poptotale[3:6]} millions ", kpi_tx_pauvrete, [kpi_variation_tx_pauvrete,
                                                                                     arrow_icon], f"{kpi_pauvres[0:3]},{kpi_pauvres[3:6]} millions "


# call back du graphique à l'échelle nationale :
@callback(
    Output('graph_national', 'figure'),
    [
        Input('annee_selection', 'value'),
        Input('menu_national', 'value'),
        Input('top_selection', 'value'),
        Input('line_selection', 'value'),
        Input('exclu_dom', 'value')
    ]

)
def update_graph_national(annee_selection, menu_national, top_selection, line_selection, exclu_dom):
    df = pd.read_csv(urldf)
    df['pauvres'] = df['tx_pauvrete_monetaire'] * df['population'] / 100
    df_national = df[(df['annee'] == annee_selection)]

    if exclu_dom == False:
        df_national = df_national.query(
            f"departements != 'Guadeloupe' and departements != 'La-Réunion' and departements != 'Mayotte' and departements != 'Martinique' and departements != 'Guyane'")
    else:
        pass

    df_graph = df_national.sort_values(by=menu_national, ascending=False).head(top_selection)

    fig = px.bar(df_graph, x='departements', y=menu_national,
                 title=f"Classement des {top_selection} Départements concernant le/la {menu_national}")

    # Ajout d'une ligne horizontale pour le taux de pauvreté ou le nombre de personnes précaires
    if line_selection != 'desactiver':
        if line_selection == 'tx_pauvrete_monetaire':
            line_values = df_graph['tx_pauvrete_monetaire']
        elif line_selection == 'Nb pers. précaires':
            line_values = df_graph['pauvres']
        else:
            line_values = None

        if line_values is not None:
            # Ajouter une trace Scatter pour la ligne sur l'axe y secondaire
            fig.add_trace(go.Scatter(x=df_graph['departements'], y=line_values, mode='lines', name=line_selection,
                                     line=dict(color='black', width=3), yaxis='y2'))

            # Ajouter un axe y secondaire
            fig.update_layout(yaxis2=dict(
                title='Taux de pauvreté' if line_selection == 'tx_pauvrete_monetaire' else 'Nombre de personnes précaires',
                overlaying='y', side='right'))
    else:
        fig = px.bar(df_graph, x='departements', y=menu_national,
                     title=f"Classement des {top_selection} Départements concernant le/la {menu_national}")

    return fig


# callback REGIONS DE FRANCE
@callback(
    [
        Output('Output-region-population', 'children'),
        Output('output_region_tx_pauvrete', 'children'),
        Output("output_region_tx_pauvrete_reg", "children"),
        Output('output_region_tx_chom', 'children'),
    ],
    [
        Input('region_selection', 'value'),
        Input('annee_region', 'value')
    ]
)
def update_region(region_selection, annee_region):
    df = pd.read_csv(urldf)
    df_reg = df[(df['annee'] == annee_region) & (df['nom_region'] == region_selection)]

    kpi_region_population = f"{df[(df['annee'] == annee_region) & (df['nom_region'] == region_selection)]['population'].sum(): ,}".replace(
        ',', ' ')
    kpi_region_tx_pauvrete = f"{round(df_reg['tx_pauvrete_monetaire'].mean(), 2)} %"
    kpi_variation_tx_pauvrete_reg_value = round(
        df[(df['annee'] == annee_region) & (df['nom_region'] == region_selection)]['tx_pauvrete_monetaire'].mean() -
        df[(df['annee'] == annee_region - 1) & (df['nom_region'] == region_selection)]['tx_pauvrete_monetaire'].mean(),
        2)

    # Ajouter une balise HTML i pour représenter l'icône de la flèche
    arrow_icon = html.I(className="fa fa-arrow-up", style={'color': 'red'})  # Par défaut, la flèche est rouge

    # Utiliser une logique conditionnelle pour déterminer la couleur de la flèche
    if kpi_variation_tx_pauvrete_reg_value < 0:
        # Si la valeur est négative, la flèche est verte
        arrow_icon = html.I(className="fa fa-arrow-down", style={'color': 'green'})

    kpi_variation_tx_pauvrete_reg = html.Span(f"{kpi_variation_tx_pauvrete_reg_value} % ", style={
        'fontWeight': 'bold'})  # Utiliser html.Span pour insérer la flèche à côté de la valeur
    kpi_tx_chom_region = f"{round(df_reg['tx_chomage_localise'].mean(), 2)} %"

    return kpi_region_population, kpi_region_tx_pauvrete, [kpi_variation_tx_pauvrete_reg,
                                                           arrow_icon], kpi_tx_chom_region


# carte folium régions :

@callback(
    Output('graph_region', 'children'),
    [
        Input('menu_regions', 'value'),
        Input('choro_value', 'value'),
        Input('circle_value', 'value')
    ])
def update_folium_region(menu_regions, choro_value, circle_value):
    # Load GeoJSON file for French regions
    geojson_file = r"datasets/departements-avec-outre-mer.geojson"
    gdf = gpd.read_file(geojson_file)

    # Load your dataset
    dataset_file = r"datasets/carte_region.csv"
    dataset = pd.read_csv(dataset_file, sep=';')
    dataset['pauvres'] = dataset['tx_pauvrete_monetaire'] * dataset['population'] / 100
    dataset = dataset[dataset['annee'] == 2022]
    # Merge the GeoDataFrame with your dataset
    merged_data = pd.merge(gdf, dataset, left_on='code', right_on='code_dep', how='left')
    merged_data = merged_data[merged_data['nom_region'] == menu_regions]

    # Create the Folium map
    m = folium.Map(location=[merged_data['geometry'].centroid.y.mean(), merged_data['geometry'].centroid.x.mean()],
                   zoom_start=7, tiles='OpenStreetMap')

    # Add the choropleth map
    folium.Choropleth(
        geo_data=gdf,
        data=merged_data,
        columns=['code_dep', choro_value],
        key_on='feature.properties.code',
        fill_color='OrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"{choro_value}",
    ).add_to(m)

    circle_radius = merged_data[circle_value].mean()

    for index, row in merged_data.iterrows():
        folium.CircleMarker(
            location=[row['geometry'].centroid.y, row['geometry'].centroid.x],
            radius=row[circle_value] * 6 / circle_radius,
            color='blue',
            fill=True,
            fill_opacity=0.5,
            fill_color='blue',
            opacity=0.2,
            tooltip=f"{row['departements']} : {choro_value} {(row[choro_value])} {circle_value} : {int(row[circle_value])}"
        ).add_to(m)

    map_html = m.get_root().render()
    return html.Iframe(srcDoc=map_html, style={'width': '100%', 'height': '600px'})


@callback(
    [
        Output('Output-departement-population', 'children'),
        Output('output_departement_tx_pauvrete', 'children'),
        Output("output_departement_tx_pauvrete_reg", "children"),
        Output('output_departement_tx_chom', 'children'),
    ],
    [
        Input('departement_selection', 'value'),
        Input('annee_departement', 'value')
    ]
)
def update_departement(departement_selection, annee_departement):
    df = pd.read_csv(urldf)
    df_reg = df[(df['annee'] == annee_departement) & (df['departements'] == departement_selection)]

    kpi_departement_population = f"{df[(df['annee'] == annee_departement) & (df['departements'] == departement_selection)]['population'].sum(): ,}".replace(
        ',', ' ')
    kpi_departement_tx_pauvrete = f"{round(df_reg['tx_pauvrete_monetaire'].mean(), 2)} %"
    kpi_variation_tx_pauvrete_departement_value = round(
        df[(df['annee'] == annee_departement) & (df['departements'] == departement_selection)][
            'tx_pauvrete_monetaire'].mean() -
        df[(df['annee'] == annee_departement - 1) & (df['departements'] == departement_selection)][
            'tx_pauvrete_monetaire'].mean(), 2)

    # Ajouter une balise HTML i pour représenter l'icône de la flèche
    arrow_icon = html.I(className="fa fa-arrow-up", style={'color': 'red'})  # Par défaut, la flèche est rouge

    # Utiliser une logique conditionnelle pour déterminer la couleur de la flèche
    if kpi_variation_tx_pauvrete_departement_value < 0:
        # Si la valeur est négative, la flèche est verte
        arrow_icon = html.I(className="fa fa-arrow-down", style={'color': 'green'})

    kpi_variation_tx_pauvrete_departement = html.Span(f"{kpi_variation_tx_pauvrete_departement_value} % ", style={
        'fontWeight': 'bold'})  # Utiliser html.Span pour insérer la flèche à côté de la valeur
    kpi_tx_chom_departement = f"{round(df_reg['tx_chomage_localise'].mean(), 2)} %"

    return kpi_departement_population, kpi_departement_tx_pauvrete, [kpi_variation_tx_pauvrete_departement,
                                                                     arrow_icon], kpi_tx_chom_departement


@callback(
    Output('graph_departement', 'children'),
    [
        Input('menu_departement', 'value'),
        Input('choro_value_departement', 'value'),
        Input('circle_value_departement', 'value')
    ])
def update_folium_departement(menu_departement, choro_value_departement, circle_value_departement):
    # Load GeoJSON file for French regions
    geojson_file = r"src/datasets/departements-avec-outre-mer.geojson"
    gdf = gpd.read_file(geojson_file)

    # Load your dataset
    dataset_file = r"src/datasets/carte_region.csv"
    dataset = pd.read_csv(dataset_file, sep=';')
    dataset['pauvres'] = dataset['tx_pauvrete_monetaire'] * dataset['population'] / 100
    dataset = dataset[dataset['annee'] == 2022]
    # Merge the GeoDataFrame with your dataset
    merged_data = pd.merge(gdf, dataset, left_on='code', right_on='code_dep', how='left')
    merged_data = merged_data[merged_data['departements'] == menu_departement]

    # Create the Folium map
    m = folium.Map(location=[merged_data['geometry'].centroid.y.mean(), merged_data['geometry'].centroid.x.mean()],
                   zoom_start=9, tiles='OpenStreetMap')

    # Add the choropleth map
    folium.Choropleth(
        geo_data=gdf,
        data=merged_data,
        columns=['code_dep', choro_value_departement],
        key_on='feature.properties.code',
        fill_color='OrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"{choro_value_departement}",
    ).add_to(m)

    circle_radius = merged_data[circle_value_departement].mean()

    for index, row in merged_data.iterrows():
        folium.CircleMarker(
            location=[row['geometry'].centroid.y, row['geometry'].centroid.x],
            radius=row[circle_value_departement] * 12 / circle_radius,
            color='blue',
            fill=True,
            fill_opacity=0.5,
            fill_color='blue',
            opacity=0.2,
            tooltip=f"{row['departements']} : {choro_value_departement} {(row[choro_value_departement])} {circle_value_departement} : {int(row[circle_value_departement])}"
        ).add_to(m)

    map_html = m.get_root().render()
    return html.Iframe(srcDoc=map_html, style={'width': '100%', 'height': '600px'})
