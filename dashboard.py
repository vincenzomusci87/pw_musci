import pandas as pd
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import simulatore





data_inizio = simulatore.data_inizio
data_fine = simulatore.data_fine
mesi_utili = simulatore.mesi_utili





# IMPORTA DATI DAL SIMULATORE

dati = simulatore.simulazione(data_inizio, data_fine, mesi_utili)

df_suolo = dati["df_suolo"]
df_colture = dati["df_colture"]
df_cultivar = dati["df_cultivar"]
df_ettari = dati["df_ettari"]
df_alberi = dati["df_alberi"]
df_alberi_varieta = dati["df_alberi_varieta"]
df_data_utile = dati["df_data_utile"]
df_clima = dati["df_clima"]
df_ciliegeto = dati["df_ciliegeto"]
df_oliveto = dati["df_oliveto"]
df_irrigazione = dati["df_irrigazione"]
df_irrigazione_olive = dati["df_irrigazione_olive"]
df_irrigazione_ciliegie = dati["df_irrigazione_ciliegie"]
df_danni = dati["df_danni"]
df_danni_olive = dati["df_danni_olive"]
df_danni_ciliegie = dati["df_danni_ciliegie"]
df_raccolta = dati["df_raccolta"]
df_raccolta_olive = dati["df_raccolta_olive"]
df_raccolta_ciliegie = dati["df_raccolta_ciliegie"]
df_fertilizzazione = dati["df_fertilizzazione"]
df_fertilizzazione_olive = dati["df_fertilizzazione_olive"]
df_fertilizzazione_ciliegie = dati["df_fertilizzazione_ciliegie"]
df_trattamento = dati["df_trattamento"]
df_trattamento_olive = dati["df_trattamento_olive"]
df_trattamento_ciliegie = dati["df_trattamento_ciliegie"]
df_potatura = dati["df_potatura"]
df_potatura_olive = dati["df_potatura_olive"]
df_potatura_ciliegie = dati["df_potatura_ciliegie"]
df_mansioni = dati["df_mansioni"]
df_costi_totali = dati["df_costi_totali"]



# CREAZIONE DATAFRAME DF_RESE E CALCOLI VARI: PROFITTO, RESE, COSTI, RICAVI (TOTALI, PER ETTARO, PER ALBERO) MARGINE PROFITTO, PREZZO MEDIO

df_raccolta_somme = df_raccolta.groupby(["Anno","Coltura"]).agg({"Quantità": "sum", "Ricavo": "sum"}).reset_index()
df_costi_totali_somme = df_costi_totali.groupby(["Anno","Coltura"]).agg({"Costo_dipendenti": "sum", "Costo_materiale": "sum", "Costo_totale_mansione": "sum"}).reset_index()

df_rese = pd.merge(df_raccolta_somme, df_costi_totali_somme, on=["Anno","Coltura"], how="left")
df_rese = df_rese.merge(df_colture[["Coltura","Ettari","Alberi TOT"]], on="Coltura", how="left")

df_rese["Profitto"] = df_rese["Ricavo"] - df_rese["Costo_totale_mansione"]
df_rese["Profitto Ha"] = df_rese["Profitto"] / df_rese["Ettari"]
df_rese["Profitto Albero"] = df_rese["Profitto"] / df_rese["Alberi TOT"]

df_rese["Quantità Ha"] = df_rese["Quantità"] / df_rese["Ettari"]
df_rese["Quantità Albero"] = df_rese["Quantità"] / df_rese["Alberi TOT"]

df_rese["Costi Ha"] = df_rese["Costo_totale_mansione"] / df_rese["Ettari"]
df_rese["Costi Albero"] = df_rese["Costo_totale_mansione"] / df_rese["Alberi TOT"]

df_rese["Ricavo Ha"] = df_rese["Ricavo"] / df_rese["Ettari"]
df_rese["Ricavo Albero"] = df_rese["Ricavo"] / df_rese["Alberi TOT"]

df_rese["Margine Profitto"] = (df_rese["Ricavo"] - df_rese["Costo_totale_mansione"]) / df_rese["Ricavo"] * 100


df_rese_varieta = df_raccolta.groupby(["Anno","Coltura","Varietà"]).agg({"Quantità": "sum", "Ricavo": "sum"}).reset_index()
df_rese_varieta = df_rese_varieta.merge(df_cultivar[["Coltura","Varietà","Alberi"]], how="left")

df_rese_varieta["Prezzo medio"] = df_rese_varieta["Ricavo"] / df_rese_varieta["Quantità"]
df_rese_varieta["Quantità Albero"] = df_rese_varieta["Quantità"] / df_rese_varieta["Alberi"]
df_rese_varieta["Ricavo Albero"] = df_rese_varieta["Ricavo"] / df_rese_varieta["Alberi"]









# DASH

app = JupyterDash(__name__, external_stylesheets=[dbc.themes.DARKLY])


anni_disponibili = sorted(df_clima["Anno"].unique())



