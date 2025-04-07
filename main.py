
import streamlit as st
import sqlite3
import openai
from datetime import datetime

# Configura tu clave de OpenAI
openai.api_key = "TU_API_KEY"

# Conexión a la base de datos SQLite
conn = sqlite3.connect("base_datos.db")
cursor = conn.cursor()

def ejecutar_consulta(pregunta_usuario):
    # Procesa la pregunta y devuelve una respuesta
    if "ahorros" in pregunta_usuario.lower():
        cursor.execute("SELECT SUM(saldo) FROM cuentas WHERE tipo = 'ahorro'")
        resultado = cursor.fetchone()[0]
        return f"El total en cuentas de ahorro es ${resultado:,.2f}"

    elif "créditos" in pregunta_usuario.lower():
        mes_actual = datetime.now().month
        cursor.execute("""
            SELECT SUM(monto) FROM creditos 
            WHERE strftime('%m', fecha_otorgado) = ?
        """, (f"{mes_actual:02d}",))
        resultado = cursor.fetchone()[0]
        return f"El monto total de créditos otorgados este mes es ${resultado:,.2f}"

    elif "morosos" in pregunta_usuario.lower():
        cursor.execute("""
            SELECT nombre FROM socios 
            WHERE id IN (SELECT socio_id FROM creditos WHERE estado = 'mora')
        """)
        morosos = cursor.fetchall()
        if morosos:
            nombres = ", ".join([m[0] for m in morosos])
            return f"Los socios en mora son: {nombres}"
        else:
            return "No hay socios en mora actualmente."

    else:
        # Si no encuentra coincidencias, usar GPT para responder
        respuesta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente financiero de una cooperativa."},
                {"role": "user", "content": pregunta_usuario},
            ]
        )
        return respuesta.choices[0].message.content

# Interfaz de usuario con Streamlit
st.set_page_config(page_title="Asistente de IA - Cooperativa", page_icon="📊")
st.title("🤖 Asistente de IA para Cooperativa de Ahorro y Crédito")

st.markdown("""
Ingresa una pregunta relacionada con:
- Ahorros
- Créditos
- Socios en mora

Ejemplos:
- "¿Cuál es el total en cuentas de ahorro?"
- "¿Cuántos créditos se han otorgado este mes?"
- "¿Quiénes están en mora?"
""")

pregunta = st.text_input("Haz tu pregunta:")

if pregunta:
    with st.spinner("Buscando respuesta..."):
        respuesta = ejecutar_consulta(pregunta)
        st.success(respuesta)

# Cierra la conexión al final
conn.close()
