import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="Noticias Energía", layout="wide")
st.title("🔎 Noticias Relevantes sobre Energía (España y UE)")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                   (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Connection": "keep-alive",
}

# Palabras clave
keywords = [ "energía", "transición energética", "transición sostenible", "renovables", "nextgeneration",
    "sostenibilidad", "electricidad", "calor", "potencia", "nuclear", "solar", "eólica",
    "hidroeléctrica", "eficiencia energética", "aerogenerador", "aerotermia", "fotovoltaico",
    "biomasa", "energía térmica", "energía eléctrica", "geotermia", "almacenamiento hidroeléctrico",
    "almacenamiento térmico", "emisiones", "carbono", "descarbonización", "gases", "invernadero",
    "instalaciones", "energía verde", "fuentes de energía", "autoconsumo", "placas solares",
    "vehículos eléctricos", "vehículos híbridos" ]

exclusion_keywords = [ "subvención", "ayuda", "guerra", "militar", "ejército", "misil", "bomba", "ataque",
    "conflicto", "israel", "palestina", "iran", "ucrania", "rusia", "otan", "norte corea", "nuclear militar",
    "armamento", "defensa", "netanyahu", "trump", "putin", "hamás", "hezbolá", "suministro", "impacto", "fuentes" ]

# Regex
keywords_regex = re.compile(r'\b(?:' + '|'.join(re.escape(kw) for kw in keywords) + r')\b', re.IGNORECASE)
exclusion_regex = re.compile(r'\b(?:' + '|'.join(re.escape(kw) for kw in exclusion_keywords) + r')\b', re.IGNORECASE)

def is_relevant(title):
    return bool(keywords_regex.search(title)) and not exclusion_regex.search(title)

def run_scraper(nombre_medio, url, selector, base_url=None, attrs=None):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        articles = soup.select(selector) if not attrs else soup.find_all(attrs["tag"], class_=attrs["class"])
        results = []
        for a in articles:
            if not a or not a.get_text(strip=True): continue
            title = a.get_text(strip=True)
            link = a['href'] if a.has_attr('href') else None
            if not link:
                continue
            if base_url and not link.startswith("http"):
                link = base_url + link
            if is_relevant(title):
                results.append({
                    "medio": nombre_medio,
                    "título": title,
                    "url": link,
                    "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                })
        return results
    except Exception as e:
        return []

def extraer_noticias():
    medios = [
        ("EnergyNews", "https://www.energynews.es/", "article h2.entry-title a", None),
        ("EFEVerde", "https://efeverde.com/", "article h2 a", None),
        ("El Periódico de la Energía", "https://elperiodicodelaenergia.com/", "h3.entry-title a", None),
        ("Energías Renovables", "https://www.energias-renovables.com/", "div.enrTitularNoticia a", "https://www.energias-renovables.com"),
        ("Review Energy", "https://www.review-energy.com/", "div.card-title a", None),
        ("Diario de la Energía", "https://www.diariodelaenergia.com/", "h3.entry-title a", None),
        ("El Día", "https://www.eldia.es/", "article h3 a", "https://www.eldia.es"),
        ("Diario de Avisos", "https://diariodeavisos.elespanol.com/", "h2.entry-title a", None),
        ("El País", "https://elpais.com/", "h2.c_t a", "https://elpais.com"),
        ("El Mundo", "https://www.elmundo.es/", "h2.ue-c-cover-content__headline a", "https://www.elmundo.es"),
        ("La Vanguardia", "https://www.lavanguardia.com/", "h2 a", "https://www.lavanguardia.com"),
        ("ABC", "https://www.abc.es/", "h2 a", "https://www.abc.es"),
        ("EFE", "https://efe.com/", "article h3 a", "https://efe.com"),
        ("Europa Press", "https://www.europapress.es/", "div.noticiacuerpo h2 a", "https://www.europapress.es"),
        ("La Razón", "https://www.larazon.es/", "h2.title-news a", "https://www.larazon.es"),
        ("El Español", "https://www.elespanol.com/", "article h2 a", "https://www.elespanol.com"),
        ("Cadena SER Canarias", "https://cadenaser.com/ccaa/canarias/", "article h2 a", "https://cadenaser.com"),
        ("Euronews UE", "https://es.euronews.com/tag/union-europea", "main a", "https://es.euronews.com"),
        ("EnergiaParaElCambio", "https://energiaparaelcambio.com/", "main a", "https://energiaparaelcambio.com"),
    ]

    news = []
    for nombre, url, selector, base_url in medios:
        news += run_scraper(nombre, url, selector, base_url)

    return pd.DataFrame(news)

# INTERFAZ STREAMLIT
if st.button("🔍 Buscar noticias"):
    df = extraer_noticias()

    if df.empty:
        st.warning("🚫 No se encontraron noticias relevantes.")
    else:
        st.success(f"✅ Se encontraron {len(df)} noticias relevantes.")
        st.dataframe(df)

        # Descarga CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", csv, f"noticias_energia_{datetime.now().date()}.csv", "text/csv")
