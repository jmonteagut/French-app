import streamlit as st
from openai import OpenAI
import random
import time
import re
import json 
import os   

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="unmute.", page_icon="⚡", layout="centered")

# --- 2. ESTILOS ---
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 8rem; }
    .gradient-text {
        background: linear-gradient(45deg, #FF5F6D, #FFC371);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 2.5rem; margin: 0;
    }
    .vocab-card {
        background-color: #F8F9FA; border-left: 5px solid #FF5F6D;
        padding: 15px; border-radius: 12px; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #000000 !important; 
    }
    .vocab-card strong { color: #000000 !important; }
    .stChatMessage { padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem; }
    [data-testid="stChatInput"] { padding-bottom: 4rem !important; background-color: transparent !important; }
    .stChatInput textarea { border: 2px solid #FFC371 !important; border-radius: 15px; }
    #MainMenu, footer, header, [data-testid="stToolbar"] {visibility: hidden;}
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
    
    perfil = ""
    if st.session_state.nombre_usuario:
        perfil += f" Se llama {st.session_state.nombre_usuario}."
    if st.session_state.intereses_usuario:
        perfil += f" Le gusta: {st.session_state.intereses_usuario}."
        
    instruccion_perfil = f"\nINFO DEL ALUMNO:{perfil} Úsalo sutilmente para personalizar la charla o los ejemplos si cuadra." if perfil else ""

    if dia <= 7:
        formato_idioma = "FORMATO OBLIGATORIO: Frase en Francés (Traducción en Español)."
    elif dia <= 14:
        formato_idioma = "Habla en francés. Usa español solo para aclarar dudas."
    else:
        formato_idioma = "Solo francés."

    base = f"Eres Kai. SITUACIÓN ACTUAL: '{fase}'. {formato_idioma} {instruccion_perfil}"

    if modo == "vocab":
        instruccion_extra = "IMPORTANTE: Incluye 'S'il vous plaît', 'Merci' y 'Je voudrais...'." if dia <= 7 else ""
        return f"{base} Genera 5 frases clave en FRANCÉS para esta situación. {instruccion_extra} Formato: Emoji Palabra (Pronunciación) - Traducción."

    elif modo == "inicio_activo":
        if dia == 1:
            return f"""{base}
            ¡PRIMER DÍA!
            1. PRESENTACIÓN (En Español): Preséntate. Di que esto es un programa de 30 días de Roleplay Activo.
            2. TRANSICIÓN (En Español): "Hoy empezamos en una cafetería. ¡Vamos allá!".
            3. ACCIÓN (En Francés + Español): Entra en el rol de Camarero y haz la primera pregunta.
            """
        else:
            return f"{base} 1. CONTEXTO (En Español): Explica la situación. 2. ACCIÓN (En Francés): Cambia de línea, entra en tu rol y lanza tu primera pregunta."

    elif modo == "practica":
        return f"{base} TU ROL: Eres un ACTOR. 1. PROHIBIDO REPETIR lo que dice el usuario. 2. Responde a lo que te pide. 3. CORRECCIÓN INVISIBLE: Si se equivoca, usa la forma correcta en tu respuesta."

    # --- NUEVO: MODO PISTA ---
    elif modo == "pista":
        return f"""{base}
        El usuario se ha quedado en blanco y te ha pedido una pista. 
        Sal de tu personaje un momento.
        ACTÚA COMO UN TUTOR DE APOYO EN ESPAÑOL.
        Analiza la conversación y dale 2 opciones sencillas de lo que podría decir a continuación en francés (con su traducción).
        Sé muy breve y motivador."""

    elif modo == "examen_generador":
        sep = "Separa cada ítem con '|||'. NO uses guiones."
        if contexto_extra == "traduccion": return f"3 frases en ESPAÑOL sobre '{fase}' para traducir. {sep}"
        elif contexto_extra == "quiz": return f"3 preguntas test en FRANCÉS sobre '{fase}' (con traducción). {sep}"
        elif contexto_extra == "roleplay": return f"Inicia un roleplay sobre '{fase}'. Tu primera frase en FRANCÉS (con traducción)."

    elif modo == "examen_roleplay_activo": return f"Roleplay examen. Actúa y responde. No ayudes."
    elif modo == "corrector_final": return f"Evalúa. Formato: NOTA: [0-10]/10. FEEDBACK: [Resumen español]. TIPS: [Consejos]."

# --- 5. SISTEMA DE GUARDADO (MEMORIA) ---
ARCHIVO_PROGRESO = "progreso_kai.json"

def guardar_progreso():
    datos = {
        "dia_actual": st.session_state.dia_actual,
        "mensajes": st.session_state.mensajes,
        "vocabulario_dia": st.session_state.vocabulario_dia,
        "modo_app": st.session_state.modo_app,
        "examen_tipo": st.session_state.examen_tipo,
        "examen_data": st.session_state.examen_data,
        "examen_respuestas": st.session_state.examen_respuestas,
        "examen_progreso": st.session_state.examen_progreso,
        "nota_final": st.session_state.nota_final,
        "nombre_usuario": st.session_state.nombre_usuario,
        "intereses_usuario": st.session_state.intereses_usuario,
        "pistas_usadas": st.session_state.pistas_usadas # <--- GUARDAMOS LAS PISTAS GASTADAS
    }
    with open(ARCHIVO_PROGRESO, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def cargar_progreso():
    if os.path.exists(ARCHIVO_PROGRESO):
        with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# --- 6. GESTIÓN DE ESTADO E INICIALIZACIÓN ---
if 'iniciado' not in st.session_state:
    datos_guardados = cargar_progreso()
    
    if datos_guardados:
        for key, value in datos_guardados.items():
            st.session_state[key] = value
    else:
        st.session_state.dia_actual = 1
        st.session_state.mensajes = []
        st.session_state.vocabulario_dia = None
        st.session_state.modo_app = "practica"
        st.session_state.examen_tipo = None 
        st.session_state.examen_data = [] 
        st.session_state.examen_respuestas = [] 
        st.session_state.examen_progreso = 0
        st.session_state.nota_final = None
        st.session_state.nombre_usuario = ""
        st.session_state.intereses_usuario = ""
        st.session_state.pistas_usadas = 0 # <--- NUEVA VARIABLE PARA EL CONTADOR
        
    st.session_state.iniciado = True

# --- 7. SIDEBAR Y FASES ---
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

    st.divider()

    with st.expander("👤 Tu Perfil (Opcional)", expanded=False):
        st.caption("Kai usará esto para personalizar tus clases.")
        st.text_input("Tu nombre:", key="nombre_usuario", on_change=guardar_progreso)
        st.text_input("Tus hobbies (ej: cine, deportes):", key="intereses_usuario", on_change=guardar_progreso)
    
    st.divider()

    if st.button("🔄 Borrar Partida y Reiniciar"):
        if os.path.exists(ARCHIVO_PROGRESO):
            os.remove(ARCHIVO_PROGRESO)
        for key in ["mensajes", "vocabulario_dia", "examen_tipo", "examen_data", "examen_respuestas", "nota_final"]:
            st.session_state[key] = None if key in ["vocabulario_dia", "examen_tipo", "nota_final"] else []
        st.session_state.dia_actual = 1
        st.session_state.modo_app = "practica"
        st.session_state.examen_progreso = 0
        st.session_state.pistas_usadas = 0 # Reiniciamos las pistas
        st.rerun()

# --- 8. INTERFAZ ---
st.markdown('<h1 class="gradient-text">unmute.</h1>', unsafe_allow_html=True)

# A) INICIO
if not st.session_































