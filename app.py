import streamlit as st
from openai import OpenAI
import random
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="unmute.", page_icon="⚡", layout="centered")

# --- 2. ESTILOS CSS ---
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

# --- 4. CEREBRO DE KAI (LOGICA DE INSTRUCTOR) ---
def get_system_prompt(dia, fase, modo="practica", contexto_extra=""):
    # Nivel de rigurosidad con el idioma
    if dia <= 7: idioma_inst = "Nivel Principiante: Usa español entre paréntesis SOLO para aclarar palabras muy difíciles."
    elif dia <= 14: idioma_inst = "Nivel Intermedio: Intenta hablar solo en francés."
    else: idioma_inst = "Nivel Avanzado: Solo francés."

    base = f"Eres Kai, tu objetivo es que el usuario use el vocabulario de hoy: '{fase}'. {idioma_inst}."

    if modo == "vocab":
        return f"{base} Genera 5 palabras/frases clave y útiles sobre el tema. Formato lista con emojis."

    # ESTE ES EL CAMBIO CLAVE: El inicio ya no es un saludo, es una SITUACIÓN
    elif modo == "inicio_activo":
        return f"""{base}
        NO SALUDES con un simple 'Hola'.
        Inicia DIRECTAMENTE una simulación o haz una pregunta específica que obligue al usuario a usar el vocabulario de '{fase}'.
        Ejemplo: Si el tema es 'Comida', di: 'Soy el camarero, ¿qué quieres comer hoy?'.
        Sé breve y directo."""

    # CORRECCIÓN CONSTANTE
    elif modo == "practica":
        return f"""{base}
        Continúa la conversación/simulación.
        REGLA DE ORO: Si el usuario comete un error gramatical, CORRÍGELO inmediatamente de forma breve entre paréntesis o negrita, y luego responde a lo que dijo para seguir la charla.
        No seas pesado con las correcciones, sé ágil."""

    # EXÁMENES (Igual que antes)
    elif modo == "examen_generador":
        if contexto_extra == "traduccion": return f"Genera 3 frases en ESPAÑOL sobre '{fase}' para traducir. Sepáralas con guion (-)."
        elif contexto_extra == "quiz": return f"Genera 3 preguntas tipo test en Francés sobre '{fase}'. Sepáralas con guion (-)."
        elif contexto_extra == "roleplay": return f"Define escenario roleplay sobre '{fase}'. Di tu primera frase."

    elif modo == "examen_roleplay_activo": return f"Roleplay de examen '{fase}'. NO CORRIJAS NADA AHORA."
    elif modo == "corrector_final": return f"Evalúa el examen (0/10) y lista los errores cometidos."

# --- 5. GESTIÓN DE ESTADO ---
if 'dia_actual' not in st.session_state: st.session_state.dia_actual = 1
if 'mensajes' not in st.session_state: st.session_state.mensajes = []
if 'vocabulario_dia' not in st.session_state: st.session_state.vocabulario_dia = None
if 'modo_app' not in st.session_state: st.session_state.modo_app = "practica"
# Variables examen
if 'examen_tipo' not in st.session_state: st.session_state.examen_tipo = None 
if 'examen_data' not in st.session_state: st.session_state.examen_data = [] 
if 'examen_respuestas' not in st.session_state: st.session_state.examen_respuestas = [] 
if 'examen_progreso' not in st.session_state: st.session_state.examen_progreso = 0

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("🗺️ Mapa")
    dia = st.session_state.dia_actual
    if dia <= 7: fase = "Supervivencia Básica"
    elif dia <= 14: fase = "Vida Social"
    elif dia <= 21: fase = "Viajes"
    else: fase = "Debate"
    st.progress(dia / 30)
    st.caption(f"Día {dia}: {fase}")

    if st.button("🔄 Reiniciar Lección"):
        st.session_state.mensajes = []
        st.session_state.vocabulario_dia = None
        st.session_state.modo_app = "practica"
        st.rerun()

# --- 7. INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="gradient-text">unmute.</h1>', unsafe_allow_html=True)

# A) GENERAR LECCIÓN AUTOMÁTICA
if not st.session_state.vocabulario_dia:
    with st.spinner("Kai está preparando la clase..."):
        # 1. Vocabulario
        prompt_v = get_system_prompt(dia, fase, "vocab")
        vocab = consultar_kai([{"role": "system", "content": prompt_v}, {"role": "user", "content": "Vocab"}])
        st.session_state.vocabulario_dia = vocab
        
        # 2. INICIO ACTIVO DE LA LECCIÓN (Solo si el chat está vacío)
        if len(st.session_state.mensajes) == 0:
            prompt_i = get_system_prompt(dia, fase, "inicio_activo")
            # Le pasamos el vocabulario generado para que sepa qué preguntar
            inicio = consultar_kai([
                {"role": "system", "content": prompt_i}, 
                {"role": "user", "content": f"Empieza la lección usando estas palabras: {vocab}"}
            ])
            st.session_state.mensajes.append({"role": "assistant", "content": inicio})