app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H1("DASHBOARD - AZIENDA AGRICOLA MUSCI", style={"textAlign": "center", "fontWeight": "bold"}), className="align-items-center col-12"),
                    ]) 
                ]),
                
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col(html.H2([html.Span(id="coltura_selezionata"), html.Span(" - "), html.Span(id="anno_selezionato")]), style={"textAlign": "center"}, className="align-items-center", lg=10),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                id="coltura-dropdown",
                                                options=[
                                                    {"label": "Tutte", "value": "Tutte"},
                                                    {"label": "Oliveto", "value": "Oliveto"},
                                                    {"label": "Ciliegeto", "value": "Ciliegeto"}
                                                ],
                                                value="Tutte",
                                                clearable=False,
                                                style={"width": "100%", "textAlign": "center"},
                                                className="dropdown-custom"
                                            ),
                                            dcc.Dropdown(
                                                id="anno-dropdown",
                                                options=[{"label": str(a), "value": a} for a in anni_disponibili],
                                                value=anni_disponibili[-1],
                                                clearable=False,
                                                style={"width": "100%", "textAlign": "center"},
                                                className="dropdown-custom"
                                            ),
                                        ], lg=2),
                                    ]),
                                ]),
                            ], color="#5a5a5a", style={"textAlign": "center"}, className="mb-2"),
                        )
                    ]),

                    dbc.Row([

                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(html.B("RESA TOTALE")),
                                dbc.CardBody([html.H3(id="resa_coltura_annuale")])
                            ], color="#5a5a5a", style={"textAlign": "center"}, className="mb-2"),
                            xs=12, sm=6, lg=2 
                        ),

                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(html.B("RICAVO TOTALE")),
                                dbc.CardBody([html.H3(id="ricavo_coltura_annuale")])
                            ], color="#5a5a5a", style={"textAlign": "center"}, className="mb-2"),
                            xs=12, sm=6, lg=2
                        ),

                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(html.B("PROFITTO TOTALE")),
                                dbc.CardBody([html.H3(id="profitto_coltura_annuale")])
                            ], color="#5a5a5a", style={"textAlign": "center"}, className="mb-2"),
                            xs=12, sm=6, lg=2
                        ),

                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(html.B("COSTO TOTALE")),
                                dbc.CardBody([html.H3(id="costi_coltura_annuale")])
                            ], color="#5a5a5a", style={"textAlign": "center"}, className="mb-2"),
                            xs=12, sm=6, lg=2
                        ),

                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(html.B("N. IRRIGAZIONI")),
                                dbc.CardBody([html.H3(id="conta_irrigazioni_annuale")])
                            ], color="#5a5a5a", style={"textAlign": "center"}, className="mb-2"),
                            xs=12, sm=6, lg=2
                        ),

                        dbc.Col(
                            dbc.Card([
                                dbc.CardHeader(html.B("PRECIPITAZIONI")),
                                dbc.CardBody([html.H3(id="totale_pioggia_annuale")])
                            ], color="#5a5a5a", style={"textAlign": "center"}, className="mb-2"),
                            xs=12, sm=6, lg=2
                        ),
                    ], className="g-1"),


                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("ETTARI", style={"textAlign": "center"}),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([
                                            html.Div(id="numero_ettari", style={"textAlign": "center"}),

                                            dcc.Graph(id="grafico-semitorta_ettari", style={"textAlign": "center", "height": "200px"}, className="g-1")
                                        ])
                                    ]) 
                                ], style={"backgroundColor": "#5a5a5a"})
                            ], className="mb-2"),
                            dbc.Card([
                                dbc.CardHeader([html.Div("PER ETTARO")]),
                                dbc.CardBody([
                                    html.P(id="resa_ettaro_annuale"),
                                    html.P(id="ricavo_ettaro_annuale"),
                                    html.P(id="costi_ettaro_annuale"),
                                    html.P(id="profitto_ettaro_annuale")
                                ]),
                            ], style={"backgroundColor": "#5a5a5a", "textAlign": "center"}, className="mb-2"),
                            html.Div(id="card_varieta")
                        ], xs=12, lg=2), 


                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("RESE, RICAVI, COSTI E PROFITTI", style={"textAlign": "center"}),
                                dbc.CardBody([

                                    dbc.Row([
                                        dbc.Col(dcc.Graph(id="grafico-totali", style={"height": "300px"}), xs=12, lg=6), 
                                        dbc.Col(dcc.Graph(id="grafico-ettaro", style={"height": "300px"}), xs=12, lg=6), 
                                    ], className="g-1"),
                                    

                                    dbc.Row([
                                        dbc.Col(dcc.Graph(id="grafico-albero", style={"height": "300px"}), xs=12, lg=6),
                                        dbc.Col(dcc.Graph(id="grafico-costi2", style={"height": "300px"}), xs=12, lg=6)
                                    ], className="g-1"), 
                                    

                                    dbc.Row([
                                        dbc.Col(dcc.Graph(id="grafico-quantita_ciliegeto", style={"height": "300px"}), xs=12, lg=6),
                                        dbc.Col(dcc.Graph(id="grafico-ricavo_ciliegeto", style={"height": "300px"}), xs=12, lg=6)
                                    ], className="g-1"), 
                                    

                                    dbc.Row([
                                        dbc.Col(dcc.Graph(id="grafico-varieta", style={"height": "300px"}), width=12) 
                                    ]),
                                ], style={"backgroundColor": "#111111"})
                            ], className="mb-2"),
                            

                            dbc.Card([
                                dbc.CardHeader("DATI CLIMATICI", style={"textAlign": "center"}),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col(dcc.Graph(id="grafico-pioggia", style={"height": "300px"}), xs=12, lg=6),
                                        dbc.Col(dcc.Graph(id="grafico-umidita", style={"height": "300px"}), xs=12, lg=6)
                                    ], className="g-1"), 
                                    dbc.Row([
                                        dbc.Col(dcc.Graph(id="grafico-temp_max_min", style={"height": "300px"}), xs=12, lg=6),
                                        dbc.Col(dcc.Graph(id="grafico-vento", style={"height": "300px"}), xs=12, lg=6)
                                    ], className="g-1")
                                ], style={"backgroundColor": "#111111"})
                            ], className="mb-2"),


                            dbc.Card([
                                dbc.CardHeader("PRECIPITAZIONI, UMIDITA' DEL SUOLO E IRRIGAZIONI", style={"textAlign": "center"}),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col(dcc.Graph(id="grafico-irrigazione", style={"height": "400px"}), width=12)
                                    ]) 
                                ], style={"backgroundColor": "#111111"})
                            ], className="mb-2"),

                            dbc.Card([
                                dbc.CardHeader("NPK E FERTILIZZAZIONI", style={"textAlign": "center"}),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col(dcc.Graph(id="grafico-fertilizzazione_oliveto", style={"height": "300px"}), xs=12, lg=6),
                                        dbc.Col(dcc.Graph(id="grafico-fertilizzazione_ciliegeto", style={"height": "300px"}), xs=12, lg=6)
                                    ], className="g-1") 
                                ], style={"backgroundColor": "#111111"})
                            ], className="mb-2"),

                            dbc.Card([
                                dbc.CardHeader("STIMA DEI DANNI", style={"textAlign": "center"}),
                                dbc.CardBody(dcc.Graph(id="grafico-stima_danni"), style={"backgroundColor": "#111111"})
                            ], className="mb-2"),
                            dbc.Card([
                                dbc.CardHeader("STORICO", style={"textAlign": "center"}),
                                dbc.CardBody(dcc.Graph(id="grafico-grafici_riassuntivi"), style={"backgroundColor": "#111111"}),
                                dbc.CardBody(dcc.Graph(id="grafico-margine"), style={"backgroundColor": "#111111"})
                            ], className="mb-2"),
                        ], xs=12, lg=8),

                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("ALBERI", style={"textAlign": "center"}),
                                dbc.CardBody([
                                    dbc.Col([
                                        html.Div(id="numero_alberi", style={"textAlign": "center"}),
                                        dcc.Graph(id="grafico-semitorta_alberi", style={"textAlign": "center", "margin": "0 auto"})
                                    ])
                                ], style={"backgroundColor": "#5a5a5a"})
                            ], className="mb-2"),
                            dbc.Card([
                                dbc.CardHeader([
                                    html.Div("PER ALBERO"),
                                    html.Div(id="totale_alberi")
                                ]),
                                dbc.CardBody([
                                    html.P(id="resa_albero_annuale"),
                                    html.P(id="ricavo_albero_annuale"),
                                    html.P(id="costi_albero_annuale"),
                                    html.P(id="profitto_albero_annuale")
                                ]),
                            ], style={"backgroundColor": "#5a5a5a", "textAlign": "center"}, className="mb-2"),
                            html.Div(id="card_varieta_albero"),
                        ], xs=12, lg=2)
                    ], className="g-1"), 

                ])
                
            ], className="mb-2")
        ], width=12),
    ]),

], fluid=True, style={"backgroundColor": "#222", "padding": "10px", "paddingLeft": "10px", "paddingRight": "10px"})










