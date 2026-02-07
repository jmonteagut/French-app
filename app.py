import streamlit as st
from openai import OpenAI
import time

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(
    page_title="Unmute AI",
    page_icon="🌍",
    layout="wide"  # Usamos todo el ancho de la pantalla
)

# Estilos CSS personalizados: "Compact Mode"
st.markdown("""
<style>
    /* 1. Ajuste del espacio superior (Compact Mode) */
    .block-container {
        padding-top: 3rem !important; /* Le damos un poco más de aire para que quepa la flecha */
        padding-bottom: 0rem !important;
    }
    
    /* 2. Título compacto */
    h1 {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }
    
    /* 3. Botones redondeados */
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
    }
    
    /* 4. Cajas de texto de resultados */
    .highlight { 
        background-color: #f0f2f6; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #ff4b4b; 
    }
    
    /* 5. ÁREA DE ESCRITURA EN AZUL CIELO (Tu diseño) */
    .stChatInput textarea {
        background-color: #f0f2f6 !important; 
        color: #000000 !important;            
        border: 2px solid #5CA8FF !important; 
        border-radius: 15px !important;
    }
    
    /* Icono de enviar en azul oscuro */
    .stChatInput button {
        color: #004488 !important;
    }
    
    /* 6. ARREGLO DEL MENÚ: */
    /* Ocultamos el menú de opciones (tres puntos) y el footer... */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ...PERO DEJAMOS VISIBLE LA CABECERA para que puedas ver la flecha del menú */
    header {visibility: visible !important;} 
    
    /* Opcional: Hacemos la cabecera transparente para que no se vea una barra blanca fea */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
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

# --- LÓGICA DINÁMICA (AHORA CON IDIOMA) ---
def obtener_prompt(tipo, fase, idioma_objetivo):
    # Definimos el idioma base (tu idioma nativo)
    idioma_base = "Español"
    
    base = f"Eres un tutor experto de {idioma_objetivo} para hispanohablantes. Sigues la metodología 'Outcome-First'."
    
    if tipo == "vocab":
        return f"{base} Genera una tabla Markdown con 5 palabras/frases clave de 'Frequency-Core' para la {fase}. Columnas: {idioma_objetivo}, Pronunciación figurada, Significado en {idioma_base}, Ejemplo de uso."
    elif tipo == "drill":
        return f"{base} Actúa como un nativo. Haz una pregunta corta en {idioma_objetivo} sobre: {fase}. Espera respuesta. Luego corrige y mejora la frase."
    elif tipo == "roleplay":
        return f"{base} Inicia un roleplay breve en {idioma_objetivo}. Situación: {fase}. Tú empiezas."
    return base

# --- INTERFAZ PRINCIPAL ---

# 1. HEADER COMPACTO
col1, col2 = st.columns([1, 6]) # Hacemos la col2 más ancha para que el texto no salte de línea
with col1:
    # Logo un poco más pequeño (width=60 en vez de 80)
    st.image("https://cdn-icons-png.flaticon.com/512/3898/3898150.png", width=60)
with col2:
    # Usamos markdown en vez de title para controlar mejor el espaciado vertical
    st.markdown("""
    <h1 style='margin-bottom: 0px; margin-top: 0px;'>Unmute AI.</h1>
    <p style='margin-top: 0px; font-style: italic; color: gray;'>Speak first. Study later.🚀</p>
    """, unsafe_allow_html=True)

st.divider() # Línea divisoria fina

# 2. SIDEBAR (CONTROLES)
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # 1. Selector de Idioma
    idioma = st.selectbox("¿Qué quieres aprender?", ["Francés", "Inglés", "Italiano", "Alemán"])
    
    st.divider()
    
    # 2. LÓGICA DE PROGRESO
    if 'dia_actual' not in st.session_state:
        st.session_state.dia_actual = 1
    
    # Inicializamos el estado de "Lección Completada" si no existe
    if 'day_completed' not in st.session_state:
        st.session_state.day_completed = False

    # Botones de navegación
    col_prev, col_next = st.columns(2)
    
    with col_prev:
        if st.button("⬅️ Anterior"):
            if st.session_state.dia_actual > 1:
                st.session_state.dia_actual -= 1
                # (Opcional) Si vuelves atrás, ¿quieres que esté completado o no? 
                # De momento lo dejamos como estaba.
                st.rerun()

    with col_next:
        # EL TRUCO: El botón se desactiva (disabled) si 'day_completed' es False
        bloqueado = not st.session_state.day_completed
        if st.button("Siguiente ➡️", disabled=bloqueado):
            if st.session_state.dia_actual < 30:
                st.session_state.dia_actual += 1
                st.session_state.day_completed = False # ¡Reseteamos para el nuevo día!
                st.rerun()
    
    # Mensaje de estado (Candado)
    if not st.session_state.day_completed:
        st.caption("🔒 *Completa la lección para avanzar.*")
    else:
        st.success("🔓 *¡Nivel desbloqueado!*")

    # Barra de progreso
    dia = st.session_state.dia_actual
    st.write(f"### 📆 Día {dia} de 30")
    progreso = dia / 30
    st.progress(progreso)

    # ... (El resto del código de Fases igual que antes) ...
    if dia <= 7:
        fase = "Fase 1: Supervivencia"
        icono_fase = "🆘"
    elif dia <= 14:
        fase = "Fase 2: Conexión Social"
        icono_fase = "🤝"
    elif dia <= 21:
        fase = "Fase 3: Resolución"
        icono_fase = "🧩"
    else:
        fase = "Fase 4: Fluidez"
        icono_fase = "🗣️"
    
    st.info(f"{icono_fase} **{fase}**")

# 3. PESTAÑAS MEJORADAS
tab1, tab2, tab3 = st.tabs(["📚 Vocabulario Inteligente", "⚡ Drills de Conversación", "🎭 Simulador Real"])

# --- TAB 1: VOCABULARIO ---
with tab1:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader(f"Lección del Día {dia}: {idioma}")
        st.markdown(f"Aquí tienes el vocabulario esencial para dominar la **{fase}**.")
    with col_b:
        if st.button("✨ Generar Lección", type="primary"):
            with st.spinner(f"Analizando frecuencias de uso en {idioma}..."):
                sys_p = obtener_prompt("vocab", fase, idioma)
                resultado = consultar_ia(sys_p, f"Genera material para día {dia}.")
                st.session_state['vocab_result'] = resultado # Guardamos en memoria
    
    # Mostrar resultado si existe
    if 'vocab_result' in st.session_state:
        st.markdown('<div class="highlight">', unsafe_allow_html=True)
        st.markdown(st.session_state['vocab_result'])
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: DRILLS (CHAT) ---
with tab2:
    st.subheader("Entrenador Personal")
    
    if "mensajes_drill" not in st.session_state:
        st.session_state.mensajes_drill = []

    # Botón de reinicio más limpio
    col_reset, _ = st.columns([1, 4])
    with col_reset:
        if st.button("🔄 Nuevo Ejercicio"):
            sys_p = obtener_prompt("drill", fase, idioma)
            q = consultar_ia(sys_p, "Empieza.")
            st.session_state.mensajes_drill = [{"role": "assistant", "content": q}]

    # Chat UI
    chat_container = st.container(height=250) # Un contenedor con scroll fijo
    with chat_container:
        for msg in st.session_state.mensajes_drill:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    if prompt := st.chat_input(f"Escribe en {idioma}..."):
        st.session_state.mensajes_drill.append({"role": "user", "content": prompt})
        with chat_container:
            st.chat_message("user").write(prompt)
            
            with st.spinner("Corrigiendo..."):
                sys_p = obtener_prompt("drill", fase, idioma)
                contexto = str(st.session_state.mensajes_drill[-3:])
                resp = consultar_ia(sys_p, f"Usuario: '{prompt}'. Contexto: {contexto}. Corrige brevemente y sigue.")
                
                st.session_state.mensajes_drill.append({"role": "assistant", "content": resp})
                st.chat_message("assistant").write(resp)

# --- TAB 3: ROLEPLAY ---
with tab3:
    st.subheader("Simulador de Inmersión")
    col_x, col_y = st.columns(2)
    
    with col_x:
        escenario = st.selectbox("Situación:", ["Restaurante", "Aeropuerto", "Hotel", "Cita Médica", "Trabajo"])
    
    with col_y:
        st.write("") # Espaciador
        st.write("") 
        start_rp = st.button("🎬 ¡Acción!", use_container_width=True)

    if start_rp:
        with st.spinner("Creando escenario..."):
            sys_p = obtener_prompt("roleplay", f"{fase} - {escenario}", idioma)
            intro = consultar_ia(sys_p, "Empieza.")
            st.success(f"Escenario: {escenario}")
            st.chat_message("assistant").write(intro)
            st.info("💡 Tip: Responde en tu mente o en voz alta para practicar.")













