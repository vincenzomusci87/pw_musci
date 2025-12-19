import numpy as np
import pandas as pd
from datetime import date
import random



# DEFINIZIONE DEL SEED

random.seed(1)
np.random.seed(1)



# DEFINIZIONI VARIABILI

nomi_varietà_ciliegeto = ["Ferrovia", "Bigarreau", "Black Star", "Giorgia", "Royal Tioga", "Early Lory", "Grace Star"]
nomi_varietà_oliveto = ["Coratina"]
data_inizio = "2021-01-01"
data_fine = "2025-12-31"

quantità_min_ciliegie = 70
quantità_max_ciliegie = 300
prezzo_min_ciliegie = 1.70
prezzo_max_ciliegie = 5.90
dipendenti_min_raccolta_ciliegie = 2
dipendenti_max_raccolta_ciliegie = 4
tariffa_dipendenti_raccolta_ciliegie = 65
quantità_min_olive = 1500
quantità_max_olive = 3000
prezzo_min_olive = 0.80
prezzo_max_olive = 1.10
dipendenti_min_raccolta_olive = 3
dipendenti_max_raccolta_olive = 4
tariffa_dipendenti_raccolta_olive = 65
tariffa_dipendenti_fertiliz_ciliegie = 60
tariffa_dipendenti_fertiliz_olive = 60
tariffa_dipendenti_trattam_ciliegie = 80
tariffa_dipendenti_trattam_olive = 80
tariffa_dipendenti_potatura_ciliegie = 75
tariffa_dipendenti_potatura_olive = 75
costo_materiale_fertiliz_ciliegie = 200
costo_materiale_fertiliz_olive = 300
costo_materiale_trattam_ciliegie = 500
costo_materiale_trattam_olive = 500
costo_materiale_potatura_ciliegie = 0
costo_materiale_potatura_olive = 0





# DEFINIZIONI MESI UTILI PER CIASCUN EVENTO

mesi_utili = {
    "Raccolta_olive": [11, 12],
    "Raccolta_ciliegie": [5, 6],
    "Potatura_olive": [1, 2, 3, 4],
    "Potatura_ciliegie": [10,11],
    "Irrigazione": [4,5,6,7,8,9,10],
    "Precipitazioni": {1:0.25, 2:0.20, 3:0.15, 4:0.10, 5:0.05, 6:0.02, 7:0.01, 8:0.02, 9:0.05, 10:0.10, 11:0.15, 12:0.20},
    "Temperatura_MAX_media": {1:14, 2:15, 3:17, 4:20, 5:25, 6:29, 7:33, 8:32, 9:27, 10:23, 11:18, 12:16},
    "Temperatura_MIN_media": {1:5, 2:6, 3:7, 4:10, 5:14, 6:18, 7:20, 8:21, 9:17, 10:14, 11:10, 12:7},
    "Trattamento_olive": [1, 4, 6, 9],
    "Trattamento_ciliegie": [1, 3, 6, 10],
    "Fertilizzazione_olive": [2, 4, 6],
    "Fertilizzazione_ciliegie": [2, 3, 4, 5]
}





# IMPORTAZIONE DATI SUOLO DA FILE CSV

def dati_suolo():
    df_suolo = pd.read_csv("dati_suolo.csv")
    return df_suolo




# IMPORTAZIONE INFO SULLE CARATTERISTICHE DELLE COLTIVAZIONI DA FILE EXCEL 

def dati_colture():
    colture = pd.read_excel("colture.xlsx", sheet_name=None)
    df_colture = colture["Coltura"]
    df_ciliegeto = colture["Ciliegeto"]
    df_oliveto = colture["Oliveto"]
    df_cultivar = pd.concat([df_ciliegeto, df_oliveto], ignore_index=True)
    df_ettari = df_colture[["Ettari"]]
    df_alberi = df_colture[["Alberi TOT"]]
    df_alberi_varieta = df_cultivar[["Varietà", "Alberi"]]
    return  {
        "df_colture": df_colture,
        "df_ciliegeto": df_ciliegeto,
        "df_oliveto": df_oliveto,
        "df_cultivar": df_cultivar,
        "df_ettari": df_ettari,
        "df_alberi": df_alberi,
        "df_alberi_varieta": df_alberi_varieta
    }