@app.callback(
    Output("anno_selezionato", "children"),
    Output("coltura_selezionata", "children"),
    Output("grafico-pioggia", "figure"),
    Output("grafico-umidita", "figure"),
    Output("grafico-vento", "figure"),
    Output("grafico-temp_max_min", "figure"),
    Output("grafico-quantita_ciliegeto", "figure"),
    Output("grafico-ricavo_ciliegeto", "figure"),
    Output("grafico-irrigazione", "figure"),
    Output("grafico-fertilizzazione_oliveto", "figure"),
    Output("grafico-fertilizzazione_ciliegeto", "figure"),
    Output("resa_coltura_annuale", "children"),
    Output("ricavo_coltura_annuale", "children"),
    Output("profitto_coltura_annuale", "children"),
    Output("costi_coltura_annuale", "children"),
    Output("conta_irrigazioni_annuale", "children"),
    Output("resa_ettaro_annuale", "children"),
    Output("ricavo_ettaro_annuale", "children"),
    Output("costi_ettaro_annuale", "children"),
    Output("profitto_ettaro_annuale", "children"),
    Output("resa_albero_annuale", "children"),
    Output("ricavo_albero_annuale", "children"),
    Output("costi_albero_annuale", "children"),
    Output("profitto_albero_annuale", "children"),
    Output("card_varieta", "children"),
    Output("totale_pioggia_annuale", "children"),
    Output("card_varieta_albero", "children"),
    Output("grafico-costi2", "figure"),
    Output("grafico-varieta", "figure"),
    Output("grafico-albero", "figure"),
    Output("grafico-totali", "figure"),
    Output("grafico-ettaro", "figure"),
    Output("grafico-semitorta_ettari", "figure"),
    Output("grafico-semitorta_alberi", "figure"),
    Output("grafico-grafici_riassuntivi", "figure"),
    Output("grafico-stima_danni", "figure"),
    Output("grafico-margine", "figure"),
    Input("anno-dropdown", "value"),
    Input("coltura-dropdown", "value")
)





