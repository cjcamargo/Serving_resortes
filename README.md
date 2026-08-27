# Serving S.A.S. — Calculadora de resortes

Aplicación Streamlit para apoyar el rediseño de resortes de válvulas de
seguridad. A partir de las medidas del resorte actual y una presión deseada,
calcula alternativas de diámetro de alambre y la deflexión necesaria para cada
una.

## Modelo de cálculo

La aplicación reproduce el modelo de cálculo que Serving S.A.S. utiliza en su
hoja de trabajo:

```text
K = (d⁴ × G) / (8 × D_exterior³ × N_activas)
Área = 3.1415 × (diámetro_boquilla / 2)²
Presión = (K × deflexión) / Área
```

Las medidas geométricas se ingresan en milímetros, `G` en Mpsi y la presión en
PSI. El motor convierte internamente las longitudes a pulgadas para conservar
las convenciones del archivo original.

La deflexión disponible se calcula como:

```text
altura_sólida = espiras_totales × diámetro_alambre
deflexión_disponible = altura_libre − altura_sólida
```

El diámetro exterior se mantiene constante para los resortes candidatos. Los
diámetros de alambre se evalúan en incrementos de 0.5 mm. El intervalo preferido
es de 25% a 40% de deflexión; cuando corresponde, la aplicación muestra
alternativas excepcionales hasta un máximo absoluto de 60%.

Además, cuando existe al menos una opción preferida, se muestra por separado el
diámetro inmediatamente anterior —0.5 mm menor que la opción preferida mínima—
como comparación económica. Si requiere más de 60% de deflexión, queda marcado
explícitamente como referencia y no como recomendación técnica.

## Uso local

Requiere Python 3.12.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Pruebas

```powershell
python -m pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

Las pruebas incluyen el caso de referencia del Excel: alambre de 10 mm,
diámetro exterior de 50 mm, siete espiras activas, boquilla de 40 mm,
deflexión disponible de 60 mm y `G = 11.6 Mpsi`.

## Publicación en Streamlit Community Cloud

1. Crear una aplicación desde este repositorio.
2. Seleccionar la rama `main`.
3. Usar `streamlit_app.py` como archivo de entrada.
4. Seleccionar Python 3.12.

La aplicación no requiere secretos ni servicios externos.

## Alcance y seguridad

Esta herramienta apoya cálculos preliminares. No sustituye la revisión de
ingeniería, la comprobación de esfuerzos y materiales ni la calibración y prueba
en banco de la válvula antes de entrar en servicio.

El archivo Excel original no se incluye en el repositorio. Solo se trasladó a
código la lógica necesaria de su hoja de cálculo de resortes.