# DEFINIZIONE FUNZIONE PER DATAFRAME DATA

def dati_data(data_inizio, data_fine):
    data = pd.date_range(start=data_inizio, end=data_fine, freq='D')
    df_data_utile = pd.DataFrame({"Data": data})
    df_data_utile["Mese"] = df_data_utile["Data"].dt.month
    df_data_utile["Anno"] = df_data_utile["Data"].dt.year
    return df_data_utile





# DEFINIZIONE FUNZIONE PER DATAFRAME CLIMA

def clima(df_data_utile, mesi_utili):
    df_clima = df_data_utile.copy().reset_index(drop=True)
    df_clima["Mese"] = df_clima["Data"].dt.month
    df_clima["Anno"] = df_clima["Data"].dt.year
    df_clima["Temperatura_MAX_media"] = df_clima["Mese"].map(mesi_utili["Temperatura_MAX_media"])
    df_clima["Temperatura_MAX"] = np.round(np.random.normal(loc=df_clima["Temperatura_MAX_media"], scale=2.5, size=len(df_clima)), 1)
    df_clima["Temperatura_MIN_media"] = df_clima["Mese"].map(mesi_utili["Temperatura_MIN_media"])
    df_clima["Temperatura_MIN"] = np.round(np.random.normal(loc=df_clima["Temperatura_MIN_media"], scale=2.5, size=len(df_clima)), 1)
    df_clima["Umidità"] = np.round(np.random.uniform(40, 91, len(df_clima)), 1)
    df_clima["Vento"] = np.round(np.random.triangular(left=3, mode=7, right=50, size=len(df_clima)), 1)
    df_clima["Probabilità_pioggia"] = df_clima["Mese"].map(mesi_utili["Precipitazioni"])
    df_clima["Precipitazioni_mm"] = np.where(
        np.random.rand(len(df_clima)) < df_clima["Probabilità_pioggia"],
        np.round(np.random.uniform(0.1, 31, size=len(df_clima)), 1),
        0
    )
    df_clima["giorno_piovoso"] = df_clima["Precipitazioni_mm"] > 0.7
    df_clima["giorno_piovoso_5gg"] = df_clima["giorno_piovoso"].rolling(window=6, min_periods=1).sum()
    df_clima["Grandine"] = np.where(
         (df_clima["giorno_piovoso"] == True),
        (np.random.rand(len(df_clima)) < 0.05),
        0
    )
    df_clima = df_clima.drop(columns=["Temperatura_MIN_media","Temperatura_MAX_media","Probabilità_pioggia"])
    return df_clima





# DEFINIZIONE FUNZIONE PER DATAFRAME IRRIGAZIONE

def irrigazione(df_data_utile, mesi_utili, coltura, df_clima):
    df = df_data_utile[df_data_utile["Mese"].isin(mesi_utili)].copy()
    df = df.merge(df_clima[["Data", "Precipitazioni_mm", "giorno_piovoso", "giorno_piovoso_5gg"]], on="Data", how="left")
    df_irrigazione = df[(df.index % 10 == 0) & (df["giorno_piovoso_5gg"] == 0)].copy()
    df_irrigazione["Coltura"] = coltura
    df_irrigazione["Attività"] = "Irrigazione"
    df_irrigazione["Ore"] = np.where((coltura=="Oliveto"), np.random.randint(12, 17, size=len(df_irrigazione)), np.random.randint(6, 8, size=len(df_irrigazione)))
    df_irrigazione["Prezzo"] = np.random.randint(13, 19, size=len(df_irrigazione))
    df_irrigazione["Costo_totale_mansione"] = df_irrigazione["Ore"] * df_irrigazione["Prezzo"]
    df_irrigazione["Costo_dipendenti"] = 0
    df_irrigazione["Costo_materiale"] = 0
    return df_irrigazione[["Data", "Anno", "Coltura", "Attività", "Ore", "Prezzo", "Costo_totale_mansione", "Costo_dipendenti", "Costo_materiale"]]





# DEFINIZIONE FUNZIONE PER DATAFRAME STIMA DANNI

