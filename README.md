# Projet de fin de formation "Data Analyst"
## [Wild Code School de Bordeaux](https://www.wildcodeschool.com/)



## "Soliguide outil de diagnostic territorial"</h4>


<div>Le projet de fin de formation est un projet d'une durée de 2 mois, durant lesquels les élèves continuent leurs études </br>(sous forme de quêtes Machine Learning avec la librairie python Scikit-Learn, Dashboards grâce aux outils Dash Plotly...)</div>

C'est ainsi que mon collègue [Jean-Baptiste Le Friant](https://www.linkedin.com/in/jean-baptiste-le-friant-6b8744aa/) et moi-même [Michaël Tirat](https://www.linkedin.com/in/michael-tirat/), avins choisi parmis les 4 sujets
</br> un thème complexe qu'est la précarité en France.

Les missions explicites étaient de :
- collecter des données publiques via des API (INSEE, France travail, DREES) afin de compoiler 4 années de dionnées sociales sur tout le territoire,
- Récolter les données de [Solinum](https://www.solinum.org/solidata/) afin de démontrer que Soliguide était un outil de diagnostic territorial,
- Réaliser au moin un modèle de Machine Learning (nous avons utilisé deux modèles : KNN et une pipeline orientée Logistic Regression)


Concernant les données publiques, nous avons :
- récolté 124 variables sociales de 104 départements sur 4 années (2009 à 2022),
- réalisé des calculs pour obtenir des KPI sociales telles que le nombre de personnes en situation précaire (fixé à 60% du taux de pauvreté monétaire), la part des familles monoparentales...

Concernant les données Solinum nous avons :
- "scrappé" les données 2023 (car les données fournies n'étaient disponibles que jusqu'à 2020) : langue du navigateur, nombre de connexions hebdomadaires...,
- réalisé une cartographie des structures listées grâce à la librairie python, triées par catégories...
- créé des KPI selon le pourcentage de structures accueillant exclusivement des femmes, des personnes sans papier...

Concernant le Machine Learning, nous avons :
- réalisé une cartographie des départements prioritaires dans le développement territorial de Soliguide (en comparaison avec les départements déjà couverts),
- créé un modèle prédictif en prenant chaque département en valeur catégorique afin de proposer une prédicition des dépenses sociales selon l'année et les valeurs des variables prises en compte.



# Pour ce projet, les outils utilisés ont été :
- power BI pour la structuration des données sociales ainsi que celles du site de Soliguide,
- Python pour l'EDA (Analyse Exploratoire des Données) avec Pandas et Numpy,
- Folium pour la création des cartographies (Choroplèthes et marqueurs),
- Scikit-Learn pour le Machine Learning,
- Dash Plotly pour le Dashboard interactif
- Git pour la mise à jour du code
- Vscode pour l'IDE d'écriture de code
- Google Colaboratory pour nos notebooks de tests de code.


# En conclusion :
Ce projet a été un réel engagement de notre part et nous sommes très fiers du travail restitué, que nous avons pu présenté en fin de formation intensive.

Nous tenons à remercier la Wild Code School pour ce que nous avons été en mesure de réaliser, et Phil notre formateur.

# Mise en ligne de l'application :
L'application est visible en ligne (attendre un peu car sous render, la mise en route de l'environnement met un peu de temps) :
Application SolidR : https://solidr-cl1j.onrender.com/
