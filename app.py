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

# --- 4. CEREBRO DE KAI (MODO ESTRICTO FRANCÉS) ---
def get_system_prompt(dia, fase, modo="practica", contexto_extra=""):
    
    # REGLAS DE IDIOMA BLINDADAS
    if dia <= 7:
        regla_idioma = "IDIOMA PRINCIPAL: FRANCÉS. (Usa español entre paréntesis SOLO para traducir palabras difíciles)."
    elif dia <= 14:
        regla_idioma = "IDIOMA PRINCIPAL: FRANCÉS. (Evita el español al máximo)."
    else:
        regla_idioma = "IDIOMA PRINCIPAL: FRANCÉS EXCLUSIVO."

    base = f"""Eres Kai, un tutor nativo de francés. 
    ESTRICTO: {regla_idioma}
    Tu objetivo es simular una situación real de: '{fase}'."""

    if modo == "vocab":
        return f"{base} Genera 5 palabras/frases clave en FRANCÉS para esta situación. Formato: Emoji Palabra (Pronunciación) - Traducción."

    elif modo == "inicio_activo":
        return f"""{base}
        INSTRUCCIÓN: Inicia la simulación DIRECTAMENTE EN FRANCÉS.
        Usa el vocabulario del día.
        Haz una pregunta corta en FRANCÉS al usuario (como si fueras el camarero, amigo, etc).
        NO HABLES EN ESPAÑOL AHORA."""

    elif modo == "practica":
        return f"""{base}
        INSTRUCCIONES DE INTERACCIÓN:
        1. Responde SIEMPRE en FRANCÉS. Si el usuario te habla en español, respóndele en francés (puedes añadir la traducción pequeña entre paréntesis).
        2. Mantén el rol (camarero, amigo, etc).
        3. CORRECCIÓN SILENCIOSA: Si el usuario comete un error, repite su frase corregida dentro de tu respuesta natural, sin decir "te has equivocado".
        Ejemplo: Usuario dice "Yo querer café". Tú respondes: "Ah, tu veux un café? (¿Quieres un café?) Très bien." """

    # EXÁMENES
    elif modo == "examen_generador":
        if contexto_extra == "traduccion": return f"Dame 3 frases en ESPAÑOL para que el usuario las traduzca al FRANCÉS. Sepáralas con guiones (-)."
        elif contexto_extra == "quiz": return f"3 preguntas tipo test en FRANCÉS sobre '{fase}'. Sepáralas con guiones (-)."
        elif contexto_extra == "roleplay": return f"Inicia un roleplay difícil en FRANCÉS sobre '{fase}'. Di solo tu primera frase."

    elif modo == "examen_roleplay_activo": return f"Roleplay en FRANCÉS puro. No ayudes."

    elif modo == "corrector_final":
        return f"""Eres un examinador. Formato:
        NOTA: [0-10]/10
        FEEDBACK: [Resumen en español]
        TIPS: [Consejos en español]"""

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

# --- 7. INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="gradient-text">unmute.</h1>', unsafe_allow_html=True)

# A) INICIO AUTOMÁTICO
if not st.session_state.vocabulario_dia:
    with st.spinner(f"Preparando inmersión en: {fase}..."):
        # 1. Vocab
        prompt_v = get_system_prompt(dia, fase, "vocab")
        vocab = consultar_kai([{"role": "system", "content": prompt_v}, {"role": "user", "content": "Generar"}])
        st.session_state.vocabulario_dia = vocab
        
        # 2. Inicio Activo (Forzando vocabulario)
        if len(st.session_state.mensajes) == 0:
            prompt_i = get_system_prompt(dia, fase, "inicio_activo")
            # Le pasamos el vocabulario generado explícitamente al prompt de inicio
            inicio = consultar_kai([
                {"role": "system", "content": prompt_i}, 
                {"role": "user", "content": f"Usa ESTE vocabulario para empezar: {vocab}"}
            ])
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
        st.session_state.examen_respuestas.append(resp)
        st.session_state.examen_progreso += 1
        
        if st.session_state.examen_progreso >= 3:
            st.session_state.modo_app = "examen_finalizado"
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
            st.rerun()

# CORRECCIÓN
elif st.session_state.modo_app == "examen_finalizado":
    
    if len(st.session_state.mensajes) > 0 and "RESULTADO" not in st.session_state.mensajes[-1]["content"]:
        with st.spinner("Evaluando..."):
            log = "\n".join([f"R{i+1}: {r}" for i, r in enumerate(st.session_state.examen_respuestas)])
            p_sys = get_system_prompt(dia, fase, "corrector_final")
            corr = consultar_kai([{"role": "system", "content": p_sys}, {"role": "user", "content": log}])
            
            st.session_state.mensajes.append({"role": "assistant", "content": f"📊 **RESULTADO:**\n\n{corr}"})
            
            match = re.search(r"NOTA:\s*(\d+)", corr)
            st.session_state.nota_final = int(match.group(1)) if match else 5
            st.rerun()

    nota = st.session_state.nota_final if st.session_state.nota_final is not None else 0
    
    if nota <= 5:
        st.error(f"Nota: {nota}/10. ¡Inténtalo de nuevo!")
        if st.button("🔄 REPETIR EXAMEN", type="primary"):
            st.session_state.modo_app = "practica"
            st.session_state.examen_respuestas = []
            st.session_state.examen_progreso = 0
            st.session_state.nota_final = None
            st.rerun()
            
    else:
        st.balloons()
        st.success(f"¡Aprobado: {nota}/10!")
        if st.button("🚀 SIGUIENTE DÍA", type="primary"):
            st.session_state.dia_actual += 1
            st.session_state.mensajes = []
            st.session_state.vocabulario_dia = None
            st.session_state.modo_app = "practica"
            st.session_state.nota_final = None
            st.rerun()

# PRÁCTICA
elif st.session_state.modo_app == "practica":
    if prompt := st.chat_input("Escribe en francés..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        
        # PROMPT DE RESPUESTA
        p_sys = get_system_prompt(dia, fase, "practica")
        hist = [{"role": "system", "content": p_sys}] + st.session_state.mensajes[-5:]
        
        with st.spinner("..."):
            resp = consultar_kai(hist)
        
        st.session_state.mensajes.append({"role": "assistant", "content": resp})
        st.rerun()

    if len(st.session_state.mensajes) >= 3:
        if st.button("🔥 EXAMEN", type="primary", use_container_width=True):
            tipo = random.choice(["traduccion", "quiz", "roleplay"])
            st.session_state.examen_tipo = tipo
            with st.spinner(f"Generando {tipo}..."):
                p_sys = get_system_prompt(dia, fase, "examen_generador", tipo)
                raw = consultar_kai([{"role": "system", "content": p_sys}, {"role": "user", "content": "Generar"}])
                
                if tipo == "roleplay":
                    st.session_state.examen_data = "roleplay"
                    msg = f"🎭 **ROLEPLAY**\n{raw}"
                else:
                    qs = [q.strip() for q in raw.split("-") if q.strip()]
                    if len(qs)<3: qs = ["P1", "P2", "P3"]
                    st.session_state.examen_data = qs
                    msg = f"📝 **QUIZ**\n1. {qs[0]}"

                st.session_state.modo_app = "examen_activo"
                st.session_state.examen_progreso = 0
                st.session_state.examen_respuestas = []
                st.session_state.nota_final = None
                st.session_state.mensajes.append({"role": "assistant", "content": msg})
                st.rerun()























