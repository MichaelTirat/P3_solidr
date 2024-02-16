import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import folium
import pandas as pd
from dash import html, dcc, Input, Output, callback, State
import geopandas as gpd
from sklearn.neighbors import NearestNeighbors
from folium.features import CustomIcon
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression

link = r"datasets/data_ml.csv"
df = pd.read_csv(link)

url = r"datasets/solidR_dataset_final.csv"
dfml = pd.read_csv(url)
dep_options = [{"label": departements, "value": departements} for departements in dfml['departements'].unique()]

depenses_sociales = [{'label': "Dépenses d'aides sociales totales", 'value': 'depenses_brutes_totales'},
                     {'label': 'Dépenses brutes RSA', 'value': 'depenses_brutes_rsa'},
                     {'label': "Dépenses d'aides sociales par habitant", 'value': 'depenses_brutes_par_habitant'},
                     {'label': "Dépenses d'Aides Sociales à l'Enfance", 'value': 'depenses_brutes_ASE'},
                     {'label': "Dépenses d'Aides Personnalisées à l'Autonomie", 'value': 'depenses_brutes_APA'},
                     {'label': "Dépenses d'Aides aux Adultes Handicapés", 'value': 'depenses_brutes_aah'}, ]

# debut KNN :
col_to_keep = ['nb_allocataires_rsa', 'nb_cmu_css', 'nb_demandeurs_emplois',
               'depenses_brutes_totales', 'nb_quartiers_prioritaires',
               'nb_demandeurs_emplois_ld', 'depenses_brutes_rsa', 'naissances',
               'depenses_brutes_ASE', 'total_explusions_locatives', 'population',
               'Expulsions "conditionnelles"', 'tx_activite', 'tx_pop_quartiers_prio',
               'tx_loges_gratuits', 'tx_chomage_localise', 'niveau_vie_median',
               'tx_natalite', 'disparites_revenus_deciles', 'part_familles_mono',
               'tx_mortalite_infantile', 'tx_logements_suroccupes',
               'depenses_brutes_APA', 'esperance_vie_naissance', 'tx_allocataires_rsa',
               'esperance_vie_65', 'inteniste_pauvrete', 'salaire_net_ouvriers',
               'tx_allocataires_aspa', 'tx_chomage_français']

df_2022 = df.query(f"annee == 2022")

X_knn_22 = df_2022[col_to_keep]
df_dep_93_2022 = df_2022[df_2022['DEP'] == '93']
df_num_dep_93_2022 = X_knn_22.loc[df_dep_93_2022.index]
model_KNN_dep_93_2022 = NearestNeighbors(n_neighbors=15).fit(X_knn_22)
neighbors_dep_22 = model_KNN_dep_93_2022.kneighbors(df_num_dep_93_2022)
dep_proches_2022 = neighbors_dep_22[1][0].tolist()

distance_22 = neighbors_dep_22[0][0].tolist()
data = {
    'distance_22': ["{:.10f}".format(distance) for distance in distance_22],
    'DEP': dep_proches_2022
}
df_voisins = pd.DataFrame(data)
df_voisins['distance_22'] = df_voisins['distance_22'].astype(float)
df_voisins['rank'] = df_voisins['distance_22'].rank(ascending=True)
df_voisins['DEP'] = df_voisins['DEP'].astype(str)

# cartographie KNN :
geojson_file = r"datasets/departements-avec-outre-mer.geojson"
gdf = gpd.read_file(geojson_file)
merged_data = pd.merge(df_voisins, gdf, left_on='DEP', right_on='code', how='left')

# Create the Folium map
m = folium.Map(location=[46.6031, 1.8883], zoom_start=6, tiles='OpenStreetMap')
# Add the choropleth map
folium.Choropleth(
    geo_data=gdf,
    data=merged_data,
    columns=['DEP', 'distance_22'],
    key_on='feature.properties.code',
    fill_color='OrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=f"{'distance_22'}",
).add_to(m)

logo_path = r'assets/logo_soliguide.png'

for index, row in df.iterrows():
    if row['dep_sol'] == 1:
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            color='blue',
            fill=True,
            fill_opacity=0.5,
            fill_color='blue',
            opacity=0.8,
            icon=folium.features.CustomIcon(logo_path, icon_size=(25, 25)),
            popup=f"{row['departements']}"
        ).add_to(m)
    else:
        pass

map_html = m.get_root().render()

dash.register_page(__name__)