def danni(coltura, df_data_utile):
    anni = pd.to_datetime(df_data_utile["Data"]).dt.year.unique()
    df = pd.DataFrame({"Anno": anni})
    df["Coltura"] = coltura
    df["Pioggia/Grandine"] = np.where((coltura=="Oliveto"), np.random.triangular(left=0, mode=0, right=50, size=len(df)).astype(int), np.random.triangular(left=0, mode=10, right=50, size=len(df)).astype(int))
    df["Gelata"] = np.random.triangular(left=0, mode=0, right=50, size=len(df)).astype(int)
    df["Danni Umidità"] = np.random.triangular(left=0, mode=0, right=10, size=len(df)).astype(int)
    df["Danni Vento"] = np.random.triangular(left=0, mode=5, right=20, size=len(df)).astype(int)
    df["Pappagalli"] = np.random.triangular(left=0, mode=2, right=20, size=len(df)).astype(int)
    df["Mosca"] = np.where((coltura=="Oliveto"), np.random.triangular(left=0, mode=5, right=20, size=len(df)), 0).astype(int)
    df["Tignola"] = np.where((coltura=="Oliveto"), np.random.triangular(left=0, mode=5, right=20, size=len(df)), np.random.triangular(left=0, mode=2, right=20, size=len(df))).astype(int)
    df["Drosophila"] = np.where((coltura=="Ciliegeto"), np.random.triangular(left=0, mode=5, right=20, size=len(df)), 0).astype(int)
    df["Cinghiali"] = np.where((coltura=="Ciliegeto"), np.random.triangular(left=0, mode=5, right=20, size=len(df)), 0).astype(int)
    return df





# DEFINIZIONE FUNZIONE PER  DATAFRAME MANSIONE (per fertilizzazioni, trattamenti fitosanitari e potature)

def mansione(tipo_mansione, df_data_utile, mesi_utili, coltura, tariffa_dip, costo_materiale, fertil_o_tratt=True):
    df = df_data_utile[df_data_utile["Mese"].isin(mesi_utili)].copy()
    if fertil_o_tratt == True:
        df = df.groupby(["Anno","Mese"]).sample(n=1).reset_index(drop=True)
    df["Coltura"] = coltura
    df["Attività"] = tipo_mansione
    df["Num_dipendenti"] = np.random.randint(2, 4, size=len(df))
    df["Tariffa_dipendenti"] = tariffa_dip
    df["Costo_dipendenti"] = df["Num_dipendenti"] * df["Tariffa_dipendenti"]
    df["Costo_materiale"] = costo_materiale
    df["Costo_totale_mansione"] = df["Costo_dipendenti"] + df["Costo_materiale"]
    return df





# DEFINIZIONE FUNZIONE PER DATAFRAME RACCOLTA
    
def raccolta(df_data_utile, mesi_utili, coltura, quantità_min, quantità_max, prezzo_min, prezzo_max, dipendenti_min, dipendenti_max, tariffa_dip):
    df = df_data_utile[df_data_utile["Mese"].isin(mesi_utili)].copy()
    df["Coltura"] = coltura
    df["Varietà"] = np.where((coltura=="Oliveto"), np.random.choice(nomi_varietà_oliveto), np.random.choice(nomi_varietà_ciliegeto, size=len(df)))
    df["Quantità"] = np.random.randint(quantità_min, quantità_max+1, size=len(df))
    df["Prezzo"] = np.round(np.random.uniform(prezzo_min, prezzo_max, size=len(df)), 2)
    df["Ricavo"] = df["Quantità"] * df["Prezzo"]
    df["Num_dipendenti"] = np.random.randint(dipendenti_min, dipendenti_max+1, size=len(df))
    df["Tariffa_dipendenti"] = tariffa_dip
    df["Costo_dipendenti"] = df["Num_dipendenti"] * df["Tariffa_dipendenti"]
    return df[["Data", "Anno", "Coltura", "Varietà", "Quantità", "Prezzo", "Ricavo", "Num_dipendenti", "Costo_dipendenti"]]





# DEFINIZIONE FUNZIONE PER INZIARE LA SIMULAZIONE

