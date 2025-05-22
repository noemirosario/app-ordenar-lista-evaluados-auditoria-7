import streamlit as st
import pandas as pd
import io

st.title("Generador de Evaluaciones - Auxiliares de Surtido")

archivo_subido = st.file_uploader("📂 Sube el archivo Excel con las hojas 'Evaluados' y 'Evaluadores'", type=["xlsx"])

if archivo_subido:
    try:
        # Leer las hojas
        evaluados = pd.read_excel(archivo_subido, sheet_name="Evaluados")
        evaluadores = pd.read_excel(archivo_subido, sheet_name="Evaluadores")

        # Limpiar y seleccionar columnas
        evaluados['Tienda'] = evaluados['Tienda'].astype(str).str.strip()
        evaluadores['Tienda'] = evaluadores['Tienda'].astype(str).str.strip()

        evaluados = evaluados[['Tienda', 'Nomina']].rename(columns={'Nomina': 'Evaluado'})
        evaluadores = evaluadores[['Tienda', 'Nomina']].rename(columns={'Nomina': 'Evaluador'})

        # Combinación cruzada por tienda
        cruzado = pd.merge(evaluados, evaluadores, on='Tienda', how='inner')

        # Excluir autoevaluaciones del merge cruzado
        cruzado = cruzado[cruzado['Evaluado'] != cruzado['Evaluador']]

        # ✅ Agregar autoevaluaciones explícitas
        autoevals = evaluados.copy()
        autoevals['Evaluador'] = autoevals['Evaluado']
        autoevals = autoevals[['Tienda', 'Evaluador', 'Evaluado']]

        # ✅ Unir resultados
        resultado_final = pd.concat([cruzado, autoevals], ignore_index=True)

        # Mostrar resultados
        st.subheader("✅ Vista previa del resultado:")
        st.dataframe(resultado_final)

        # Opcional: mostrar autoevaluaciones por separado
        st.subheader("👤 Autoevaluaciones:")
        st.dataframe(resultado_final[resultado_final['Evaluador'] == resultado_final['Evaluado']])

        # Guardar archivo en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            resultado_final.to_excel(writer, index=False, sheet_name='Resultado')
        output.seek(0)

        # Botón para descargar
        st.download_button(
            label="📥 Descargar archivo generado",
            data=output,
            file_name="Evaluaciones_Generadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
