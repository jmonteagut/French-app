import streamlit as st
from openai import OpenAI
import random
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="unmute.", page_icon="⚡", layout="centered")

# --- 2. ESTILOS VISUALES (Mantenemos tu diseño moderno) ---
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

# --- 4. CEREBRO METODOLÓGICO (TUS 5 PILARES) ---
def get_system_prompt(dia, fase, modo="practica", contexto_extra=""):
    
    # PILAR 1: PLAN DE LENGUAJE (Objetivo utilizable, sin repeticiones)
    if dia <= 7:
        nivel = "PRINCIPIANTE - SUPERVIVENCIA"
        instruccion_idioma = "Habla en francés simple. Usa español (entre paréntesis) SOLO para aclarar el significado si es vital."
    elif dia <= 14:
        nivel = "INTERMEDIO - SOCIAL"
        instruccion_idioma = "Habla en francés natural. Evita el español salvo bloqueo total."
    else:
        nivel = "AVANZADO - FLUIDEZ"
        instruccion_idioma = "Solo Francés."

    base = f"""Eres Kai, un entrenador de francés enfocado en RESULTADOS PRIORITARIOS.
    Objetivo: Francés utilizable para viajes, trabajo y el día a día.
    Nivel actual: {nivel}. Contexto de hoy: '{fase}'.
    {instruccion_idioma}."""

    # PILAR 2: VOCABULARIO DE FRECUENCIA
    if modo == "vocab":
        return f"""{base}
        Enséñame las 5 palabras/frases en francés MÁS USADAS (Alta Frecuencia) para este contexto.
        Formato de lista estricto:
        Use emojis.
        Estructura: **Palabra/Frase** (Pronunciación figurada sencilla para hispanohablantes) - Significado - *Ejemplo muy corto y natural*."""

    # PILAR 5: SIMULADOR DE CONVERSACIÓN REAL (INICIO)
    elif modo == "inicio_activo":
        return f"""{base}
        Imita una conversación en francés natural para el escenario: '{fase}'.
        NO saludes genéricamente. Entra directo en el rol (Camarero, Recepcionista, Amigo, Desconocido).
        Hazme una pregunta corta para forzarme a hablar."""

    # PILAR 3 Y 4: EJERCICIOS DE HABLA Y GRAMÁTICA A LA CARTA
    elif modo == "practica":
        return f"""{base}
        Actúa como parte del simulador.
        1. Hazme preguntas cortas en francés. Espera mi respuesta.
        2. PILAR DE CORRECCIÓN: Corrígeme LIGERAMENTE y mejora mi expresión ("Así suena más natural: ...") sin interrumpir el ritmo.
        3. PILAR DE GRAMÁTICA: NO expliques gramática a menos que sea un error que impida la comprensión. Si explicas, que sea en 1 frase enfocada a la utilidad.
        Mantén el flujo de la conversación."""

    # EXÁMENES (Validación funcional)
    elif modo == "examen_generador":
        if contexto_extra == "traduccion": return f"Dime 3 frases en ESPAÑOL muy útiles sobre '{fase}' que yo deba saber decir en francés. Sepáralas con guiones (-)."
        elif contexto_extra == "quiz": return f"Hazme 3 preguntas rápidas en francés sobre cómo actuar en la situación '{fase}'. Sepáralas con guiones (-)."
        elif contexto_extra == "roleplay": return f"Ponme en una situación difícil de '{fase}' (ej: hubo un problema). Di tu primera frase en francés para ver cómo reacciono."

    elif modo == "examen_roleplay_activo": return f"Simulación de examen '{fase}'. Ponme a prueba. No ayudes."
    elif modo == "corrector_final": return f"Evalúa si fui capaz de comunicarme efectivamente (0/10). Sé breve y dame un consejo práctico."

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

# --- 6. SIDEBAR (CONTENIDO ACTUALIZADO A SUPERVIVENCIA REAL) ---
with st.sidebar:
    st.header("🗺️ Plan de 30 Días")
    dia = st.session_state.dia_actual
    
    # FASES REDEFINIDAS (Vocabulario del día a día)
    if dia == 1: fase = "Cafetería: Pedir y pagar"
    elif dia == 2: fase = "Transporte: Metro y Tickets"
    elif dia == 3: fase = "Supermercado: Básicos"
    elif dia == 4: fase = "Restaurante: Alergias y Carta"
    elif dia == 5: fase = "Calle: Pedir direcciones"
    elif dia == 6: fase = "Emergencia: Farmacia/Dolor"
    elif dia == 7: fase = "Hotel: Check-in y Wifi"
    elif dia <= 14: fase = "Social: Conociendo gente"
    elif dia <= 21: fase = "Trabajo y Llamadas"
    else: fase = "Opinión Fluida"
    
    st.progress(dia / 30)
    st.caption(f"Día {dia}: {fase}")

    if st.button("🔄 Reiniciar Lección"):
        st.session_state.mensajes = []
        st.session_state.vocabulario_dia = None
        st.session_state.modo_app = "practica"
        st.rerun()

