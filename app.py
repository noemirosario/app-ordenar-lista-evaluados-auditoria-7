import streamlit as st
import pandas as pd
import io

st.title("Generador de Evaluaciones")

# Subir archivo Excel
archivo_subido = st.file_uploader("Sube el archivo Excel con las hojas 'Evaluados' y 'Evaluadores'", type=["xlsx"])

if archivo_subido:
    try:
        # Leer hojas
        evaluados = pd.read_excel(archivo_subido, sheet_name="Evaluados")
        evaluadores = pd.read_excel(archivo_subido, sheet_name="Evaluadores")

        # Procesar data
        evaluados = evaluados[['Tienda', 'Nomina']].rename(columns={'Nomina': 'Evaluado'})
        evaluadores = evaluadores[['Tienda', 'Nomina']].rename(columns={'Nomina': 'Evaluador'})

        # Autoevaluaciones
        autoevals = evaluados.copy()
        autoevals = autoevals.rename(columns={'Evaluado': 'Evaluador'})
        autoevals['Evaluado'] = autoevals['Evaluador']

        # Merge cruzado por tienda
        resultado = pd.merge(evaluados, evaluadores, on="Tienda", how="inner")
        resultado = resultado[resultado['Evaluado'] != resultado['Evaluador']]

        # Unión final
        resultado_final = pd.concat([resultado, autoevals], ignore_index=True)

        # Mostrar resultados
        st.subheader("Vista previa del resultado:")
        st.dataframe(resultado_final)

        # Descargar archivo
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            resultado_final.to_excel(writer, index=False, sheet_name='Resultado')
        output.seek(0)

        st.download_button(
            label="📥 Descargar archivo generado",
            data=output,
            file_name="Evaluaciones_Generadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