def aggiorna_grafici_cards(anno, coltura):

    


    
# TITOLO SCELTA ANNO E COLTURA
    
    anno_selezionato = anno

    if coltura != "Tutte":
        coltura_selezionata = coltura
    else:
        coltura_selezionata = "COMPLESSIVO"




    
# FILTRO ANNO SUI DATAFRAMES 
    
    df_aggiorna_rese = df_rese[df_rese["Anno"] == anno]
    df_aggiorna_rese_varieta = df_rese_varieta[df_rese_varieta["Anno"] == anno]
    df_aggiorna_costi = df_costi_totali[df_costi_totali["Anno"] == anno]
    df_aggiorna_costi_somme = df_costi_totali_somme[df_costi_totali_somme["Anno"] == anno]
    df_aggiorna_clima = df_clima[df_clima["Anno"] == anno]




# CALCOLO CARD
    
    
# CARD PRINCIPALI
    
    if coltura != "Tutte":
        df_aggiorna_rese = df_aggiorna_rese[df_aggiorna_rese["Coltura"] == coltura]


    resa_coltura_somma = df_aggiorna_rese["Quantità"].sum()
    ricavo_coltura_somma = df_aggiorna_rese["Ricavo"].sum()
    
    resa_coltura_annuale = html.Div(f"{resa_coltura_somma:,d}".replace(",", ".") + " kg")
    ricavo_coltura_annuale = html.Div(f"{ricavo_coltura_somma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €")
    

    
    if coltura != "Tutte":
        profitto_coltura_somma = df_aggiorna_rese[df_aggiorna_rese["Coltura"] == coltura]["Profitto"].sum()
        costi_coltura_somma = df_aggiorna_rese[df_aggiorna_rese["Coltura"] == coltura]["Costo_totale_mansione"].sum()
        irrigazioni_filtrato = df_irrigazione[(df_irrigazione["Anno"] == anno) & (df_irrigazione["Coltura"] == coltura)]
    else:
        profitto_coltura_somma = df_aggiorna_rese["Profitto"].sum()
        costi_coltura_somma = df_aggiorna_rese["Costo_totale_mansione"].sum()
        irrigazioni_filtrato = df_irrigazione[df_irrigazione["Anno"] == anno]

    profitto_coltura_annuale = html.Div([f"{profitto_coltura_somma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"])
    costi_coltura_annuale = html.Div([f"{costi_coltura_somma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"])
    conta_irrigazioni = len(irrigazioni_filtrato)
    conta_irrigazioni_annuale = html.Div([f"{conta_irrigazioni:,d}"])

    totale_pioggia_anno = df_aggiorna_clima["Precipitazioni_mm"].sum()
    totale_pioggia_annuale = html.Div([f"{totale_pioggia_anno:,.0f}".replace(",", ".") + " mm"])




