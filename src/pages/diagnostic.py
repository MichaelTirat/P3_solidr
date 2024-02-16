import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster

urletab = r'datasets/etablissements_soliguide_total.csv'
dfetab = pd.read_csv(urletab)
filtered_df = dfetab
dfetab['code'] = dfetab['Code Postal'].apply(lambda x: str(x)[:2])

url_1 = r'datasets/recherches_cat_soliguide.csv'
df_recherche = pd.read_csv(url_1)
df_recherche_sorted = df_recherche.sort_values(by='nb_recherches', ascending=False)

url_2 = r'datasets/langues.csv'
dflang = pd.read_csv(url_2)

url_3 = r"datasets/recherches_services.csv"
df_services = pd.read_csv(url_3)
df_services_filtered = df_services.sort_values(by='nb_recherches', ascending=False)

url_4 = r'datasets/recherches_villes.csv'
df_villes = pd.read_csv(url_4)
df_villes_filtered = df_villes.sort_values(by='nb_recherches_2023', ascending=False)

url5 = r"datasets/recherches_2023.csv"
df_2023 = pd.read_csv(url5)

# Assuming `app` is your Dash app instance
dash.register_page(__name__)

option_zone = [{'label': 'Gironde - 33', 'value': '33'},
               {'label': 'Paris - 75', 'value': '75'},
               {'label': 'Seine-Saint-Denis - 93', 'value': '93'}]
option_category = [{'label': str(category), 'value': str(category)} for category in dfetab['grande_categorie'].unique()]

layout = html.Div([
    dbc.Row(html.H1("Soliguide, un outil de diagnostic territorial", className='padding_haut_bas',
                    style={'text-align': 'center'})),

    dbc.Row("Selectionner un département & une catégorie :", style={"padding-bottom": "2px", "text-align": "center"}),
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='select_zone', value='33', options=option_zone)),
        dbc.Col(dcc.Dropdown(id='select_category', value='alimentation', options=option_category))
    ], style={"padding-bottom": "5px"}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Nombre de lieux référencées"),
                dbc.CardBody(id='nb_etab')
            ])]),

        dbc.Col(dbc.Card([
            dbc.CardHeader(f"Accueil des réfugiés"),
            dbc.CardBody(id='pourcent_refugies')])),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Demandeurs d'asile :"),
                dbc.CardBody(id='demandeurs_asile')
            ])]),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Accueil exclusif des femmes"),
                dbc.CardBody(id='nb_str_femmes')
            ])]),

    ], style={"padding-bottom": "10px"}),
    # 2° lignes de cards

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Structures alimentaires :"),
                dbc.CardBody(id='nb_str_alimentaires')
            ])]),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Structures de santé :"),
                dbc.CardBody(id='nb_structures_sante')
            ])]),

    ]),

    # front carte :
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(html.Div(id='map_html')),
        dbc.Col(width=2)
    ]),

    # ZOOM SUR LA GIRONDE :
    dbc.Row(html.H4('Zoom sur la Gironde, données 2023 de Soliguide', style={"text-align": "center"}),
            style={"padding-top": "3em"}),
    dbc.Row([

        dbc.Col(dcc.Graph(figure=px.bar(df_recherche_sorted.head(5), x='Catégorie', y='nb_recherches', text_auto=True,
                                        title=f"Classement des 5 catégories les plus consultées"))),
        dbc.Col(dcc.Graph(figure=px.bar(df_services_filtered.head(10), x='services', y='nb_recherches', text_auto=True,
                                        title=f"Classement des services les plus recherchées")))
    ]),

    dbc.Row([

        dbc.Col(dcc.Graph(figure=px.pie(dflang, values='nb', names='nationalite',
                                        title='Répartition des recherches par langues étrangères'))),
        dbc.Col(dcc.Graph(figure=px.bar(df_villes_filtered.head(10), x='villes', y='nb_recherches_2023',
                                        title=f"Classement des villes selon le nombre de recherches")))
    ], style={"padding-top": "10px"}),

    dbc.Row(dcc.Graph(figure=px.bar(df_2023, x='Dates', y='nb_recherches_gironde',
                                    title=f"Consultations journalières du site sur l'année passée")),
            className="padding_haut_bas")

], className="padding_haut_bas")


@callback(
    [Output('nb_etab', 'children'),
     Output('pourcent_refugies', 'children'),
     Output('demandeurs_asile', 'children'),
     Output('nb_str_femmes', 'children'),
     Output('nb_str_alimentaires', 'children'),
     Output('nb_structures_sante', 'children'),
     Output('map_html', 'children'),
     ],
    [Input('select_zone', 'value'),
     Input('select_category', 'value')]
)
def zone_geo(select_zone, select_category):
    filtered_df = dfetab[dfetab['code'] == select_zone]

    nb_etab = filtered_df.shape[0]  # Count of rows
    pourcent_refugies = f"{round(len(filtered_df[filtered_df['refugie'] == True]) / len(filtered_df) * 100, 2)} %"
    nb_str_femmes = f"{round(len(filtered_df[filtered_df['Sexe'] == 'femme']) / len(filtered_df) * 100, 2)} %"
    nb_str_alimentaires = f"{len(filtered_df[filtered_df['grande_categorie'] == 'alimentation'])}"
    demandeurs_asile = f"{round(len(filtered_df[filtered_df['asile'] == True]) / len(filtered_df) * 100, 2)} %"
    nb_structures_sante = f"{len(filtered_df[filtered_df['grande_categorie'] == 'sante'])}"

    # carte folium :
    filtered_category = filtered_df[filtered_df['grande_categorie'] == select_category].drop_duplicates()
    carte_etab = folium.Map(location=[filtered_category['Lng'].mean(), filtered_category['Lat'].mean()], zoom_start=10,
                            tiles='OpenStreetMap')
    marker_cluster = MarkerCluster().add_to(carte_etab)  # Create a MarkerCluster object

    for index, row in filtered_category.iterrows():
        folium.Marker(
            location=[row['Lng'], row['Lat']],
            color='blue',
            fill=True,
            fill_opacity=0.5,
            fill_color='blue',
            opacity=0.8,
            tooltip=f"{row['Nom de la structure']}, {row['libelle_evenements']}"
        ).add_to(marker_cluster)  # Add marker

    map_html = html.Iframe(srcDoc=carte_etab.get_root().render(), style={'width': '100%', 'height': '600px'})

    return f"{nb_etab}", pourcent_refugies, demandeurs_asile, nb_str_femmes, nb_str_alimentaires, nb_structures_sante, map_html