layout = html.Div([

    html.H1('Analyses prédictives', className='texte_soulign'),
    dmc.Divider(size="xl"),

    html.H4("Cartographie des départements prioritaires :", className="texte_soulign",
            style={"margin-top": '4em', "margin-bottom": "10px"}),
    dbc.Row([
        dbc.Col(html.P(
            f"les zones colorées représentent le résultat de notre algorithme des départements prioritaires concernant les indicateurs de pauvreté. Les logos Soliguide indiquent les 30 départements dans lesquels la structure est présente.",
            className="smallfont", style={'margin-top': '30px'})),

        dbc.Col(html.Iframe(srcDoc=map_html, style={'width': '100%', 'height': '600px'}), width=8),
        dbc.Col('')
    ]),

    dbc.Row(html.H4("Prédiction des dépenses sociales"), style={"margin-top": "7em", "text-align": "center"}),
    dmc.Divider(size="xl"),

    dbc.Card([
        dbc.Row([
            dbc.Col([html.Label("Année"), dcc.Input(id='annee', type='number', value=2024)]),
            dbc.Col([html.Label("Dépense sociale"), dcc.Dropdown(
                id='depenses_sociales',
                options=depenses_sociales,
                value='depenses_brutes_totales')]),
            dbc.Col([html.Label("Département"), dcc.Dropdown(
                id='departements',
                options=dep_options,
                value='Gironde')])
        ], className="padding_haut_bas"),

        dbc.Row([
            dbc.Col([dbc.Card([html.Label("Population", className="texte_soulign"),
                               dcc.Input(id='population', className="texte_soulign")])]),
            dbc.Col([dbc.Card([html.Label("Expulsions locatives", className="texte_soulign"),
                               dcc.Input(id='total_explusions_locatives', className="texte_soulign")])]),
            dbc.Col([dbc.Card([html.Label("Nombre de ménages fiscaux", className="texte_soulign"),
                               dcc.Input(id='nb_menages_fiscaux', className="texte_soulign")])]),
            dbc.Col([dbc.Card([html.Label("Nombre de logements", className="texte_soulign"),
                               dcc.Input(id='nb_logements', className="texte_soulign")])]),
        ], className="margin_cote"),

        dbc.Row([
            dbc.Col([dbc.Card([html.Label("Nombre de demandeurs d'emplois", className="texte_soulign"),
                               dcc.Input(id='nb_demandeurs_emplois', className="texte_soulign")])]),
            dbc.Col([dbc.Card([html.Label("Nombre d'actifs", className="texte_soulign"),
                               dcc.Input(id="nb_actifs", className="texte_soulign")])]),
            dbc.Col([dbc.Card([html.Label("Nombre de naissances", className="texte_soulign"),
                               dcc.Input(id='naissances', className="texte_soulign")])]),
            dbc.Col([dbc.Card([html.Label("Nombre de décès", className="texte_soulign"),
                               dcc.Input(id='deces', className="texte_soulign")])]),
        ], className="margin_cote"),

    ]),

    dbc.Card([html.Button('Valider :', id='predict-button', n_clicks=0),
              html.Div(id='prediction_depenses_totales', style={"text-align": "center", "font-size": "30px"})],
             className="validation"),

]),


@callback(
    [Output('population', 'value'),
     Output('total_explusions_locatives', 'value'),
     Output('nb_menages_fiscaux', 'value'),
     Output('nb_logements', 'value'),
     Output('nb_demandeurs_emplois', 'value'),
     Output('nb_actifs', 'value'),
     Output('naissances', 'value'),
     Output('deces', 'value')],
    [Input('departements', 'value')]
)
def update_inputs(departements):
    if not departements:
        raise PreventUpdate

    # Récupérer les données du département sélectionné
    data_departement = dfml[dfml['departements'] == departements].iloc[0]

    return (data_departement['population'],
            data_departement['total_explusions_locatives'],
            data_departement['nb_menages_fiscaux'],
            data_departement['nb_logements'],
            data_departement['nb_demandeurs_emplois'],
            data_departement['nb_actifs'],
            data_departement['naissances'],
            data_departement['deces'])


@callback(
    Output('prediction_depenses_totales', 'children'),

    [Input('predict-button', 'n_clicks')],

    [State('annee', 'value'),
     State('depenses_sociales', 'value'),
     State('departements', 'value'),
     State('population', 'value'),
     State('total_explusions_locatives', 'value'),
     State('nb_menages_fiscaux', 'value'),
     State('nb_logements', 'value'),
     State('nb_demandeurs_emplois', 'value'),
     State('nb_actifs', 'value'),
     State('naissances', 'value'),
     State('deces', 'value'), ])
def update_budget(n_clicks, annee, depenses_sociales, departements, population, total_explusions_locatives,
                  nb_menages_fiscaux, nb_logements, nb_demandeurs_emplois, nb_actifs, naissances, deces):
    if n_clicks > 0:
        input_data = pd.DataFrame({
            'annee': [annee],
            'departements': [departements],
            'population': [population],
            "total_explusions_locatives": [total_explusions_locatives],
            'nb_menages_fiscaux': [nb_menages_fiscaux],
            "nb_logements": [nb_logements],
            "nb_demandeurs_emplois": [nb_demandeurs_emplois],
            "nb_actifs": [nb_actifs],
            "naissances": [naissances],
            "deces": [deces]

        })

        colonnes_to_keep = ['annee', 'departements', depenses_sociales, 'population', 'total_explusions_locatives',
                            'nb_menages_fiscaux', 'nb_logements', 'nb_demandeurs_emplois', 'nb_actifs', 'naissances',
                            'deces']

        # Séparer les features et la target
        X = dfml[colonnes_to_keep].drop(columns=[depenses_sociales])
        y = dfml[depenses_sociales]

        # Créer un préprocesseur
        cat_cols = ['departements']
        num_cols = X.columns.difference(cat_cols)

        cat_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        num_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='constant')),
            ('scaler', StandardScaler())
        ])

        preprocessor = ColumnTransformer([
            ('cat', cat_pipeline, cat_cols),
            ('num', num_pipeline, num_cols)
        ])

        # Entraîner le modèle
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('model', LinearRegression())
        ])

        model.fit(X, y)

        prediction_totale = model.predict(input_data)[0]

        ############################################## RETURNS

        return f"{int(prediction_totale)} euros"
    else:
        return 'Aucune estimation réalisée...'