def simulazione(data_inizio, data_fine, mesi_utili):
    df_suolo = dati_suolo()
    df_data_utile = dati_data(data_inizio, data_fine)
    df_clima = clima(df_data_utile, mesi_utili)
    
    info_colture = dati_colture()
    df_colture = info_colture["df_colture"]
    df_ciliegeto = info_colture["df_ciliegeto"]
    df_oliveto = info_colture["df_oliveto"]
    df_cultivar = info_colture["df_cultivar"]
    df_ettari = info_colture["df_ettari"]
    df_alberi = info_colture["df_alberi"]
    df_alberi_varieta = info_colture["df_alberi_varieta"]

    


    
# CREAZIONE DATAFRAME IRRIGAZIONE, STIMA DANNI, RACCOLTA, FERTILIZZAZIONE, TRATTAMENTO FITOSANITARIO E POTATURA (tutti sia per oliveto, sia per ciliegeto)

    df_irrigazione_olive = irrigazione(df_data_utile, mesi_utili["Irrigazione"], "Oliveto", df_clima)
    df_irrigazione_ciliegie = irrigazione(df_data_utile, mesi_utili["Irrigazione"], "Ciliegeto", df_clima)
    
    df_irrigazione = pd.concat([df_irrigazione_olive, df_irrigazione_ciliegie], ignore_index=True)

    
    df_fertilizzazione_olive = mansione("Fertilizzazione", df_data_utile, mesi_utili["Fertilizzazione_olive"], "Oliveto", tariffa_dipendenti_fertiliz_olive, costo_materiale_fertiliz_olive, fertil_o_tratt=True)
    df_fertilizzazione_ciliegie = mansione("Fertilizzazione", df_data_utile, mesi_utili["Fertilizzazione_ciliegie"], "Ciliegeto", tariffa_dipendenti_fertiliz_ciliegie, costo_materiale_fertiliz_ciliegie, fertil_o_tratt=True)
    
    df_fertilizzazione = pd.concat([df_fertilizzazione_olive, df_fertilizzazione_ciliegie], ignore_index=True)

    
    df_trattamento_olive = mansione("Trattamento", df_data_utile, mesi_utili["Trattamento_olive"], "Oliveto", tariffa_dipendenti_trattam_olive, costo_materiale_trattam_olive, fertil_o_tratt=True)
    df_trattamento_ciliegie = mansione("Trattamento", df_data_utile, mesi_utili["Trattamento_ciliegie"], "Ciliegeto", tariffa_dipendenti_trattam_ciliegie, costo_materiale_trattam_ciliegie, fertil_o_tratt=True)
    
    df_trattamento = pd.concat([df_trattamento_olive, df_trattamento_ciliegie], ignore_index=True)

    
    df_potatura_olive = mansione("Potatura", df_data_utile, mesi_utili["Potatura_olive"], "Oliveto", tariffa_dipendenti_potatura_olive, costo_materiale_potatura_olive, fertil_o_tratt=False)
    df_potatura_ciliegie = mansione("Potatura", df_data_utile, mesi_utili["Potatura_ciliegie"], "Ciliegeto", tariffa_dipendenti_potatura_ciliegie, costo_materiale_potatura_ciliegie, fertil_o_tratt=False)
    df_potatura = pd.concat([df_potatura_olive, df_potatura_ciliegie], ignore_index=True)

    df_mansioni = pd.concat([df_fertilizzazione, df_trattamento, df_potatura], ignore_index=True)
    
    
    df_raccolta_olive = raccolta(df_data_utile, mesi_utili["Raccolta_olive"], "Oliveto", quantità_min_olive, quantità_max_olive, prezzo_min_olive, prezzo_max_olive, dipendenti_min_raccolta_olive, dipendenti_max_raccolta_olive, tariffa_dipendenti_raccolta_olive)
    df_raccolta_ciliegie = raccolta(df_data_utile, mesi_utili["Raccolta_ciliegie"], "Ciliegeto", quantità_min_ciliegie, quantità_max_ciliegie, prezzo_min_ciliegie, prezzo_max_ciliegie, dipendenti_min_raccolta_ciliegie, dipendenti_max_raccolta_ciliegie, tariffa_dipendenti_raccolta_ciliegie)

    df_raccolta = pd.concat([df_raccolta_olive, df_raccolta_ciliegie], ignore_index=True)
    

    df_danni_olive = danni("Oliveto", df_data_utile)
    df_danni_ciliegie = danni("Ciliegeto", df_data_utile)
    
    df_danni = pd.concat([df_danni_olive, df_danni_ciliegie], ignore_index=True)

    


    
