


import streamlit as st
from openai import OpenAI
import time

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(
    page_title="unmute.",
    page_icon="⚡", # Icono de rayo, más energético
    layout="wide"
)

# --- ESTILOS CSS "VIVOS" (LIVELY MODE) ---
st.markdown("""
<style>
    /* 1. AJUSTE ESPACIO SUPERIOR */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* 2. NUEVO: TÍTULO CON DEGRADADO (GRADIENT TEXT) */
    .gradient-text {
        background: linear-gradient(45deg, #FF5F6D, #FFC371); /* De rosa a naranja */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900; /* Muy negrita */
        font-size: 3rem;
        margin: 0;
        padding: 0;
        line-height: 1.1;
    }
    
    /* 3. BOTONES MÁS MODERNOS */
    .stButton>button { 
        width: 100%; 
        border-radius: 12px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease; /* Animación suave al pasar el ratón */
    }
    .stButton>button:hover {
        transform: translateY(-2px); /* Pequeño salto al pasar el ratón */
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* 4. NUEVO: TARJETAS FLOTANTES (LIVELY CARDS) */
    /* Reemplaza a la antigua clase .highlight */
    .lively-card {
        background-color: #ffffff; /* Fondo blanco limpio */
        padding: 25px; 
        border-radius: 20px; /* Bordes muy redondeados */
        box-shadow: 0 8px 20px rgba(0,0,0,0.08); /* Sombra suave para dar profundidad */
        border: 1px solid #f0f0f0;
        margin-bottom: 20px;
    }
    
    /* 5. ÁREA DE ESCRITURA (Mantenemos tu azul, pero más integrado) */
    .stChatInput textarea {
        background-color: #E3F2FD !important; /* Azul un poco más claro y fresco */
        color: #1565C0 !important; /* Texto azul oscuro */
        border: 2px solid #BBDEFB !important; 
        border-radius: 15px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stChatInput button {
        color: #FF5F6D !important; /* Botón de enviar en color acento rosa */
    }
    
    /* 6. MENÚS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: visible !important;} 
    [data-testid="stHeader"] {background-color: rgba(0,0,0,0);}
    
    /* 7. SIDEBAR MÁS LIMPIA */
    [data-testid="stSidebar"] {
        background-color: #FAFAFA; /* Gris muy claro */
        border-right: 1px solid #E0E0E0;
    }

</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN IA ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("⚠️ Falta la API Key en los secretos.")
    st.stop()

def consultar_ia(system_prompt, user_prompt):
    try:
        with st.spinner("🧠 Pensando..."): # Spinner genérico
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- LÓGICA DINÁMICA ---
def obtener_prompt(tipo, fase, idioma_objetivo):
    idioma_base = "Español"
    base = f"Eres un tutor experto de {idioma_objetivo} para hispanohablantes. Metodología ágil, moderna y práctica."
    
    if tipo == "vocab":
        return f"{base} Genera 5 palabras/frases de ALTA FRECUENCIA para la {fase}. No uses formato tabla. Usa formato de lista con emojis: '🔹 **Palabra ({idioma_objetivo})** / Pronunciación figurada / Significado ({idioma_base}) - *Ejemplo corto*'."
    elif tipo == "drill":
        return f"{base} Actúa como un nativo joven. Haz una pregunta corta, directa y natural en {idioma_objetivo} sobre: {fase}."
    elif tipo == "roleplay":
        return f"{base} Inicia una simulación breve en {idioma_objetivo}. Situación: {fase}. Eres el otro personaje. Empieza tú."
    return base

# --- INTERFAZ PRINCIPAL VIVA ---

# 1. HEADER NUEVO CON DEGRADADO
col1, col2 = st.columns([1, 7])
with col1:
    # Usamos un emoji gigante en lugar de imagen por ahora, queda más pop
    st.markdown("<div style='font-size: 4rem; text-align: center;'>⚡</div>", unsafe_allow_html=True)
with col2:
    # Aplicamos la clase de texto con degradado
    st.markdown('<h1 class="gradient-text">unmute.</h1>', unsafe_allow_html=True)
    st.markdown("<p style='margin-top: -10px; font-size: 1.1rem; color: gray;'>Speak first. Study later.</p>", unsafe_allow_html=True)

st.divider()

# 2. SIDEBAR (CONTROLES)
with st.sidebar:
    st.header("⚙️ Configuración")
    idioma = st.selectbox("Idioma Objetivo", ["Francés 🇫🇷", "Inglés 🇬🇧", "Italiano 🇮🇹", "Alemán 🇩🇪", "Japonés 🇯🇵"])
    st.divider()
    
    if 'dia_actual' not in st.session_state: st.session_state.dia_actual = 1
    if 'day_completed' not in st.session_state: st.session_state.day_completed = False

    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ Anterior"):
            if st.session_state.dia_actual > 1:
                st.session_state.dia_actual -= 1
                st.rerun()
    with col_next:
        bloqueado = not st.session_state.day_completed
        if st.button("Siguiente ➡️", disabled=bloqueado, type="primary" if not bloqueado else "secondary"):
            if st.session_state.dia_actual < 30:
                st.session_state.dia_actual += 1
                st.session_state.day_completed = False
                st.rerun()
    
    if not st.session_state.day_completed:
        st.caption("🔒 Completa la lección para avanzar.")
    else:
        st.success("✨ ¡Nivel desbloqueado!")

    dia = st.session_state.dia_actual
    st.write(f"### 📆 Día {dia} / 30")
    progreso = dia / 30
    # Color de la barra de progreso personalizado (Naranja vibrante)
    st.markdown(
        """
        <style>
            .stProgress > div > div > div > div {
                background-color: #FFC371;
                background-image: linear-gradient(315deg, #FFC371 0%, #FF5F6D 74%);
            }
        </style>""",
        unsafe_allow_html=True,
    )
    st.progress(progreso)

    if dia <= 7: fase, icono_fase = "Supervivencia Básica", "🆘"
    elif dia <= 14: fase, icono_fase = "Conexión Social", "🤝"
    elif dia <= 21: fase, icono_fase = "Resolución de Problemas", "🧩"
    else: fase, icono_fase = "Fluidez y Opinión", "🗣️"
    st.info(f"{icono_fase} **{fase}**")

# 3. PESTAÑAS PRINCIPALES
tab1, tab2, tab3 = st.tabs(["📚 Vocabulario", "⚡ Drills Rápidos", "🎭 Roleplay"])

# --- TAB 1: VOCABULARIO (Usando las nuevas tarjetas) ---
with tab1:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader(f"Lección del Día {dia}")
        st.write(f"Objetivo: Dominar el vocabulario de **{fase}**.")
    with col_b:
        if st.button("✨ Generar Lección", type="primary", use_container_width=True):
            sys_p = obtener_prompt("vocab", fase, idioma)
            resultado = consultar_ia(sys_p, f"Genera material para día {dia}.")
            st.session_state['vocab_result'] = resultado
    
    if 'vocab_result' in st.session_state:
        # AQUI USAMOS LA NUEVA CLASE .lively-card
        st.markdown(f'<div class="lively-card">{st.session_state["vocab_result"]}</div>', unsafe_allow_html=True)

# --- TAB 2: DRILLS ---
with tab2:
    st.subheader("Entrenador Personal")
    if "mensajes_drill" not in st.session_state: st.session_state.mensajes_drill = []

    col_reset, _ = st.columns([1, 3])
    with col_reset:
        if st.button("🔄 Nueva Pregunta"):
            sys_p = obtener_prompt("drill", fase, idioma)
            q = consultar_ia(sys_p, "Empieza.")
            st.session_state.mensajes_drill = [{"role": "assistant", "content": q}]

    chat_container = st.container(height=300)
    with chat_container:
        for msg in st.session_state.mensajes_drill:
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

    if prompt := st.chat_input(f"Responde en {idioma}..."):
        st.session_state.mensajes_drill.append({"role": "user", "content": prompt})
        with chat_container:
            st.chat_message("user", avatar="👤").write(prompt)
            sys_p = obtener_prompt("drill", fase, idioma)
            contexto = str(st.session_state.mensajes_drill[-3:])
            resp = consultar_ia(sys_p, f"Usuario: '{prompt}'. Contexto: {contexto}. Corrige y sigue.")
            st.session_state.mensajes_drill.append({"role": "assistant", "content": resp})
            st.chat_message("assistant", avatar="🤖").write(resp)

# --- TAB 3: ROLEPLAY ---
with tab3:
    st.subheader("Simulador de Inmersión")
    col_x, col_y = st.columns(2)
    with col_x:
        escenario = st.selectbox("Situación:", ["Cafetería/Bar", "Tienda de ropa", "Perdido en la calle", "Conociendo gente", "Entrevista de trabajo"])
    with col_y:
        st.write("")
        st.write("")
        start_rp = st.button("🎬 ¡Acción!", type="primary", use_container_width=True)

    if start_rp:
        sys_p = obtener_prompt("roleplay", f"{fase} - {escenario}", idioma)
        intro = consultar_ia(sys_p, "Empieza.")
        # Usamos una tarjeta viva para el escenario
        st.markdown(f"""
        <div class="lively-card" style="border-left: 5px solid #FF5F6D;">
            <h4>📍 Escenario: {escenario}</h4>
            <p>{intro}</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 Tip: Responde en tu mente o en voz alta. ¡Actúa!")

# --- FOOTER ---
st.divider()
if not st.session_state.day_completed:
    st.write("### ¿Terminaste por hoy?")
    # Botón grande con gradiente (truco CSS en el style del principio)
    if st.button("🎉 Marcar Lección como Completada", type="primary", use_container_width=True):
        st.session_state.day_completed = True
        st.balloons()
        time.sleep(1)
        st.rerun()
else:
    st.markdown('<div class="lively-card" style="text-align: center; background-color: #E8F5E9; border: none;">✅ <b>¡Lección completada!</b> Vuelve mañana para más.</div>', unsafe_allow_html=True)












