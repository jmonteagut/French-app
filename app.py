import streamlit as st
from openai import OpenAI
import random
import time
import re
import json # <--- NUEVO: Para guardar el progreso
import os   # <--- NUEVO: Para comprobar si existe el archivo de guardado

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
    if dia <= 7:
        formato_idioma = "FORMATO OBLIGATORIO: Frase en Francés (Traducción en Español)."
    elif dia <= 14:
        formato_idioma = "Habla en francés. Usa español solo para aclarar dudas."
    else:
        formato_idioma = "Solo francés."

    base = f"Eres Kai. SITUACIÓN ACTUAL: '{fase}'. {formato_idioma}"

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
    """Guarda todas las variables de la sesión en un archivo local"""
    datos = {
        "dia_actual": st.session_state.dia_actual,
        "mensajes": st.session_state.mensajes,
        "vocabulario_dia": st.session_state.vocabulario_dia,
        "modo_app": st.session_state.modo_app,
        "examen_tipo": st.session_state.examen_tipo,
        "examen_data": st.session_state.examen_data,
        "examen_respuestas": st.session_state.examen_respuestas,
        "examen_progreso": st.session_state.examen_progreso,
        "nota_final": st.session_state.nota_final
    }
    with open(ARCHIVO_PROGRESO, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def cargar_progreso():
    """Carga los datos si el archivo existe"""
    if os.path.exists(ARCHIVO_PROGRESO):
        with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# --- 6. GESTIÓN DE ESTADO E INICIALIZACIÓN ---
if 'iniciado' not in st.session_state:
    datos_guardados = cargar_progreso()
    
    if datos_guardados:
        # Si hay partida guardada, restauramos todo
        for key, value in datos_guardados.items():
            st.session_state[key] = value
    else:
        # Si es la primera vez, valores por defecto
        st.session_state.dia_actual = 1
        st.session_state.mensajes = []
        st.session_state.vocabulario_dia = None
        st.session_state.modo_app = "practica"
        st.session_state.examen_tipo = None 
        st.session_state.examen_data = [] 
        st.session_state.examen_respuestas = [] 
        st.session_state.examen_progreso = 0
        st.session_state.nota_final = None
        
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

    # Ahora reiniciar borra el archivo de guardado
    if st.button("🔄 Borrar Partida y Reiniciar"):
        if os.path.exists(ARCHIVO_PROGRESO):
            os.remove(ARCHIVO_PROGRESO)
        for key in ["mensajes", "vocabulario_dia", "examen_tipo", "examen_data", "examen_respuestas", "nota_final"]:
            st.session_state[key] = None if key in ["vocabulario_dia", "examen_tipo", "nota_final"] else []
        st.session_state.dia_actual = 1
        st.session_state.modo_app = "practica"
        st.session_state.examen_progreso = 0
        st.rerun()

# --- 8. INTERFAZ ---
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
            guardar_progreso() # Guardamos tras la generación inicial

with st.expander(f"📚 Vocabulario: {fase}", expanded=True):
    st.markdown(f'<div class="vocab-card">{st.session_state.vocabulario_dia}</div>', unsafe_allow_html=True)

st.divider()

# B) CHAT
for msg in st.session_state.mensajes:
    avatar = "🧢" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# --- 9. ZONA DE ACCIÓN ---

# EXAMEN ACTIVO
if st.session_state.modo_app == "examen_activo":
    tipo = st.session_state.examen_tipo
    prog = st.session_state.examen_progreso
    label = f"🎭 SIMULACIÓN ({prog+1}/3)" if tipo == "roleplay" else f"📝 PREGUNTA ({prog+1}/3)"
    
    if resp := st.chat_input(label):
        st.session_state.mensajes.append({"role": "user", "content": resp})
        st.session_state.examen_respuestas.append(resp)
        st.session_state.examen_progreso += 1
        
        if st.session_state.examen_progreso >= 3:
            st.session_state.modo_app = "examen_finalizado"
            guardar_progreso()
            st.rerun()
        else:
            if tipo == "roleplay":
                p_sys = get_system_prompt(dia, fase, "examen_roleplay_activo")
                ctx = st.session_state.mensajes[-3:]
                ia_msg = consultar_kai([{"role": "system", "content": p_sys}] + ctx)
                st.session_state.mensajes.append({"role": "assistant", "content": ia_msg})
            else:
                next_q = st.session_state.examen_data[st.session_state.examen_progreso]
                st.session_state.mensajes.append({"role": "assistant", "content": f"➡️ {next_q}"})
            guardar_progreso()
            st.rerun()

# CORRECCIÓN
elif st.session_state.modo_app == "examen_finalizado":
    
    if len(st.session_state.mensajes) > 0 and "RESULTADO" not in st.session_state.mensajes[-1]["content"]:
        with st.spinner("Evaluando..."):
            log = "\n".join([f"R{i+1}: {r}" for i, r in enumerate(st.session_state.examen_respuestas)])
            p_sys






