# --- 7. INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="gradient-text">unmute.</h1>', unsafe_allow_html=True)

# A) GENERACIÓN DE LECCIÓN (Automática)
if not st.session_state.vocabulario_dia:
    with st.spinner(f"Kai está preparando el simulador de '{fase}'..."):
        # 1. Vocabulario de Frecuencia
        prompt_v = get_system_prompt(dia, fase, "vocab")
        vocab = consultar_kai([{"role": "system", "content": prompt_v}, {"role": "user", "content": "Generar"}])
        st.session_state.vocabulario_dia = vocab
        
        # 2. Inicio Activo (Simulador)
        if len(st.session_state.mensajes) == 0:
            prompt_i = get_system_prompt(dia, fase, "inicio_activo")
            inicio = consultar_kai([
                {"role": "system", "content": prompt_i}, 
                {"role": "user", "content": f"El usuario ya leyó el vocabulario: {vocab}. ¡Acción!"}
            ])
            st.session_state.mensajes.append({"role": "assistant", "content": inicio})

# Tarjeta Vocabulario
with st.expander(f"📚 Vocabulario Útil: {fase}", expanded=True):
    st.markdown(f'<div class="vocab-card">{st.session_state.vocabulario_dia}</div>', unsafe_allow_html=True)

st.divider()

# B) CHAT (SIMULADOR)
for msg in st.session_state.mensajes:
    avatar = "🧢" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# --- 8. ZONA DE RESPUESTA ---

# MODO EXAMEN
if st.session_state.modo_app == "examen_activo":
    tipo = st.session_state.examen_tipo
    prog = st.session_state.examen_progreso
    label = f"🎭 SIMULACIÓN ({prog+1}/3)" if tipo == "roleplay" else f"📝 RETO ({prog+1}/3)"
    
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

# MODO CORRECCIÓN
elif st.session_state.modo_app == "examen_finalizado":
    if len(st.session_state.mensajes) > 0 and "RESULTADO" not in st.session_state.mensajes[-1]["content"]:
        with st.spinner("Analizando resultados..."):
            log = "\n".join([f"R{i+1}: {r}" for i, r in enumerate(st.session_state.examen_respuestas)])
            p_sys = get_system_prompt(dia, fase, "corrector_final")
            corr = consultar_kai([{"role": "system", "content": p_sys}, {"role": "user", "content": log}])
            st.session_state.mensajes.append({"role": "assistant", "content": f"🎓 **FEEDBACK:**\n\n{corr}"})
            st.balloons()
            st.rerun()
    
    if st.button("🚀 Siguiente Día", type="primary"):
        st.session_state.dia_actual += 1
        st.session_state.mensajes = []
        st.session_state.vocabulario_dia = None
        st.session_state.modo_app = "practica"
        st.rerun()

# MODO PRÁCTICA (SIMULADOR DE HABLA)
elif st.session_state.modo_app == "practica":
    if prompt := st.chat_input("Responde para seguir el ritmo..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        
        # PROMPT DE CORRECCIÓN LIGERA
        p_sys = get_system_prompt(dia, fase, "practica")
        historial = [{"role": "system", "content": p_sys}] + st.session_state.mensajes[-5:]
        
        with st.spinner("..."):
            resp = consultar_kai(historial)
        
        st.session_state.mensajes.append({"role": "assistant", "content": resp})
        st.rerun()

    # Opción de examen tras practicar
    if len(st.session_state.mensajes) >= 3:
        if st.button("💪 Demostrar lo aprendido (Reto)", type="primary", use_container_width=True):
            tipo = random.choice(["traduccion", "quiz", "roleplay"])
            st.session_state.examen_tipo = tipo
            with st.spinner(f"Preparando reto de {tipo}..."):
                p_sys = get_system_prompt(dia, fase, "examen_generador", tipo)
                raw = consultar_kai([{"role": "system", "content": p_sys}, {"role": "user", "content": "Generar"}])
                
                if tipo == "roleplay":
                    st.session_state.examen_data = "roleplay"
                    msg = f"🎭 **SITUACIÓN LÍMITE**\n{raw}"
                else:
                    qs = [q.strip() for q in raw.split("-") if q.strip()]
                    if len(qs)<3: qs = ["Q1", "Q2", "Q3"]
                    st.session_state.examen_data = qs
                    msg = f"📝 **TRADUCE RÁPIDO**\n1. {qs[0]}"

                st.session_state.modo_app = "examen_activo"
                st.session_state.examen_progreso = 0
                st.session_state.examen_respuestas = []
                st.session_state.mensajes.append({"role": "assistant", "content": msg})
                st.rerun()





















