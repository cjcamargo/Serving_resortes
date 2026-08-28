"""Interfaz Streamlit de la calculadora de resortes de Serving S.A.S."""

from __future__ import annotations

import base64
import math
from pathlib import Path

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

HERO_PATH = Path(__file__).parent / "assets" / "serving-valve-spring-hero.png"
HERO_IMAGE = base64.b64encode(HERO_PATH.read_bytes()).decode("ascii")


st.markdown(
    """
    <style>
    :root {
        --serving-navy: #071b29;
        --serving-blue: #0b5d83;
        --serving-cyan: #13a8d8;
        --serving-blue-soft: #eaf5fa;
        --serving-yellow: #fff2a8;
        --serving-gold: #f2b134;
        --serving-orange: #ed8e45;
        --serving-ink: #102b3b;
        --serving-muted: #5c7380;
    }
    .stApp {
        color: var(--serving-ink);
        background:
            radial-gradient(circle at 92% 3%, rgba(19,168,216,.10), transparent 22rem),
            linear-gradient(180deg, #f9fbfc 0%, #f2f7f9 100%);
    }
    .block-container { max-width: 1240px; padding-top: 1.4rem; padding-bottom: 3rem; }
    div[data-testid="stHeadingWithActionElements"] h1 {
        color: var(--serving-navy);
        letter-spacing: -.035em;
        font-weight: 800;
        margin-bottom: 0;
    }
    div[data-testid="stCaptionContainer"] { color: var(--serving-muted); }
    div[data-testid="stForm"] {
        background: rgba(255,255,255,.94);
        border: 1px solid #d6e3e9;
        border-radius: 22px;
        padding: 1.5rem 1.65rem 1.65rem;
        box-shadow: 0 18px 50px rgba(7,27,41,.08);
    }
    div[data-testid="stNumberInput"] input {
        background: var(--serving-yellow);
        border-color: #e2ca53;
        color: #1a2d35;
        font-weight: 650;
    }
    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--serving-gold);
        box-shadow: 0 0 0 1px var(--serving-gold);
    }
    div[data-testid="stFormSubmitButton"] button {
        min-height: 3rem;
        border: 0;
        border-radius: 12px;
        background: linear-gradient(100deg, var(--serving-navy), var(--serving-blue));
        box-shadow: 0 9px 22px rgba(11,93,131,.22);
        font-weight: 750;
        letter-spacing: .015em;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(100deg, #0b2c40, #0b74a3);
        transform: translateY(-1px);
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #edf5f8);
        border: 1px solid #d6e4ea;
        border-top: 4px solid var(--serving-cyan);
        border-radius: 15px;
        padding: .85rem 1rem;
        box-shadow: 0 8px 24px rgba(7,27,41,.06);
    }
    div[data-testid="stMetricValue"] {
        color: var(--serving-navy);
        font-weight: 780;
    }
    .industrial-hero {
        min-height: 390px;
        margin: .6rem 0 1rem;
        padding: 3.1rem 3.2rem;
        border-radius: 26px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        background-image:
            linear-gradient(90deg, rgba(3,17,27,.98) 0%, rgba(3,20,32,.90) 37%, rgba(3,20,32,.20) 68%, rgba(3,20,32,.03) 100%),
            url("data:image/png;base64,HERO_IMAGE_PLACEHOLDER");
        background-size: cover;
        background-position: center;
        box-shadow: 0 24px 65px rgba(3,20,32,.27);
        overflow: hidden;
    }
    .hero-eyebrow {
        width: fit-content;
        color: #071b29;
        background: var(--serving-gold);
        border-radius: 999px;
        padding: .42rem .8rem;
        font-size: .72rem;
        font-weight: 850;
        letter-spacing: .11em;
    }
    .industrial-hero h2 {
        color: white;
        font-size: clamp(2rem, 4vw, 3.55rem);
        max-width: 680px;
        line-height: 1.02;
        letter-spacing: -.04em;
        margin: 1rem 0 .8rem;
    }
    .industrial-hero p {
        color: #cae0e9;
        font-size: 1.06rem;
        line-height: 1.55;
        max-width: 540px;
        margin: 0;
    }
    .process-strip {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .8rem;
        margin: 1rem 0 1.5rem;
    }
    .process-item {
        background: #ffffff;
        border: 1px solid #d7e4ea;
        border-radius: 14px;
        padding: .85rem 1rem;
        display: flex;
        gap: .8rem;
        align-items: center;
        box-shadow: 0 7px 18px rgba(7,27,41,.05);
    }
    .process-item b {
        color: var(--serving-cyan);
        font-size: 1.45rem;
        line-height: 1;
    }
    .process-item strong { display: block; color: var(--serving-navy); }
    .process-item small { color: var(--serving-muted); }
    .intro-copy {
        color: var(--serving-muted);
        font-size: 1rem;
        margin: .25rem 0 1.1rem;
    }
    .result-card {
        border-radius: 18px;
        padding: 1.15rem 1.35rem;
        margin: .7rem 0 1rem 0;
        box-shadow: 0 12px 30px rgba(7,27,41,.08);
    }
    .result-card.preferred {
        background: linear-gradient(135deg, #e9f7fc, #dceef5);
        border: 2px solid var(--serving-blue);
    }
    .result-card.exceptional {
        background: linear-gradient(135deg, #fff6e9, #ffead7);
        border: 2px solid var(--serving-orange);
    }
    .result-card h3 { margin: 0 0 .35rem 0; color: var(--serving-navy); }
    .safety-note {
        color: #dcecf2;
        background: linear-gradient(115deg, #071b29, #0c354a);
        border-left: 6px solid var(--serving-gold);
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-top: 1.6rem;
        font-size: .93rem;
    }
    .safety-note strong { color: #ffd66d; }
    div[data-testid="stDataFrame"] {
        border: 1px solid #d5e2e8;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(7,27,41,.05);
    }
    @media (max-width: 760px) {
        .industrial-hero {
            min-height: 430px;
            padding: 2rem 1.3rem;
            background-position: 62% center;
        }
        .industrial-hero h2 { font-size: 2.25rem; max-width: 90%; }
        .industrial-hero p { max-width: 78%; }
        .process-strip { grid-template-columns: 1fr; }
    }
    </style>
    """.replace("HERO_IMAGE_PLACEHOLDER", HERO_IMAGE),
    unsafe_allow_html=True,
)