# ESPORTAZIONE TABELLE IN FORMATO CSV DEI DATAFRAME PRINCIPALI GENERATI DAL SIMULATORE

    df_irrigazione.to_csv("tabella_irrigazione.csv", index=False, encoding='utf-8')
    df_danni.to_csv("tabella_danni.csv", index=False, encoding='utf-8')
    df_mansioni.to_csv("tabella_mansioni.csv", index=False, encoding='utf-8')
    df_raccolta.to_csv("tabella_raccolta.csv", index=False, encoding='utf-8')
    df_suolo.to_csv("tabella_suolo.csv", index=False, encoding='utf-8')
    df_clima.to_csv("tabella_clima.csv", index=False, encoding='utf-8')
    df_colture.to_csv("tabella_colture.csv", index=False, encoding='utf-8')
    df_oliveto.to_csv("tabella_oliveto.csv", index=False, encoding='utf-8')
    df_ciliegeto.to_csv("tabella_ciliegeto.csv", index=False, encoding='utf-8')





# CREAZIONE DATAFRAME COSTI TOTALI

    df_costi_raccolta = df_raccolta.copy()
    df_costi_raccolta["Attività"] = "Raccolta"
    df_costi_raccolta["Costo_materiale"] = 0 
    df_costi_raccolta["Costo_totale_mansione"] = df_costi_raccolta["Costo_dipendenti"]

    df_costi_raccolta = df_costi_raccolta[["Data", "Anno", "Coltura", "Attività", "Costo_dipendenti", "Costo_materiale", "Costo_totale_mansione"]]
    df_costi_mansioni = df_mansioni[["Data", "Anno", "Coltura", "Attività", "Costo_dipendenti", "Costo_materiale", "Costo_totale_mansione"]]

    df_costi_irrigazione = df_irrigazione.copy()
    df_costi_irrigazione = df_costi_irrigazione[["Data", "Anno", "Coltura", "Attività", "Costo_dipendenti", "Costo_materiale", "Costo_totale_mansione"]]

    df_costi_totali = pd.concat([df_costi_raccolta, df_costi_mansioni, df_costi_irrigazione], ignore_index=True)




    
    return {
        "df_suolo": df_suolo,
        "df_colture": df_colture,
        "df_cultivar": df_cultivar,
        "df_ettari": df_ettari,
        "df_alberi": df_alberi,
        "df_alberi_varieta": df_alberi_varieta,
        "df_data_utile": df_data_utile,
        "df_clima": df_clima,
        "df_ciliegeto": df_ciliegeto,
        "df_oliveto": df_oliveto,
        "df_irrigazione": df_irrigazione,
        "df_irrigazione_olive": df_irrigazione_olive,
        "df_irrigazione_ciliegie": df_irrigazione_ciliegie,
        "df_danni": df_danni,
        "df_danni_olive": df_danni_olive,
        "df_danni_ciliegie": df_danni_ciliegie,
        "df_raccolta": df_raccolta,
        "df_raccolta_olive": df_raccolta_olive,
        "df_raccolta_ciliegie": df_raccolta_ciliegie,
        "df_fertilizzazione": df_fertilizzazione,
        "df_fertilizzazione_olive": df_fertilizzazione_olive,
        "df_fertilizzazione_ciliegie": df_fertilizzazione_ciliegie,
        "df_trattamento": df_trattamento,
        "df_trattamento_olive": df_trattamento_olive,
        "df_trattamento_ciliegie": df_trattamento_ciliegie,
        "df_potatura": df_potatura,
        "df_potatura_olive": df_potatura_olive,
        "df_potatura_ciliegie": df_potatura_ciliegie,
        "df_mansioni": df_mansioni,
        "df_costi_totali": df_costi_totali
    }



