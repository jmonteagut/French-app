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

# --- 4. CEREBRO DE KAI ---
def get_system_prompt(dia, fase, modo="practica", contexto_extra=""):
    
    # REGLAS DE IDIOMA
    if dia <= 7:
        instruccion_idioma = "Eres tutor de PRINCIPIANTES. Tu Regla de Oro: Cuando hables francés, pon la traducción al español justo al lado entre paréntesis. Ejemplo: 'Bonjour (Hola)'."
    elif dia <= 14:
        instruccion_idioma = "Habla francés sencillo. Usa español solo para emergencias."
    else:
        instruccion_idioma = "Solo francés."

    base = f"Eres Kai. Contexto: '{fase}'. {instruccion_idioma}"

    if modo == "vocab":
        # --- CAMBIO AQUÍ: OBLIGATORIEDAD DE CORTESÍA ---
        instruccion_extra = ""
        if dia <= 7:
            instruccion_extra = "IMPORTANTE: Incluye OBLIGATORIAMENTE fórmulas de cortesía (S'il vous plaît, Merci) y la estructura para pedir cosas (Je voudrais...) adaptadas al contexto."
        
        return f"{base} Dame 5 palabras/frases clave en Francés. {instruccion_extra} Formato: Emoji Palabra (Pronunciación) - Traducción."

    elif modo == "inicio_activo":
        return f"{base} Inicia la situación '{fase}' con una pregunta directa (traducida al español). No saludes genéricamente."

    elif modo == "practica":
        return f"{base} Mantén la charla. Si el usuario habla español, responde en francés (traducido). Corrige errores repitiendo la frase bien dicha."

    # --- ARREGLO DEL QUIZ (MANTENIDO) ---
    elif modo == "examen_generador":
        separator_instruction = "Separa cada pregunta/frase EXACTAMENTE con el símbolo '|||' (tres barras verticales). NO uses guiones ni números al principio."
        
        if contexto_extra == "traduccion": 
            return f"Dame 3 frases en ESPAÑOL sencillas sobre '{fase}' para traducir al francés. {separator_instruction}"
        
        elif contexto_extra == "quiz": 
            return f"Dame 3 preguntas tipo test cortas en Francés sobre '{fase}' (incluye traducción entre paréntesis). {separator_instruction}"
        
        elif contexto_extra == "roleplay": 
            return f"Inicia un roleplay sobre '{fase}'. Di solo tu primera frase (traducida)."

    elif modo == "examen_roleplay_activo": return f"Roleplay examen. No ayudes mucho."

    elif modo == "corrector_final":
        return f"Evalúa brevemente. Formato: NOTA: [0-10]/10. FEEDBACK: [Resumen]. TIPS: [Consejos]."

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
    st.header("🗺️ Ruta 30 Días")
    dia = st.session_state.dia_actual
    
    if dia == 1: fase = "Cafetería: Pedir y pagar"
    elif dia == 2: fase = "Transporte: Metro y Tickets"
    elif dia == 3: fase = "Supermercado: Básicos"
    elif dia == 4: fase = "Restaurante: Alergias"
    elif dia == 5: fase = "Calle: Direcciones"
    elif dia == 6: fase = "Farmacia: Dolor"
    elif dia == 7: fase = "Hotel: Check-in"
    elif dia <= 14: fase = "Social: Conocer gente"
    else: fase = "Vida Profesional"
    
    st.progress(dia / 30)
    st.caption(f"Día {dia}: {fase}")

    if st.button("🔄 Reiniciar Todo"):
        st.session_state.mensajes = []
        st.session_state.vocabulario_dia = None
        st.session_state.modo_app = "practica"
        st.session_state.nota_final = None
        st.rerun()

# --- 7. INTERFAZ ---
st.markdown('<h1 class="gradient-text">unmute.</h1>', unsafe_allow_html=True)

# A) INICIO
if not st.session_state.vocabulario_dia:
    with st.spinner(f"Preparando: {fase}..."):
        prompt_v = get_system_prompt(dia, fase, "vocab")
        vocab = consultar_kai([{"role": "system", "content": prompt_v}, {"role": "user", "content": "Generar"}])
        st.session_state.vocabulario_dia = vocab
        
        if len(st.session_state.mensajes) == 0:
            prompt_i = get_system_prompt(dia, fase, "inicio_activo")
            inicio = consultar_kai([{"role": "system", "content": prompt_i}, {"role": "user", "content": f"Vocabulario: {vocab}. Empieza."}])
            st.session_state.mensajes.append({"role": "assistant", "content": inicio})

with st.expander(f"📚 Vocabulario: {fase}", expanded=True):
    st.markdown(f'<div class="vocab-card">{st.session_state.vocabulario_dia}</div>', unsafe_allow_html=True)

st.divider()

# B) CHAT
for msg in st.session_state.mensajes:
    avatar = "🧢" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# --- 8. ZONA DE ACCIÓN ---

# EXAMEN ACTIVO
if st.session_state.modo_app == "examen_activo":
    tipo = st.session_state.examen_tipo
    prog = st.session_state.examen_progreso
    label = f"🎭 SIMULACIÓN ({prog+1}/3)" if tipo == "roleplay" else f"📝 PREGUNTA ({prog+1}/3)"
    
    if resp := st.chat_input(label):
        st.session_state.mensajes.append({"role": "user", "content": resp})
        st.session_state.examen_respuestas.


