# Tarjeta Vocabulario
with st.expander("📚 Vocabulario Objetivo (Leéme primero)", expanded=True):
    st.markdown(f'<div class="vocab-card">{st.session_state.vocabulario_dia}</div>', unsafe_allow_html=True)

st.divider()

# B) CHAT DE LA LECCIÓN
for msg in st.session_state.mensajes:
    avatar = "🧢" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# --- 8. ZONA DE RESPUESTA ---

# CASO 1: EXAMEN
if st.session_state.modo_app == "examen_activo":
    tipo = st.session_state.examen_tipo
    prog = st.session_state.examen_progreso
    label = f"🎭 ROLEPLAY ({prog+1}/3)" if tipo == "roleplay" else f"📝 PREGUNTA ({prog+1}/3)"
    
    if resp := st.chat_input(label):
        st.session_state.mensajes.append({"role": "user", "content": resp})
        st.session_state.examen_respuestas.append(resp)
        st.session_state.examen_progreso += 1
        
        if st.session_state.examen_progreso >= 3:
            st.session_state.modo_app = "examen_finalizado"
            st.rerun()
        else:
            # Siguiente paso examen
            if tipo == "roleplay":
                p_sys = get_system_prompt(dia, fase, "examen_roleplay_activo")
                ctx = st.session_state.mensajes[-3:]
                ia_msg = consultar_kai([{"role": "system", "content": p_sys}] + ctx)
                st.session_state.mensajes.append({"role": "assistant", "content": ia_msg})
            else:
                next_q = st.session_state.examen_data[st.session_state.examen_progreso]
                st.session_state.mensajes.append({"role": "assistant", "content": f"➡️ {next_q}"})
            st.rerun()

# CASO 2: CORRECCIÓN EXAMEN
elif st.session_state.modo_app == "examen_finalizado":
    if len(st.session_state.mensajes) > 0 and "RESULTADO" not in st.session_state.mensajes[-1]["content"]:
        with st.spinner("Evaluando..."):
            log = "\n".join([f"R{i+1}: {r}" for i, r in enumerate(st.session_state.examen_respuestas)])
            p_sys = get_system_prompt(dia, fase, "corrector_final")
            corr = consultar_kai([{"role": "system", "content": p_sys}, {"role": "user", "content": log}])
            st.session_state.mensajes.append({"role": "assistant", "content": f"🎓 **RESULTADO:**\n\n{corr}"})
            st.balloons()
            st.rerun()
    
    if st.button("🚀 Siguiente Lección", type="primary"):
        st.session_state.dia_actual += 1
        st.session_state.mensajes = []
        st.session_state.vocabulario_dia = None
        st.session_state.modo_app = "practica"
        st.rerun()

# CASO 3: PRÁCTICA (LECCIÓN ACTIVA)
elif st.session_state.modo_app == "practica":
    # El input ahora invita a responder a la lección
    if prompt := st.chat_input("Responde a Kai..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        
        # Kai responde y corrige
        p_sys = get_system_prompt(dia, fase, "practica")
        historial = [{"role": "system", "content": p_sys}] + st.session_state.mensajes[-5:]
        
        with st.spinner("Kai está escribiendo..."):
            resp = consultar_kai(historial)
        
        st.session_state.mensajes.append({"role": "assistant", "content": resp})
        st.rerun()

    # Opción de examen tras practicar un poco
    if len(st.session_state.mensajes) >= 3:
        if st.button("🎲 Pasar a Examen Sorpresa", type="primary", use_container_width=True):
            tipo = random.choice(["traduccion", "quiz", "roleplay"])
            st.session_state.examen_tipo = tipo
            with st.spinner(f"Generando examen de {tipo}..."):
                p_sys = get_system_prompt(dia, fase, "examen_generador", tipo)
                raw = consultar_kai([{"role": "system", "content": p_sys}, {"role": "user", "content": "Generar"}])
                
                if tipo == "roleplay":
                    st.session_state.examen_data = "roleplay"
                    msg = f"🎭 **ROLEPLAY EXAMEN**\n{raw}"
                else:
                    qs = [q.strip() for q in raw.split("-") if q.strip()]
                    if len(qs)<3: qs = ["Q1", "Q2", "Q3"]
                    st.session_state.examen_data = qs
                    msg = f"📝 **QUIZ EXAMEN**\n1. {qs[0]}"

                st.session_state.modo_app = "examen_activo"
                st.session_state.examen_progreso = 0
                st.session_state.examen_respuestas = []
                st.session_state.mensajes.append({"role": "assistant", "content": msg})
                st.rerun()




















