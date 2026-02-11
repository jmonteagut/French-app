import streamlit as st
from openai import OpenAI
import random
import time
import re

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="unmute.", page_icon="⚡", layout="centered")

# --- 2. ESTILOS ---
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    .gradient-text {
        background: linear-gradient(45deg, #FF5F6D, #FFC371);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 2.5rem; margin: 0;
    }
    .vocab-card {
        background-color: #F8F9FA; border-left: 5px solid #FF5F6D;
        padding: 15px; border-radius: 12px; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stChatMessage { padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; }
    .stChatInput textarea { border: 2px solid #FFC371 !important; border-radius: 15px; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN IA ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Error: Configura tu API Key en los secrets.")
    st.stop()

def consultar_kai(mensajes, temperatura=0.7):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=mensajes, temperature=temperatura
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- 4. CEREBRO DE KAI (MODO BILINGÜE ADAPTATIVO) ---
def get_system_prompt(dia, fase, modo="practica", contexto_extra=""):
    
    # REGLAS DE IDIOMA SEGÚN DÍA
    if dia <= 7:
        # Días 1-7: MODO ESPEJO (Francés + Traducción)
        instruccion_idioma = """
        ERES UN TUTOR PARA PRINCIPIANTES ABSOLUTOS.
        TU REGLA DE ORO: Cada vez que hables en francés, debes poner la traducción o el significado en español entre paréntesis inmediatamente después.
        Ejemplo: "Bonjour! (¡Hola!) Qu'est-ce que tu veux? (¿Qué quieres?)".
        Esto es vital para que el usuario no se pierda.
        """
    elif dia <= 14:
        # Días 8-14: MODO HÍBRIDO
        instruccion_idioma = "Habla en francés sencillo. Usa el español solo si explicas algo complejo o corriges un error grave."
    else:
        # Días 15+: INMERSIÓN
        instruccion_idioma = "Habla solo en francés. El usuario ya sabe defenderse."

    base = f"""Eres Kai, un tutor de francés paciente y motivador. 
    Contexto: '{fase}'.
    {instruccion_idioma}"""

    if modo == "vocab":
        return f"{base} Genera 5 palabras/frases clave en FRANCÉS para esta situación. Formato: Emoji **Palabra** (Pronunciación) - Traducción."

    elif modo == "inicio_activo":
        return f"""{base}
        INSTRUCCIÓN:
        1. Inicia la simulación del rol '{fase}'.
        2. Haz una pregunta en francés para empezar.
        3. IMPORTANTE: Como es principiante, traduce tu pregunta al español entre paréntesis."""

    elif modo == "practica":
        return f"""{base}
        INSTRUCCIONES DE CHAT:
        1. Mantén la conversación en el rol.
        2. Si el usuario responde en español, traduce mentalmente y síguele el juego en Francés (con su traducción al lado si es el día 1-7).
        3. CORRECCIÓN AMABLE: Si se equivoca, repite su frase corregida de forma natural.
        NO des lecciones de gramática. Solo conversa."""

    # EXÁMENES
    elif modo == "examen_generador":
        if contexto_extra == "traduccion": return f"Dame 3 frases en ESPAÑOL sencillas sobre '{fase}' para que el usuario las traduzca."
        elif contexto_extra == "quiz": return f"3 preguntas muy sencillas en Francés sobre '{fase}'. (Incluye traducción de la pregunta)."
        elif contexto_extra == "roleplay": return f"Inicia un roleplay básico sobre '{fase}'. Di tu primera frase (con traducción)."

    elif modo == "examen_roleplay_activo": return f"Roleplay de examen. No ayudes demasiado, pero sé claro."

    elif modo == "corrector_final":
        return f"""Eres un examinador amable.
        Formato:
        NOTA: [0-10]/10
        FEEDBACK: [Resumen en español de qué tal lo hizo]
        TIPS: [2 consejos en español para mejorar]"""

# --- 5. GESTIÓN DE ESTADO ---
if 'dia_actual' not in st.session_state: st.session_state.dia_actual = 1
if 'mensajes' not in st.session_state: st.session_state.mensajes = []
if 'vocabulario_dia' not in st.session_state: st.session_state.vocabulario_dia = None
if 'modo_app' not in st.session_state: st.session_state.modo_app = "practica"
# Examen
if 'examen_tipo' not in st.session_state: st.session_state.examen_tipo = None 
if 'examen_data' not in st.session_state: st.session_state.examen_data = [] 
if 'examen_respuestas' not in st.session_state: st.session_state.examen_respuestas = [] 
if 'examen_progreso' not in st.session_state: st.session_state.examen_progreso = 0
if 'nota_final' not in st.session_state: st.session_state.nota_final = None

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("
























