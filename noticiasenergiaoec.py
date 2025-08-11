import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import time  # <- opcional, por si quieres pequeñas pausas visuales

st.set_page_config(page_title="Noticias Energía", layout="wide")
st.title("⚡ Noticias de energía (OEC)")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                   (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Connection": "keep-alive",
}

keywords = [ "energía", "transición energética", "transición sostenible", "renovables", "nextgeneration",
    "sostenibilidad", "electricidad", "calor", "potencia", "nuclear", "solar", "eólica",
    "hidroeléctrica", "eficiencia energética", "aerogenerador", "aerotermia", "fotovoltaico",
    "biomasa", "energía térmica", "energía eléctrica", "geotermia", "almacenamiento hidroeléctrico",
    "almacenamiento térmico", "emisiones", "carbono", "descarbonización", "gases", "invernadero",
    "instalaciones", "energía verde", "fuentes de energía", "autoconsumo", "placas solares",
    "vehículos eléctricos", "vehículos híbridos", "Mariano Hernández Zapata", "Zapata", "Mariano H. Zapata" ]

exclusion_keywords = [ "subvención", "ayuda", "guerra", "militar", "ejército", "misil", "bomba", "ataque",
    "conflicto", "israel", "palestina", "irán", "ucrania", "rusia", "otan", "norte corea", "nuclear militar",
    "armamento", "defensa", "netanyahu", "trump", "putin", "hamás", "hezbolá", "suministro", "impacto", "fuentes" ]

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
    except Exception:
        return []

def extraer_noticias():
    medios = [
        ("EnergyNews", "https://www.energynews.es/", "article h2.entry-title a", None),
        ("EFEVerde", "https://efeverde.com/energia/", "article h2 a", None),
        ("El Periódico de la Energía", "https://elperiodicodelaenergia.com/renovables", "h3.entry-title a", None),
        ("Energías Renovables", "https://www.energias-renovables.com/", "div.enrTitularNoticia a", "https://www.energias-renovables.com"),
        ("Review Energy", "https://www.review-energy.com/", "div.card-title a", None),
        ("Diario de la Energía", "https://www.diariodelaenergia.com/", "h3.entry-title a", None),
        ("El Día", "https://www.eldia.es/tags/ayudas/", "article h3 a", "https://www.eldia.es/tags/ayudas/"),
        ("Diario de Avisos", "https://diariodeavisos.elespanol.com/economia/", "h2.entry-title a", None),
        ("El País", "https://elpais.com/noticias/energias-renovables/", "h2.c_t a", "https://elpais.com/noticias/energias-renovables/"),
        ("El Mundo", "https://www.elmundo.es/economia.html", "h2.ue-c-cover-content__headline a", "https://www.elmundo.es/economia.html"),
        ("La Vanguardia", "https://www.lavanguardia.com/natural/energia", "h2 a", "https://www.lavanguardia.com/natural/energia"),
        ("ABC", "https://www.abc.es/noticias/energias-renovables/", "h2 a", "https://www.abc.es/noticias/energias-renovables/"),
        ("EFE", "https://efe.com/noticias/renovables/", "article h3 a", "https://efe.com/noticias/renovables/"),
        ("Europa Press", "https://www.europapress.es/", "div.noticiacuerpo h2 a", "https://www.europapress.es"),
        ("La Razón", "https://www.larazon.es/tags/renovables/", "h2.title-news a", "https://www.larazon.es/tags/renovables/"),
        ("El Español", "https://www.elespanol.com/temas/energias_renovables/", "article h2 a", "https://www.elespanol.com/temas/energias_renovables/"),
        ("Cadena SER Canarias", "https://cadenaser.com/ccaa/canarias/", "article h2 a", "https://cadenaser.com"),
        ("Euronews UE", "https://es.euronews.com/tag/union-europea", "main a", "https://es.euronews.com"),
        ("EnergiaParaElCambio", "https://energiaparaelcambio.com/", "main a", "https://energiaparaelcambio.com"),
    ]

    news = []
    total = len(medios)
    progress = st.progress(0)
    status = st.empty()
    log_area = st.empty()  # <- mostrará el log
    log_messages = []      # <- acumula mensajes
    start_time = datetime.now()

    for i, (nombre, url, selector, base_url) in enumerate(medios, start=1):
        status.markdown(f"🔎 Buscando en **{nombre}**… ({i}/{total})")
        try:
            resultado = run_scraper(nombre, url, selector, base_url)
            news += resultado
            msg = f"✅ {nombre}: {len(resultado)} noticias"
        except Exception as e:
            msg = f"❌ {nombre}: ERROR ({e})"
        log_messages.append(msg)
        log_area.markdown("**LOG:**\n" + "\n".join(log_messages))
        print(msg)  # también lo manda a la consola
        progress.progress(int(i * 100 / total))

    status.empty()
    progress.empty()
    elapsed = (datetime.now() - start_time).total_seconds()
    st.caption(f"⌛ Búsqueda completada en {elapsed:.1f} s")

    return pd.DataFrame(news)

# INTERFAZ STREAMLIT
if st.button("🔍 Buscar noticias"):
    df = extraer_noticias()

    if df.empty:
        st.warning("🚫 No se encontraron noticias relevantes.")
    else:
        st.success(f"✅ Se encontraron {len(df)} noticias relevantes.")
        st.write("### Noticias encontradas:")

        for _, row in df.iterrows():
            st.markdown(f"""
            <div style="border:1px solid #DDD; border-radius:8px; padding:10px 15px; margin-bottom:10px;">
                <p style="margin:0; font-size:14px; color:#888;">📰 <strong>{row['medio']}</strong></p>
                <p style="margin:4px 0;">
                    <a href="{row['url']}" target="_blank" style="font-size:16px; color:#0066cc; text-decoration:none;">
                        {row['título']}
                    </a>
                </p>
                <p style="margin:0; font-size:13px; color:#555;">📅 {row['fecha_extraccion']}</p>
            </div>
            """, unsafe_allow_html=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", csv, f"noticias_energia_{datetime.now().date()}.csv", "text/csv")
