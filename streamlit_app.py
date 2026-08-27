"""Interfaz Streamlit de la calculadora de resortes de Serving S.A.S."""

from __future__ import annotations

import streamlit as st

from spring_calculator import (
    Recommendation,
    SpringInputs,
    derive_geometry,
    generate_recommendations,
    validate_inputs,
)


st.set_page_config(
    page_title="Serving S.A.S. | Calculadora de resortes",
    page_icon="⚙️",
    layout="wide",
)


st.markdown(
    """
    <style>
    :root {
        --serving-blue: #164e78;
        --serving-blue-soft: #e8f2f8;
        --serving-yellow: #fff3a6;
        --serving-orange: #f5b47b;
        --serving-ink: #173042;
    }
    .stApp { color: var(--serving-ink); }
    .block-container { max-width: 1180px; padding-top: 2.2rem; }
    div[data-testid="stNumberInput"] input {
        background: var(--serving-yellow);
        border-color: #d8bf37;
    }
    div[data-testid="stHeadingWithActionElements"] h1 {
        color: var(--serving-blue);
    }
    .result-card {
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: .7rem 0 1rem 0;
    }
    .result-card.preferred {
        background: var(--serving-blue-soft);
        border: 2px solid var(--serving-blue);
    }
    .result-card.exceptional {
        background: #fff1e4;
        border: 2px solid var(--serving-orange);
    }
    .result-card h3 { margin: 0 0 .35rem 0; }
    .safety-note {
        background: #f4f6f8;
        border-left: 5px solid #697b88;
        padding: .8rem 1rem;
        margin-top: 1.4rem;
        font-size: .93rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Serving S.A.S.")
st.caption("Calculadora de resortes para válvulas de seguridad")

st.write(
    "Ingrese las medidas del resorte actual y la presión deseada. "
    "Los campos amarillos corresponden a datos medidos por el técnico."
)


def recommendation_rows(recommendations: tuple[Recommendation, ...]) -> list[dict[str, str]]:
    return [
        {
            "Tipo": item.classification,
            "Alambre nuevo (mm)": f"{item.wire_diameter_mm:.1f}",
            "Cambio (mm)": f"{item.wire_change_mm:+.1f}",
            "Diámetro interior (mm)": f"{item.resulting_inside_diameter_mm:.2f}",
            "K (lb/in)": f"{item.spring_rate_lb_per_in:,.3f}",
            "Altura sólida (mm)": f"{item.solid_height_mm:.2f}",
            "Deflexión disponible (mm)": f"{item.available_deflection_mm:.2f}",
            "Deflexión requerida (mm)": f"{item.required_deflection_mm:.2f}",
            "Deflexión (%)": f"{item.deflection_percent:.2f}%",
        }
        for item in recommendations
    ]


with st.form("spring_form"):
    st.subheader("Datos del resorte")
    spring_col_1, spring_col_2, spring_col_3 = st.columns(3)
    with spring_col_1:
        outside_diameter = st.number_input(
            "Diámetro exterior (mm)", min_value=0.1, value=50.0, step=0.1
        )
        inside_diameter = st.number_input(
            "Diámetro interior (mm)", min_value=0.1, value=30.0, step=0.1
        )
        wire_diameter = st.number_input(
            "Diámetro actual del alambre (mm)", min_value=0.1, value=10.0, step=0.1
        )
    with spring_col_2:
        active_coils = st.number_input(
            "Espiras activas", min_value=1.0, value=7.0, step=0.5
        )
        total_coils = st.number_input(
            "Espiras totales", min_value=1.0, value=9.0, step=0.5
        )
        average_gap = st.number_input(
            "Separación promedio entre espiras activas (mm)",
            min_value=0.1,
            value=10.0,
            step=0.1,
        )
    with spring_col_3:
        free_height = st.number_input(
            "Altura libre total, sin carga (mm)",
            min_value=0.1,
            value=150.0,
            step=0.1,
        )
        shear_modulus = st.number_input(
            "Módulo de corte G (Mpsi)",
            min_value=0.1,
            value=11.6,
            step=0.1,
            help="El Excel utiliza 11.6 Mpsi.",
        )

    st.subheader("Datos de la válvula y presión objetivo")
    valve_col_1, valve_col_2 = st.columns(2)
    with valve_col_1:
        nozzle_diameter = st.number_input(
            "Diámetro efectivo de la boquilla (mm)",
            min_value=0.1,
            value=40.0,
            step=0.1,
        )
    with valve_col_2:
        target_pressure = st.number_input(
            "Presión deseada (PSI)",
            min_value=0.1,
            value=300.0,
            step=1.0,
        )

    confirm_warnings = st.checkbox(
        "Confirmo que revisé las mediciones y deseo continuar si aparecen advertencias."
    )
    submitted = st.form_submit_button(
        "Calcular recomendaciones", type="primary", use_container_width=True
    )


if submitted:
    inputs = SpringInputs(
        outside_diameter_mm=outside_diameter,
        inside_diameter_mm=inside_diameter,
        wire_diameter_mm=wire_diameter,
        active_coils=active_coils,
        total_coils=total_coils,
        average_gap_mm=average_gap,
        free_height_mm=free_height,
        nozzle_diameter_mm=nozzle_diameter,
        target_pressure_psi=target_pressure,
        shear_modulus_mpsi=shear_modulus,
    )
    issues = validate_inputs(inputs)
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]

    if errors:
        st.error("No es posible calcular con los datos ingresados.")
        for issue in errors:
            st.write(f"- {issue.message}")
    else:
        if warnings:
            st.warning("Revise estas diferencias antes de utilizar el cálculo:")
            for issue in warnings:
                st.write(f"- {issue.message}")

        if warnings and not confirm_warnings:
            st.info(
                "Marque la casilla de confirmación y vuelva a calcular para continuar."
            )
        else:
            geometry = derive_geometry(inputs)
            result = generate_recommendations(inputs)

            st.divider()
            st.subheader("Resumen del resorte actual")
            metric_1, metric_2, metric_3, metric_4 = st.columns(4)
            metric_1.metric("K del resorte", f"{geometry.spring_rate_lb_per_in:,.3f} lb/in")
            metric_2.metric("Altura sólida", f"{geometry.solid_height_mm:.2f} mm")
            metric_3.metric(
                "Deflexión disponible", f"{geometry.available_deflection_mm:.2f} mm"
            )
            metric_4.metric(
                "Deflexión por espacios", f"{geometry.gap_based_deflection_mm:.2f} mm"
            )

            pressure_1, pressure_2, pressure_3 = st.columns(3)
            pressure_1.metric("Presión al 25%", f"{geometry.pressure_at_25_psi:,.3f} PSI")
            pressure_2.metric("Presión al 40%", f"{geometry.pressure_at_40_psi:,.3f} PSI")
            pressure_3.metric("Presión al 60%", f"{geometry.pressure_at_60_psi:,.3f} PSI")

            st.subheader("Recomendaciones")
            primary = result.primary
            if primary is None:
                st.error(
                    "No existe un diámetro factible que alcance la presión objetivo "
                    "entre 25% y 60% de deflexión."
                )
            else:
                card_class = (
                    "preferred" if primary.classification == "Preferida" else "exceptional"
                )
                st.markdown(
                    f"""
                    <div class="result-card {card_class}">
                      <h3>Recomendación principal: {primary.wire_diameter_mm:.1f} mm</h3>
                      <div>
                        Requiere <strong>{primary.required_deflection_mm:.2f} mm</strong>
                        de compresión, equivalentes al
                        <strong>{primary.deflection_percent:.2f}%</strong> de la
                        deflexión disponible. Clasificación:
                        <strong>{primary.classification}</strong>.
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                preferred_displayed = tuple(
                    item for item in result.displayed if item.classification == "Preferida"
                )
                exceptional_displayed = tuple(
                    item for item in result.displayed if item.classification == "Excepcional"
                )

                if preferred_displayed:
                    st.markdown("#### Opciones preferidas · 25% a 40%")
                    st.dataframe(
                        recommendation_rows(preferred_displayed),
                        hide_index=True,
                        use_container_width=True,
                    )

                if exceptional_displayed:
                    st.markdown("#### Opciones excepcionales · más de 40% y hasta 60%")
                    st.warning(
                        "Estas alternativas se muestran porque no hay una opción preferida "
                        "cercana al diámetro actual."
                    )
                    st.dataframe(
                        recommendation_rows(exceptional_displayed),
                        hide_index=True,
                        use_container_width=True,
                    )

                economic = result.economic_comparison
                if economic is not None:
                    st.markdown("#### Alternativa económica · diámetro anterior")
                    if economic.deflection_percent <= 60.0:
                        economic_note = (
                            "Está dentro del límite máximo de 60% y puede evaluarse "
                            "como una alternativa de menor costo."
                        )
                    else:
                        economic_note = (
                            "Supera el límite máximo de 60%; se muestra únicamente "
                            "como referencia económica y no como recomendación técnica."
                        )
                    st.markdown(
                        f"""
                        <div class="result-card exceptional">
                          <h3>{economic.wire_diameter_mm:.1f} mm de diámetro</h3>
                          <div>
                            Es 0.5 mm menor que la opción preferida mínima y requiere
                            <strong>{economic.required_deflection_mm:.2f} mm</strong>,
                            equivalentes al
                            <strong>{economic.deflection_percent:.2f}%</strong> de la
                            deflexión disponible. {economic_note}
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.dataframe(
                        recommendation_rows((economic,)),
                        hide_index=True,
                        use_container_width=True,
                    )

            with st.expander("Fórmulas utilizadas"):
                st.code(
                    "K = (d⁴ × G) / (8 × D_exterior³ × N_activas)\n"
                    "Área = 3.1415 × (diámetro_boquilla / 2)²\n"
                    "Presión = (K × deflexión) / Área",
                    language="text",
                )


st.markdown(
    """
    <div class="safety-note">
      <strong>Verificación obligatoria:</strong> esta herramienta apoya el rediseño
      preliminar. Todo resorte debe ser revisado por personal técnico competente y la
      válvula debe calibrarse y probarse en banco antes de entrar en servicio.
    </div>
    """,
    unsafe_allow_html=True,
)
