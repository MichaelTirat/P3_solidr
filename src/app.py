
from dash import Dash, dcc,html, page_registry, page_container
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO

# SELECTION DES THEMES BOOTSTRAP
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY
theme_toggle = ThemeSwitchAIO(
    aio_id="theme",
    themes=[url_theme1, url_theme2],
    icons={"left": "fa fa-sun", "right": "fa fa-moon"},
)
local = r"assets/logo_solidr.png"
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

app = Dash(__name__, use_pages=True, external_stylesheets=[url_theme2, dbc_css])
server = app.server

navbar = dbc.NavbarSimple(
    [
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(page["name"], href=page["path"])
                for page in page_registry.values()
                if page["module"] != "pages.not_found_404"
            ],
            nav=True,
            label="Menu",
        ),
    ],
    brand="Solid'R de Soliguide",
    color="#154854",
    dark=True,
    className="mb-2",
)

footer = html.Footer(
    dbc.Row([
            dbc.Col([dbc.Col(html.Img(src = local, height = "100px")), dbc.Col(html.P(" @ Jean-Baptiste Le friant & Michaël Tirat,  tous droits réservés"))]),




    ]), className = "footer"
)





app.layout = dbc.Container(
    [navbar, theme_toggle, page_container, footer], fluid=True, className="dbc"
)

if __name__ == "__main__":
    app.run_server(debug=True)