# CARD PER ETTARO E PER ALBERO
    
    totale_resa = df_aggiorna_rese["Quantità"].sum()
    totale_ricavo = df_aggiorna_rese["Ricavo"].sum()
    totale_ettari = df_aggiorna_rese["Ettari"].sum()
    totale_alberi = df_aggiorna_rese["Alberi TOT"].sum()
    
    
    if coltura != "Tutte":
        df_aggiorna_rese = df_aggiorna_rese[df_aggiorna_rese["Coltura"] == coltura]
    
        resa_ettaro = df_aggiorna_rese["Quantità Ha"].sum()
        ricavo_ettaro = df_aggiorna_rese["Ricavo Ha"].sum()
        costi_ettaro = df_aggiorna_rese["Costi Ha"].sum()
        profitto_ettaro = df_aggiorna_rese["Profitto Ha"].sum()

        resa_albero = df_aggiorna_rese["Quantità Albero"].sum()
        ricavo_albero = df_aggiorna_rese["Ricavo Albero"].sum()
        costi_albero = df_aggiorna_rese["Costi Albero"].sum()
        profitto_albero = df_aggiorna_rese["Profitto Albero"].sum()
        


    else:
        resa_ettaro = totale_resa / totale_ettari
        ricavo_ettaro = totale_ricavo / totale_ettari
        costi_ettaro = df_aggiorna_rese["Costo_totale_mansione"].sum() / totale_ettari
        profitto_ettaro = df_aggiorna_rese["Profitto"].sum() / totale_ettari

        resa_albero = totale_resa / totale_alberi
        ricavo_albero = totale_ricavo / totale_alberi
        costi_albero = df_aggiorna_rese["Costo_totale_mansione"].sum() / totale_alberi
        profitto_albero = df_aggiorna_rese["Profitto"].sum() / totale_alberi


        
    resa_ettaro_annuale = html.Div([html.Span("RESA", className="card-body-name"), html.Br(), html.Span(f"{resa_ettaro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " kg", className="card-body-value"), html.Br()])
    ricavo_ettaro_annuale = html.Div([html.Span("RICAVO", className="card-body-name"), html.Br(), html.Span(f"{ricavo_ettaro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " kg", className="card-body-value"), html.Br()])
    costi_ettaro_annuale = html.Div([html.Span("COSTI", className="card-body-name"), html.Br(), html.Span(f"{costi_ettaro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " kg", className="card-body-value"), html.Br()])
    profitto_ettaro_annuale = html.Div([html.Span("PROFITTO", className="card-body-name"), html.Br(), html.Span(f"{profitto_ettaro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " kg", className="card-body-value"), html.Br()])
    
    resa_albero_annuale = html.Div([html.Span("RESA", className="card-body-name"), html.Br(), html.Span(f"{resa_albero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " kg", className="card-body-value"), html.Br()])
    ricavo_albero_annuale = html.Div([html.Span("RICAVO", className="card-body-name"), html.Br(), html.Span(f"{ricavo_albero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €", className="card-body-value"), html.Br()])
    costi_albero_annuale = html.Div([html.Span("COSTI", className="card-body-name"), html.Br(), html.Span(f"{costi_albero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €", className="card-body-value"), html.Br()])
    profitto_albero_annuale = html.Div([html.Span("PROFITTO", className="card-body-name"), html.Br(), html.Span(f"{profitto_albero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €", className="card-body-value"), html.Br()])



    
    







# CREAZIONE CARD PER VARIETA' (menu laterale sx)

    
    if coltura != "Tutte":
        df_aggiorna_rese_varieta = df_aggiorna_rese_varieta[df_aggiorna_rese_varieta["Coltura"] == coltura]


    
    card_varieta = [
        dbc.Card(
            [
            dbc.CardHeader(row["Varietà"] + " (TOTALE)"),
            dbc.CardBody([
                html.P([html.Span("RESA", style={"color": "#cccccc", "fontWeight": "bold", "fontSize": "14px"}), html.Br(), html.Span(f"{row['Quantità']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " kg", style={"fontSize": "18px", "fontWeight": "bold"})]),
                html.P([html.Span("RICAVO", style={"color": "#cccccc", "fontWeight": "bold", "fontSize": "14px"}), html.Br(), html.Span(f"{row['Ricavo']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €", style={"fontSize": "18px", "fontWeight": "bold"})]),
                html.P([html.Span("PREZZO MEDIO (Kg)", style={"color": "#cccccc", "fontWeight": "bold", "fontSize": "14px"}), html.Br(), html.Span(f"{row['Prezzo medio']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €", style={"fontSize": "18px", "fontWeight": "bold"})])
            ])
        ], color="#5a5a5a", style={"textAlign": "center"}, className="mb-2")
    for _, row in df_aggiorna_rese_varieta.iterrows()
    ]



    

# CREAZIONE CARD PER VARIETA' ED ALBERO (menu laterale dx)

    df_aggiorna_rese_varieta = df_aggiorna_rese_varieta.copy()
    media_resa_albero = df_aggiorna_rese_varieta["Quantità Albero"].mean()
    df_aggiorna_rese_varieta["IPR"] = df_aggiorna_rese_varieta["Quantità Albero"] / media_resa_albero
    
    card_varieta_albero = [
        dbc.Card(
            [
            dbc.CardHeader(html.Span(row["Varietà"] + " (PER ALBERO)"), className="card-header"),
            dbc.CardBody([
                html.P([html.Span("RESA", className="card-body-name"), html.Br(), html.Span(f"{row['Quantità Albero']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " kg", className="card-body-value")]),
                html.P([html.Span("RICAVO", className="card-body-name"), html.Br(), html.Span(f"{row['Ricavo Albero']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €", className="card-body-value")]),
                html.P([html.Span("IPR", className="card-body-name"), html.Br(), html.Span(f"{row['IPR']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €", className="card-body-value")])
            ])
        ], color="#5a5a5a", style={"textAlign": "center"}, className="mb-2")
    for _, row in df_aggiorna_rese_varieta.iterrows()
    ]





# CALCOLO ETTARI & ALBERI PER GRAFICI SEMITORTA
    
    totale_ettari = df_colture["Ettari"].sum()
    totale_alberi = df_colture["Alberi TOT"].sum()
    
    if coltura != "Tutte":
        df_colture_filtrato = df_colture[df_colture["Coltura"] == coltura]
        numero_ettari = df_colture_filtrato["Ettari"].sum()
        numero_alberi = df_colture_filtrato["Alberi TOT"].sum()
    else:
        numero_ettari = totale_ettari
        numero_alberi = totale_alberi




    
# GRAFICO SEMITORTA ETTARI

    fig_semitorta_ettari = go.Figure(go.Indicator(
        mode="gauge+number",
        value=numero_ettari,
        gauge={'axis': {'range': [0, totale_ettari]}, 'bar': {'color': 'green', 'thickness': 0.6}},
        domain={'x': [0.1, 0.9], 'y': [0, 1]}
    ))
    fig_semitorta_ettari.update_layout(
        height=200,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="#5a5a5a",
        plot_bgcolor="#5a5a5a",
        font_color="#ffffff"
    )




    
# GRAFICO SEMITORTA ALBERI
    
    fig_semitorta_alberi = go.Figure(go.Indicator(
        mode="gauge+number",
        value=numero_alberi,
        gauge={'axis': {'range': [0, totale_alberi]}, 'bar': {'color': 'blue', 'thickness': 0.6}},
        domain={'x': [0.1, 0.9], 'y': [0, 1]} 
    ))
    fig_semitorta_alberi.update_layout(
        height=200,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="#5a5a5a",
        plot_bgcolor="#5a5a5a",
        font_color="#ffffff"
    )



    
        
# GRAFICO PRODUTTIVO-ECONOMICO TOTALI
    
    df_aggiorna_rese = df_aggiorna_rese[df_aggiorna_rese["Anno"] == anno]
    
    if coltura != "Tutte":
        df_aggiorna_rese = df_aggiorna_rese[df_aggiorna_rese["Coltura"] == coltura]
        df_aggiorna_rese_varieta = df_aggiorna_rese_varieta[df_aggiorna_rese_varieta["Coltura"] == coltura]
        df_aggiorna_costi = df_aggiorna_costi[df_aggiorna_costi["Coltura"] == coltura]
    
    df_rese_melt = df_aggiorna_rese.melt(
        id_vars=["Anno", "Coltura"],
        value_vars=["Quantità","Ricavo","Costo_totale_mansione","Profitto"],
        var_name="Oggetto",
        value_name="Valore"
    )

    fig_totali = px.bar(
        df_rese_melt,
        x="Anno",
        y="Valore",
        color="Coltura",
        barmode="stack",
        facet_col="Oggetto",
        title=f"Resa, Ricavo, Costi e Profitto Totali - {anno}"
    )
    fig_totali.update_xaxes(title_text="", showticklabels=False)
    fig_totali.update_layout(
        title_font=dict(size=12),
        legend=dict(
            title_text="",
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=-0.2
        )
    )

    for annotation in fig_totali.layout.annotations:
        if "=" in annotation.text:
            annotation.text = annotation.text.split("=")[1]
        annotation.y = 0.00
        annotation.yanchor = "top"




        
#GRAFICO PRODUTTIVO-ECONOMICO PER ETTARO

    fig_ettaro = px.bar(
        df_aggiorna_rese,
        x="Coltura",
        y=["Quantità Ha", "Ricavo Ha", "Costi Ha", "Profitto Ha"],
        barmode="group",
        title=f"Resa, Ricavo, Costi e Profitto per Ettaro - {anno}",
    )
    fig_ettaro.update_layout(
        title_font=dict(size=12),
        legend=dict(
            title_text="",
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=-0.2
        )
    )

    


    
# GRAFICO PRODUTTIVO-ECONOMICO PER ALBERO

    fig_albero = px.scatter(
        df_aggiorna_rese_varieta,
        x="Quantità Albero",
        y="Ricavo Albero",
        size="IPR",
        color="Varietà",
        hover_data=["IPR"],
        title=f"Produzione e Ricavo per albero - {anno}",
    )
    fig_albero.update_layout(
        xaxis_title="Produzione per albero (kg)",
        yaxis_title="Ricavo per albero (€)",
    )





# GRAFICO COSTI

    fig_costi2 = px.bar(
        df_aggiorna_costi,
        x="Costo_totale_mansione",
        y="Attività",
        color="Coltura",
        orientation="h",
        barmode="stack",
        title=f"Costi specifici per attività - {anno}",
    )
    fig_costi2.update_layout(
        yaxis={'categoryorder':'total ascending'},
        yaxis_title="kg / €",
        title_font=dict(size=12),
        legend=dict(
            title_text="",
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )









    
    
# GRAFICI PRODUZIONE E RICAVO PER VARIETA 

    df_aggiorna_rese_varieta = df_aggiorna_rese_varieta[df_aggiorna_rese_varieta["Anno"] == anno]
    if coltura != "Tutte":
        df_aggiorna_rese_varieta = df_aggiorna_rese_varieta[df_aggiorna_rese_varieta["Coltura"] == coltura]
        
    fig_quantita_ciliegeto = px.bar(df_aggiorna_rese_varieta, x="Anno", y="Quantità", color="Varietà", barmode="group", title=f"Produzione per varietà - {anno}")
    fig_quantita_ciliegeto.update_xaxes(type="category")
    
    fig_ricavo_ciliegeto = px.bar(df_aggiorna_rese_varieta, x="Anno", y="Ricavo", color="Varietà", barmode="group", title=f"Ricavo per varietà - {anno}")
    fig_ricavo_ciliegeto.update_xaxes(type="category")



        
# GRAFICO PRODUZIONE - RICAVO PER VARIETA' - TREEMAP

    fig_varieta = px.treemap(
        df_aggiorna_rese_varieta,
        path=["Coltura","Varietà"],
        values="Quantità",
        color="Ricavo",
        color_continuous_scale="Viridis",
        title=f"Produzione e Ricavo per Varietà - {anno}",
    )
    





# GRAFICI CLIMA 
    
    fig_pioggia = px.line(df_aggiorna_clima, x="Data", y="Precipitazioni_mm", title=f"Precipitazioni - {anno}")
    fig_umidita = px.line(df_aggiorna_clima, x="Data", y="Umidità", title=f"Umidità - {anno}")
    fig_vento = px.line(df_aggiorna_clima, x="Data", y="Vento", title=f"Vento - {anno}")
    fig_temp_max_min = px.line(df_aggiorna_clima, x="Data", y=["Temperatura_MAX", "Temperatura_MIN"], title=f"Andamento Temperature - {anno}")
    fig_temp_max_min.update_layout(
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.1,
        xanchor="left",
        x=0
    ),
    margin=dict(t=150),
    legend_title_text=""
)



    

# GRAFICO IRRIGAZIONE
    
    df_aggiorna_irrigazione_oliveto = df_irrigazione_olive[df_irrigazione_olive["Anno"] == anno]
    df_aggiorna_irrigazione_ciliegeto = df_irrigazione_ciliegie[df_irrigazione_ciliegie["Anno"] == anno]
    df_aggiorna_irrigazione_oliveto = df_aggiorna_irrigazione_oliveto.drop_duplicates(subset=["Data"])
    df_aggiorna_irrigazione_ciliegeto = df_aggiorna_irrigazione_ciliegeto.drop_duplicates(subset=["Data"])

    fig_irrigazione = go.Figure()

    fig_irrigazione.add_trace(go.Bar(
        x=df_aggiorna_clima["Data"],
        y=df_aggiorna_clima["Precipitazioni_mm"],
        name="Pioggia (mm)",
        marker_color="cornflowerblue",
        opacity=0.7
    ))

    df_suolo["Anno"] = pd.to_datetime(df_suolo["Data"]).dt.year
    df_terreno = df_suolo[df_suolo["Anno"] == anno].sort_values("Data")
    df_oliveto = df_terreno[df_terreno["Coltura"] == "Oliveto"]
    df_ciliegeto = df_terreno[df_terreno["Coltura"] == "Ciliegeto"]
    
    fig_irrigazione.add_trace(go.Scatter(
        x=df_oliveto["Data"],
        y=df_oliveto["Umidità suolo (%)"],
        mode="lines+markers",
        name="Umidità suolo Uliveto",
        line=dict(color="lightgreen", width=2)
    ))
    
    fig_irrigazione.add_trace(go.Scatter(
        x=df_ciliegeto["Data"],
        y=df_ciliegeto["Umidità suolo (%)"],
        mode="lines+markers",
        name="Umidità suolo Ciliegeto",
        line=dict(color="deepskyblue", width=2)
    ))

    df_aggiorna_irrigazione_oliveto["Valore Y"] = 5
    fig_irrigazione.add_trace(go.Scatter(
        x=df_aggiorna_irrigazione_oliveto["Data"],
        y=df_aggiorna_irrigazione_oliveto["Valore Y"],
        mode="markers",
        name="Irrigazione Oliveto",
        marker=dict(size=10, color="darkorange", symbol="circle")
    ))

    df_aggiorna_irrigazione_ciliegeto["Valore Y"] = 10
    fig_irrigazione.add_trace(go.Scatter(
        x=df_aggiorna_irrigazione_ciliegeto["Data"],
        y=df_aggiorna_irrigazione_ciliegeto["Valore Y"],
        mode="markers",
        name="Irrigazione Ciliegeto",
        marker=dict(size=10, color="red", symbol="circle")
    ))

    fig_irrigazione.update_layout(
        title=f"Andamento pioggia e irrigazioni - {anno}",
        title_font=dict(size=14),
        height=400,
        template="plotly_dark"
    )



    

# GRAFICO FERTILIZZAZIONE & SUOLO PER OLIVETO

    df_suolo["Anno"] = pd.to_datetime(df_suolo["Data"]).dt.year
    df_terreno = df_suolo[df_suolo["Anno"] == anno].sort_values("Data")
    df_oliveto = df_terreno[df_terreno["Coltura"] == "Oliveto"]
    df_ciliegeto = df_terreno[df_terreno["Coltura"] == "Ciliegeto"]     
    df_fertilizzazione_oliveto = df_fertilizzazione_olive[df_fertilizzazione_olive["Anno"] == anno]
    df_fertilizzazione_oliveto = df_fertilizzazione_oliveto.drop_duplicates(subset=["Data"])
    df_fertilizzazione_oliveto["Valore Y"] = 100
    
    fig_fertilizzazione_oliveto = px.line(
        df_oliveto,
        x="Data",
        y=["Azoto N (%)","Fosforo P (mg/kg)","Potassio K (mg/kg)"],
        title=f"Andamento NPK e fertilizzazioni oliveto - {anno}",
        markers=True,
        height=300,
        labels={'variable': ''}
    )
    fig_fertilizzazione_oliveto.add_trace(go.Scatter(
        x=df_fertilizzazione_oliveto["Data"],
        y=df_fertilizzazione_oliveto["Valore Y"],
        mode="markers",
        name="Fertilizzazione",
        marker=dict(size=10, color="darkorange", symbol="star")
    ))
    fig_fertilizzazione_oliveto.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=0.02
        )
    )




        
# GRAFICO FERTILIZZAZIONE & SUOLO PER CILIEGETO

    df_fertilizzazione_ciliegeto = df_fertilizzazione_ciliegie[df_fertilizzazione_ciliegie["Anno"] == anno]
    df_fertilizzazione_ciliegeto = df_fertilizzazione_ciliegeto.drop_duplicates(subset=["Data"])
    df_fertilizzazione_ciliegeto["Valore Y"] = 100
    
    fig_fertilizzazione_ciliegeto = px.line(
        df_ciliegeto,
        x="Data",
        y=["Azoto N (%)","Fosforo P (mg/kg)","Potassio K (mg/kg)"],
        title=f"Andamento NPK e fertilizzazioni ciliegeto - {anno}",
        markers=True,
        height=300,
        labels={'variable': ''}
    )
    fig_fertilizzazione_ciliegeto.add_trace(go.Scatter(
        x=df_fertilizzazione_ciliegeto["Data"],
        y=df_fertilizzazione_ciliegeto["Valore Y"],
        mode="markers",
        name="Fertilizzazione",
    marker=dict(size=10, color="darkorange", symbol="star")
    ))
    fig_fertilizzazione_ciliegeto.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=0.02
        )
    )


    


# GRAFICO DANNI

    df_danni_melt = df_danni.melt(id_vars=["Anno", "Coltura"], var_name="Tipo Danno", value_name="Intensità (%)")
    stima_danni = px.line(
        df_danni_melt,
        x="Anno",
        y="Intensità (%)",
        color="Tipo Danno",
        line_group="Tipo Danno",
        facet_col="Coltura",
        markers=True,
        height=300,
        template="plotly_dark"
    )

    for annotation in stima_danni.layout.annotations:
        if "=" in annotation.text:
            annotation.text = annotation.text.split("=")[1]
        annotation.y = 1.00
        annotation.yanchor = "bottom"

    



# GRAFICO STORICO - RIASSUNTIVO (RICAVO E PRODUZIONE)

    torta_ricavi_totali = px.sunburst(df_raccolta, path=["Anno", "Coltura", "Varietà"], values='Ricavo')
    torta_quantità_totali = px.sunburst(df_raccolta, path=["Anno", "Coltura", "Varietà"], values='Quantità')

    grafici_riassuntivi = make_subplots(rows=1, cols=2, subplot_titles=("Ricavi", "Produzione"), specs=[[{"type": "domain"}, {"type": "domain"}]])
    grafici_riassuntivi.add_trace(torta_ricavi_totali.data[0], row=1, col=1)
    grafici_riassuntivi.add_trace(torta_quantità_totali.data[0], row=1, col=2)
    grafici_riassuntivi.update_layout(font_color="#ffffff", paper_bgcolor="#111111", height=300, margin=dict(l=00, r=00, t=30, b=20), template="plotly_dark")



    

# GRAFICO STORICO - MARGINE DI PROFITTO

    fig_margine = px.line(
        df_rese,
        x="Anno",
        y="Margine Profitto",
        color="Coltura",
        markers=True,
        title="Margine di profitto (%) per anno",
        height=350
    )
    fig_margine.update_xaxes(type="category")



    
    
    for fig in [fig_pioggia, fig_umidita, fig_vento, fig_temp_max_min, fig_quantita_ciliegeto, fig_ricavo_ciliegeto, fig_fertilizzazione_oliveto, fig_fertilizzazione_ciliegeto, fig_costi2, fig_varieta, fig_albero, fig_totali, fig_ettaro, fig_margine]:
        fig.update_traces(marker_line_width=0, opacity=0.99)
        fig.update_layout(
            title_font=dict(size=14),
            xaxis_title="",
            yaxis_title="",
            margin=dict(l=00, r=10, t=90, b=40),
            template="plotly_dark"
        )

    return anno_selezionato, coltura_selezionata, fig_pioggia, fig_umidita, fig_vento, fig_temp_max_min, fig_quantita_ciliegeto, fig_ricavo_ciliegeto, fig_irrigazione, fig_fertilizzazione_oliveto, fig_fertilizzazione_ciliegeto, resa_coltura_annuale, ricavo_coltura_annuale, profitto_coltura_annuale, costi_coltura_annuale, conta_irrigazioni_annuale, resa_ettaro_annuale, ricavo_ettaro_annuale, costi_ettaro_annuale, profitto_ettaro_annuale, resa_albero_annuale, ricavo_albero_annuale, costi_albero_annuale, profitto_albero_annuale, card_varieta, totale_pioggia_annuale, card_varieta_albero, fig_costi2, fig_varieta, fig_albero, fig_totali, fig_ettaro, fig_semitorta_ettari, fig_semitorta_alberi, grafici_riassuntivi, stima_danni, fig_margine











if __name__ == "__main__":
    app.run(debug=True)