st.title("Serving S.A.S.")
st.caption("Ingeniería y mantenimiento de válvulas de seguridad")

st.markdown(
    """
    <section class="industrial-hero">
      <span class="hero-eyebrow">INGENIERÍA DE VÁLVULAS · CÁLCULO DE RESORTES</span>
      <h2>Calculadora de resortes bajo estándares de diseño industrial.</h2>
      <p>
        Evalúa la rigidez, calcula la presión de apertura y compara diámetros
        de alambre con una metodología probada en operación.
      </p>
    </section>
    <section class="process-strip">
      <div class="process-item"><b>01</b><div><strong>Mide</strong><small>Geometría real del resorte</small></div></div>
      <div class="process-item"><b>02</b><div><strong>Calcula</strong><small>Rigidez y presión de apertura</small></div></div>
      <div class="process-item"><b>03</b><div><strong>Compara</strong><small>Opciones técnicas y económicas</small></div></div>
    </section>
    <p class="intro-copy">
      Ingrese las medidas del resorte actual y la presión deseada. Los campos
      amarillos corresponden a datos medidos directamente por el técnico.
    </p>
    """,
    unsafe_allow_html=True,
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


def spring_diagram_svgs(
    *,
    outside_diameter_mm: float,
    inside_diameter_mm: float,
    wire_diameter_mm: float,
    active_coils: float,
    total_coils: float,
    average_gap_mm: float,
    free_height_mm: float,
) -> tuple[str, str]:
    """Construye las vistas frontal y superior con las medidas del resorte."""

    center_x = 215.0
    top_y = 95.0
    drawing_height = 190.0
    radius = 82.0
    visible_turns = max(2.0, min(float(total_coils), 12.0))
    wire_stroke = max(
        7.0,
        min(18.0, 56.0 * wire_diameter_mm / max(outside_diameter_mm, 0.1)),
    )
    points = []
    for index in range(361):
        progress = index / 360
        x = center_x + radius * math.sin(2 * math.pi * visible_turns * progress)
        y = top_y + drawing_height * progress
        points.append(f"{x:.1f},{y:.1f}")
    spring_points = " ".join(points)

    plan_center_x = 230.0
    plan_center_y = 185.0
    outside_radius = 82.0
    inside_radius = max(
        8.0,
        min(76.0, outside_radius * inside_diameter_mm / max(outside_diameter_mm, 0.1)),
    )
    wire_mid_radius = (outside_radius + inside_radius) / 2
    plan_wire_stroke = max(6.0, outside_radius - inside_radius)

    shared_defs = """
        <defs>
          <linearGradient id="spring-metal" x1="0" x2="1">
            <stop offset="0" stop-color="#5d8799"/>
            <stop offset="0.45" stop-color="#d9f1f8"/>
            <stop offset="0.7" stop-color="#78a9bc"/>
            <stop offset="1" stop-color="#31586a"/>
          </linearGradient>
          <marker id="dimension-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#f2b134"/>
          </marker>
          <filter id="spring-shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#020c12" flood-opacity=".65"/>
          </filter>
        </defs>
        <style>
          .visual-title { fill: #ffffff; font: 700 18px sans-serif; }
          .visual-subtitle { fill: #9fc2d1; font: 12px sans-serif; }
          .dimension { stroke: #f2b134; stroke-width: 1.7; fill: none; }
          .extension { stroke: #6a94a6; stroke-width: 1; stroke-dasharray: 4 4; }
          .dimension-label { fill: #ffd66d; font: 700 13px sans-serif; }
          .technical-label { fill: #d8edf5; font: 600 13px sans-serif; }
          .muted-label { fill: #89aebd; font: 11px sans-serif; }
          .center-line { stroke: #416b7d; stroke-width: 1; stroke-dasharray: 7 6; }
        </style>
    """

    front_svg = f"""
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 350" role="img" aria-labelledby="spring-front-title spring-front-desc">
        <title id="spring-front-title">Vista frontal del resorte</title>
        <desc id="spring-front-desc">Altura libre, diámetro exterior, separación y número de espiras.</desc>
        <rect x="2" y="2" width="456" height="346" rx="18" fill="#071b29" stroke="#28566a"/>
        {shared_defs}
        <text x="24" y="28" class="visual-title">Vista frontal</text>
        <text x="24" y="48" class="visual-subtitle">Altura, espiras y separación</text>

        <line x1="215" y1="88" x2="215" y2="292" class="center-line"/>
        <polyline points="{spring_points}" fill="none" stroke="#020c12" stroke-width="{wire_stroke + 5:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity=".7"/>
        <polyline points="{spring_points}" fill="none" stroke="url(#spring-metal)" stroke-width="{wire_stroke:.1f}" stroke-linecap="round" stroke-linejoin="round" filter="url(#spring-shadow)"/>

        <line x1="{center_x - radius:.1f}" y1="78" x2="{center_x - radius:.1f}" y2="96" class="extension"/>
        <line x1="{center_x + radius:.1f}" y1="78" x2="{center_x + radius:.1f}" y2="96" class="extension"/>
        <line x1="{center_x - radius:.1f}" y1="78" x2="{center_x + radius:.1f}" y2="78" class="dimension" marker-start="url(#dimension-arrow)" marker-end="url(#dimension-arrow)"/>
        <text x="215" y="68" text-anchor="middle" class="dimension-label">Diámetro exterior = {outside_diameter_mm:.1f} mm</text>

        <line x1="125" y1="95" x2="61" y2="95" class="extension"/>
        <line x1="125" y1="285" x2="61" y2="285" class="extension"/>
        <line x1="68" y1="95" x2="68" y2="285" class="dimension" marker-start="url(#dimension-arrow)" marker-end="url(#dimension-arrow)"/>
        <text x="47" y="190" text-anchor="middle" transform="rotate(-90 47 190)" class="dimension-label">Altura libre = {free_height_mm:.1f} mm</text>

        <line x1="300" y1="142" x2="342" y2="142" class="extension"/>
        <line x1="300" y1="163" x2="342" y2="163" class="extension"/>
        <line x1="336" y1="142" x2="336" y2="163" class="dimension" marker-start="url(#dimension-arrow)" marker-end="url(#dimension-arrow)"/>
        <text x="350" y="149" class="muted-label">Separación libre (s)</text>
        <text x="350" y="166" class="dimension-label">{average_gap_mm:.1f} mm</text>

        <text x="215" y="318" text-anchor="middle" class="technical-label">Espiras totales: {total_coils:g} · Espiras activas: {active_coils:g}</text>
      </svg>
    """

    top_svg = f"""
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 350" role="img" aria-labelledby="spring-top-title spring-top-desc">
        <title id="spring-top-title">Vista superior del resorte</title>
        <desc id="spring-top-desc">Diámetros exterior, interior y del alambre.</desc>
        <rect x="2" y="2" width="456" height="346" rx="18" fill="#071b29" stroke="#28566a"/>
        {shared_defs}
        <text x="24" y="28" class="visual-title">Vista superior</text>
        <text x="24" y="48" class="visual-subtitle">Diámetros exterior, interior y del alambre</text>

        <line x1="125" y1="185" x2="335" y2="185" class="center-line"/>
        <line x1="230" y1="80" x2="230" y2="290" class="center-line"/>
        <circle cx="230" cy="185" r="{wire_mid_radius:.1f}" fill="none" stroke="#020c12" stroke-width="{plan_wire_stroke + 5:.1f}" opacity=".65"/>
        <circle cx="230" cy="185" r="{wire_mid_radius:.1f}" fill="none" stroke="url(#spring-metal)" stroke-width="{plan_wire_stroke:.1f}"/>

        <line x1="148" y1="73" x2="148" y2="103" class="extension"/>
        <line x1="312" y1="73" x2="312" y2="103" class="extension"/>
        <line x1="148" y1="83" x2="312" y2="83" class="dimension" marker-start="url(#dimension-arrow)" marker-end="url(#dimension-arrow)"/>
        <text x="230" y="69" text-anchor="middle" class="dimension-label">Diámetro exterior = {outside_diameter_mm:.1f} mm</text>

        <line x1="{plan_center_x - inside_radius:.1f}" y1="185" x2="{plan_center_x + inside_radius:.1f}" y2="185" class="dimension" marker-start="url(#dimension-arrow)" marker-end="url(#dimension-arrow)"/>
        <rect x="174" y="197" width="112" height="39" rx="6" fill="#0b3449" opacity=".96"/>
        <text x="230" y="212" text-anchor="middle" class="muted-label">Diámetro interior</text>
        <text x="230" y="229" text-anchor="middle" class="dimension-label">{inside_diameter_mm:.1f} mm</text>

        <line x1="{plan_center_x + inside_radius * 0.707:.1f}" y1="{plan_center_y + inside_radius * 0.707:.1f}" x2="{plan_center_x + outside_radius * 0.707:.1f}" y2="{plan_center_y + outside_radius * 0.707:.1f}" class="dimension" marker-start="url(#dimension-arrow)" marker-end="url(#dimension-arrow)"/>
        <line x1="{plan_center_x + outside_radius * 0.707:.1f}" y1="{plan_center_y + outside_radius * 0.707:.1f}" x2="330" y2="275" class="extension"/>
        <text x="330" y="293" text-anchor="middle" class="muted-label">Diámetro del alambre (d)</text>
        <text x="330" y="311" text-anchor="middle" class="dimension-label">{wire_diameter_mm:.1f} mm</text>
      </svg>
    """
    return front_svg.strip(), top_svg.strip()


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

    st.markdown("#### Vista ilustrativa de las medidas")
    front_svg, top_svg = spring_diagram_svgs(
        outside_diameter_mm=outside_diameter,
        inside_diameter_mm=inside_diameter,
        wire_diameter_mm=wire_diameter,
        active_coils=active_coils,
        total_coils=total_coils,
        average_gap_mm=average_gap,
        free_height_mm=free_height,
    )
    diagram_col_1, diagram_col_2 = st.columns(2)
    diagram_col_1.image(front_svg, width=500)
    diagram_col_2.image(top_svg, width=500)
    st.caption("Esquema ilustrativo para identificar las medidas; no está a escala.")

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
