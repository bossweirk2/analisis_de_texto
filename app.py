# --- Parche de compatibilidad con googletrans y Python 3.12+ ---
import sys, types

cgi_mod = types.ModuleType("cgi")

def parse_header(value):
    """Emula la función eliminada en Python 3.11+ para googletrans."""
    parts = value.split(";")
    key = parts[0].strip().lower()
    pdict = {}
    for item in parts[1:]:
        if "=" in item:
            k, v = item.strip().split("=", 1)
            pdict[k.lower()] = v.strip()
    return key, pdict

cgi_mod.parse_header = parse_header
sys.modules["cgi"] = cgi_mod
# ---------------------------------------------------------------

import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Texto Simple",
    page_icon="📊",
    layout="wide"
)

# Título y descripción
st.title("📝 Analizador de Texto con TextBlob")
st.markdown("""
Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:
- Análisis de sentimiento y subjetividad  
- Extracción de palabras clave  
- Análisis de frecuencia de palabras
""")

# Barra lateral
st.sidebar.title("Opciones")
modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

# Función para contar palabras
def contar_palabras(texto):
    stop_words = set([
        # Español
        "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con", "contra",
        "cual", "cuando", "de", "del", "desde", "donde", "durante", "e", "el", "ella",
        "ellas", "ellos", "en", "entre", "era", "eras", "es", "esa", "esas", "ese",
        "eso", "esos", "esta", "estas", "este", "esto", "estos", "ha", "había", "han",
        "has", "hasta", "he", "la", "las", "le", "les", "lo", "los", "me", "mi", "mía",
        "mías", "mío", "míos", "mis", "mucho", "muchos", "muy", "nada", "ni", "no", "nos",
        "nosotras", "nosotros", "nuestra", "nuestras", "nuestro", "nuestros", "o", "os", 
        "otra", "otras", "otro", "otros", "para", "pero", "poco", "por", "porque", "que", 
        "quien", "quienes", "qué", "se", "sea", "sean", "según", "si", "sido", "sin", 
        "sobre", "sois", "somos", "son", "soy", "su", "sus", "suya", "suyas", "suyo", 
        "suyos", "también", "tanto", "te", "tenéis", "tenemos", "tener", "tengo", "ti", 
        "tiene", "tienen", "todo", "todos", "tu", "tus", "tuya", "tuyas", "tuyo", "tuyos", 
        "tú", "un", "una", "uno", "unos", "vosotras", "vosotros", "vuestra", "vuestras", 
        "vuestro", "vuestros", "y", "ya", "yo",
        # Inglés
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", 
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", 
        "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", 
        "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", 
        "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", 
        "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", 
        "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
        "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", 
        "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", 
        "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", 
        "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", 
        "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", 
        "the", "their", "theirs", "them", "themselves", "then", "there", "there's", 
        "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", 
        "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
        "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", 
        "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", 
        "why's", "with", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
        "your", "yours", "yourself", "yourselves"
    ])
    
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for p in palabras_filtradas:
        contador[p] = contador.get(p, 0) + 1
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    return contador_ordenado, palabras_filtradas

# Inicializar traductor
translator = Translator()

# Función de traducción
def traducir_texto(texto):
    try:
        traduccion = translator.translate(texto, src='es', dest='en')
        return traduccion.text
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

# Procesamiento del texto
def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    
    frases_originales = [f.strip() for f in re.split(r'[.!?]+', texto_original) if f.strip()]
    frases_traducidas = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]
    
    frases_combinadas = []
    for i in range(min(len(frases_originales), len(frases_traducidas))):
        frases_combinadas.append({
            "original": frases_originales[i],
            "traducido": frases_traducidas[i]
        })
    
    contador_palabras, palabras = contar_palabras(texto_ingles)
    
    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

# Visualizaciones
def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Análisis de Sentimiento y Subjetividad")
        sentimiento_norm = (resultados["sentimiento"] + 1) / 2
        st.write("**Sentimiento:**")
        st.progress(sentimiento_norm)
        
        if resultados["sentimiento"] > 0.05:
            st.success(f"📈 Positivo ({resultados['sentimiento']:.2f})")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"📉 Negativo ({resultados['sentimiento']:.2f})")
        else:
            st.info(f"📊 Neutral ({resultados['sentimiento']:.2f})")
        
        st.write("**Subjetividad:**")
        st.progress(resultados["subjetividad"])
        if resultados["subjetividad"] > 0.5:
            st.warning(f"💭 Alta subjetividad ({resultados['subjetividad']:.2f})")
        else:
            st.info(f"📋 Baja subjetividad ({resultados['subjetividad']:.2f})")
    
    with col2:
        st.subheader("Palabras más frecuentes")
        if resultados["contador_palabras"]:
            palabras_top = dict(list(resultados["contador_palabras"].items())[:10])
            st.bar_chart(palabras_top)
    
    st.subheader("Texto Traducido")
    with st.expander("Ver traducción completa"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Texto Original (Español):**")
            st.text(resultados["texto_original"])
        with col2:
            st.markdown("**Texto Traducido (Inglés):**")
            st.text(resultados["texto_traducido"])
    
    st.subheader("Frases detectadas")
    if resultados["frases"]:
        for i, f in enumerate(resultados["frases"][:10], 1):
            frase_original = f["original"]
            frase_traducida = f["traducido"]
            try:
                blob_frase = TextBlob(frase_traducida)
                s = blob_frase.sentiment.polarity
                if s > 0.05:
                    emoji = "😊"
                elif s < -0.05:
                    emoji = "😟"
                else:
                    emoji = "😐"
                st.write(f"{i}. {emoji} **Original:** *\"{frase_original}\"*")
                st.write(f"   **Traducción:** *\"{frase_traducida}\"* (Sentimiento: {s:.2f})")
                st.write("---")
            except:
                st.write(f"{i}. **Original:** *\"{frase_original}\"*")
                st.write(f"   **Traducción:** *\"{frase_traducida}\"*")
                st.write("---")
    else:
        st.write("No se detectaron frases.")

# Modo principal
if modo == "Texto directo":
    st.subheader("Ingresa tu texto para analizar")
    texto = st.text_area("", height=200, placeholder="Escribe o pega aquí el texto que deseas analizar...")
    if st.button("Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando texto..."):
                resultados = procesar_texto(texto)
                crear_visualizaciones(resultados)
        else:
            st.warning("Por favor, ingresa algún texto para analizar.")

elif modo == "Archivo de texto":
    st.subheader("Carga un archivo de texto")
    archivo = st.file_uploader("", type=["txt", "csv", "md"])
    if archivo is not None:
        try:
            contenido = archivo.getvalue().decode("utf-8")
            with st.expander("Ver contenido del archivo"):
                st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
            if st.button("Analizar archivo"):
                with st.spinner("Analizando archivo..."):
                    resultados = procesar_texto(contenido)
                    crear_visualizaciones(resultados)
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

with st.expander("📚 Información sobre el análisis"):
    st.markdown("""
    ### Sobre el análisis de texto
    - **Sentimiento**: Varía de -1 (muy negativo) a 1 (muy positivo)  
    - **Subjetividad**: Varía de 0 (muy objetivo) a 1 (muy subjetivo)
    """)

st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y TextBlob")
