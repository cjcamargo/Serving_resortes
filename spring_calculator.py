"""Motor de cálculo para la calculadora de resortes de Serving S.A.S.

Las ecuaciones de este módulo reproducen deliberadamente el modelo del archivo
``CALCULOS RESORTES.xlsx``. En particular, la constante del resorte utiliza el
diámetro exterior de la espira como ``D``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal


MM_PER_INCH = 25.4
EXCEL_PI = 3.1415
WIRE_INCREMENT_MM = 0.5
PREFERRED_MIN_PERCENT = 25.0
PREFERRED_MAX_PERCENT = 40.0
EXCEPTIONAL_MAX_PERCENT = 60.0
DIAMETER_CHANGE_TRIGGER_MM = 1.0
EPSILON = 1e-9


Severity = Literal["error", "warning"]
Classification = Literal["Preferida", "Excepcional", "Comparativa económica"]


@dataclass(frozen=True)
class SpringInputs:
    outside_diameter_mm: float
    inside_diameter_mm: float
    wire_diameter_mm: float
    active_coils: float
    total_coils: float
    average_gap_mm: float
    free_height_mm: float
    nozzle_diameter_mm: float
    target_pressure_psi: float
    shear_modulus_mpsi: float = 11.6


@dataclass(frozen=True)
class ValidationIssue:
    severity: Severity
    code: str
    message: str


@dataclass(frozen=True)
class DerivedGeometry:
    geometric_wire_diameter_mm: float
    solid_height_mm: float
    available_deflection_mm: float
    gap_based_deflection_mm: float
    spring_rate_lb_per_in: float
    pressure_at_25_psi: float
    pressure_at_40_psi: float
    pressure_at_60_psi: float


@dataclass(frozen=True)
class Recommendation:
    wire_diameter_mm: float
    wire_change_mm: float
    resulting_inside_diameter_mm: float
    spring_rate_lb_per_in: float
    solid_height_mm: float
    available_deflection_mm: float
    required_deflection_mm: float
    deflection_percent: float
    classification: Classification


@dataclass(frozen=True)
class RecommendationSet:
    preferred: tuple[Recommendation, ...]
    exceptional: tuple[Recommendation, ...]
    displayed: tuple[Recommendation, ...]
    economic_comparison: Recommendation | None
    expansion_triggered: bool

    @property
    def primary(self) -> Recommendation | None:
        if self.preferred:
            return self.preferred[0]
        if self.exceptional:
            return self.exceptional[0]
        return None


def spring_rate_lb_per_in(
    wire_diameter_mm: float,
    outside_diameter_mm: float,
    active_coils: float,
    shear_modulus_mpsi: float,
) -> float:
    """Calcula K exactamente con la ecuación y unidades del Excel."""

    wire_diameter_in = wire_diameter_mm / MM_PER_INCH
    outside_diameter_in = outside_diameter_mm / MM_PER_INCH
    shear_modulus_psi = shear_modulus_mpsi * 1_000_000.0
    return (wire_diameter_in**4 * shear_modulus_psi) / (
        8.0 * outside_diameter_in**3 * active_coils
    )


def nozzle_area_in2(nozzle_diameter_mm: float) -> float:
    nozzle_radius_in = (nozzle_diameter_mm / MM_PER_INCH) / 2.0
    return EXCEL_PI * nozzle_radius_in**2


def pressure_for_deflection_psi(
    spring_rate: float,
    deflection_mm: float,
    nozzle_diameter_mm: float,
) -> float:
    force_lb = spring_rate * (deflection_mm / MM_PER_INCH)
    return force_lb / nozzle_area_in2(nozzle_diameter_mm)


def required_deflection_mm(
    target_pressure_psi: float,
    spring_rate: float,
    nozzle_diameter_mm: float,
) -> float:
    required_force_lb = target_pressure_psi * nozzle_area_in2(nozzle_diameter_mm)
    return (required_force_lb / spring_rate) * MM_PER_INCH


def validate_inputs(inputs: SpringInputs) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    numeric_fields = {
        "diámetro exterior": inputs.outside_diameter_mm,
        "diámetro interior": inputs.inside_diameter_mm,
        "diámetro del alambre": inputs.wire_diameter_mm,
        "espiras activas": inputs.active_coils,
        "espiras totales": inputs.total_coils,
        "separación entre espiras": inputs.average_gap_mm,
        "altura libre": inputs.free_height_mm,
        "diámetro de boquilla": inputs.nozzle_diameter_mm,
        "presión objetivo": inputs.target_pressure_psi,
        "módulo de corte": inputs.shear_modulus_mpsi,
    }

    for label, value in numeric_fields.items():
        if not isfinite(value) or value <= 0:
            issues.append(
                ValidationIssue(
                    "error",
                    f"non_positive_{label}",
                    f"El valor de {label} debe ser mayor que cero.",
                )
            )

    if any(issue.severity == "error" for issue in issues):
        return tuple(issues)

    if inputs.outside_diameter_mm <= inputs.inside_diameter_mm:
        issues.append(
            ValidationIssue(
                "error",
                "diameter_order",
                "El diámetro exterior debe ser mayor que el diámetro interior.",
            )
        )

    if inputs.outside_diameter_mm <= 2.0 * inputs.wire_diameter_mm:
        issues.append(
            ValidationIssue(
                "error",
                "wire_too_large",
                "El diámetro del alambre no deja un diámetro interior positivo.",
            )
        )

    if inputs.total_coils < inputs.active_coils:
        issues.append(
            ValidationIssue(
                "error",
                "coil_count_order",
                "Las espiras totales no pueden ser menores que las espiras activas.",
            )
        )

    solid_height = inputs.total_coils * inputs.wire_diameter_mm
    available_deflection = inputs.free_height_mm - solid_height
    if available_deflection <= 0:
        issues.append(
            ValidationIssue(
                "error",
                "no_available_deflection",
                "La altura libre debe ser mayor que la altura sólida del resorte.",
            )
        )

    geometric_wire = (
        inputs.outside_diameter_mm - inputs.inside_diameter_mm
    ) / 2.0
    if abs(inputs.wire_diameter_mm - geometric_wire) > 0.5 + EPSILON:
        issues.append(
            ValidationIssue(
                "warning",
                "wire_geometry_mismatch",
                "El diámetro de alambre medido difiere más de 0.5 mm del valor "
                "deducido a partir de los diámetros exterior e interior.",
            )
        )

    if abs(inputs.total_coils - (inputs.active_coils + 2.0)) > EPSILON:
        issues.append(
            ValidationIssue(
                "warning",
                "coil_count_mismatch",
                "Para extremos cerrados y rectificados se espera que las espiras "
                "totales sean las espiras activas más dos.",
            )
        )

    if available_deflection > 0:
        gap_based_deflection = max(inputs.active_coils - 1.0, 0.0) * inputs.average_gap_mm
        allowed_difference = max(1.0, 0.10 * available_deflection)
        if abs(available_deflection - gap_based_deflection) > allowed_difference + EPSILON:
            issues.append(
                ValidationIssue(
                    "warning",
                    "deflection_mismatch",
                    "La deflexión calculada por altura no coincide con la estimada "
                    "a partir del espacio entre espiras.",
                )
            )

    return tuple(issues)


def derive_geometry(inputs: SpringInputs) -> DerivedGeometry:
    spring_rate = spring_rate_lb_per_in(
        inputs.wire_diameter_mm,
        inputs.outside_diameter_mm,
        inputs.active_coils,
        inputs.shear_modulus_mpsi,
    )
    solid_height = inputs.total_coils * inputs.wire_diameter_mm
    available_deflection = inputs.free_height_mm - solid_height
    gap_based_deflection = max(inputs.active_coils - 1.0, 0.0) * inputs.average_gap_mm

    return DerivedGeometry(
        geometric_wire_diameter_mm=(
            inputs.outside_diameter_mm - inputs.inside_diameter_mm
        )
        / 2.0,
        solid_height_mm=solid_height,
        available_deflection_mm=available_deflection,
        gap_based_deflection_mm=gap_based_deflection,
        spring_rate_lb_per_in=spring_rate,
        pressure_at_25_psi=pressure_for_deflection_psi(
            spring_rate, available_deflection * 0.25, inputs.nozzle_diameter_mm
        ),
        pressure_at_40_psi=pressure_for_deflection_psi(
            spring_rate, available_deflection * 0.40, inputs.nozzle_diameter_mm
        ),
        pressure_at_60_psi=pressure_for_deflection_psi(
            spring_rate, available_deflection * 0.60, inputs.nozzle_diameter_mm
        ),
    )


def _candidate(
    inputs: SpringInputs,
    wire_diameter_mm: float,
    *,
    include_out_of_range: bool = False,
) -> Recommendation | None:
    resulting_inside = inputs.outside_diameter_mm - 2.0 * wire_diameter_mm
    solid_height = inputs.total_coils * wire_diameter_mm
    available_deflection = inputs.free_height_mm - solid_height
    if resulting_inside <= 0 or available_deflection <= 0:
        return None

    spring_rate = spring_rate_lb_per_in(
        wire_diameter_mm,
        inputs.outside_diameter_mm,
        inputs.active_coils,
        inputs.shear_modulus_mpsi,
    )
    required_deflection = required_deflection_mm(
        inputs.target_pressure_psi,
        spring_rate,
        inputs.nozzle_diameter_mm,
    )
    deflection_percent = 100.0 * required_deflection / available_deflection

    if PREFERRED_MIN_PERCENT - EPSILON <= deflection_percent <= PREFERRED_MAX_PERCENT + EPSILON:
        classification: Classification = "Preferida"
    elif PREFERRED_MAX_PERCENT + EPSILON < deflection_percent <= EXCEPTIONAL_MAX_PERCENT + EPSILON:
        classification = "Excepcional"
    elif include_out_of_range:
        classification = "Comparativa económica"
    else:
        return None

    return Recommendation(
        wire_diameter_mm=wire_diameter_mm,
        wire_change_mm=wire_diameter_mm - inputs.wire_diameter_mm,
        resulting_inside_diameter_mm=resulting_inside,
        spring_rate_lb_per_in=spring_rate,
        solid_height_mm=solid_height,
        available_deflection_mm=available_deflection,
        required_deflection_mm=required_deflection,
        deflection_percent=deflection_percent,
        classification=classification,
    )


def generate_recommendations(
    inputs: SpringInputs,
    max_results: int = 5,
) -> RecommendationSet:
    errors = [issue for issue in validate_inputs(inputs) if issue.severity == "error"]
    if errors:
        raise ValueError("No se pueden generar recomendaciones con entradas inválidas.")
    if max_results < 1:
        raise ValueError("max_results debe ser mayor que cero.")

    maximum_wire = min(
        inputs.outside_diameter_mm / 2.0,
        inputs.free_height_mm / inputs.total_coils,
    )
    step_count = int((maximum_wire - EPSILON) // WIRE_INCREMENT_MM)
    candidates = [
        candidate
        for index in range(1, step_count + 1)
        if (
            candidate := _candidate(inputs, index * WIRE_INCREMENT_MM)
        )
        is not None
    ]

    preferred = sorted(
        (item for item in candidates if item.classification == "Preferida"),
        key=lambda item: (
            abs(item.wire_change_mm),
            abs(item.deflection_percent - 32.5),
            item.wire_diameter_mm,
        ),
    )
    exceptional = sorted(
        (item for item in candidates if item.classification == "Excepcional"),
        key=lambda item: (
            abs(item.wire_change_mm),
            item.deflection_percent,
            item.wire_diameter_mm,
        ),
    )

    expansion_triggered = (
        not preferred
        or abs(preferred[0].wire_change_mm) > DIAMETER_CHANGE_TRIGGER_MM + EPSILON
    )

    economic_comparison = None
    if preferred:
        minimum_preferred_wire = min(item.wire_diameter_mm for item in preferred)
        previous_wire = minimum_preferred_wire - WIRE_INCREMENT_MM
        if previous_wire > 0:
            economic_comparison = _candidate(
                inputs,
                previous_wire,
                include_out_of_range=True,
            )

    if not preferred:
        displayed = exceptional[:max_results]
    elif expansion_triggered:
        preferred_slots = min(3, max_results)
        selected_preferred = preferred[:preferred_slots]
        remaining_slots = max_results - len(selected_preferred)
        economic_wire = (
            economic_comparison.wire_diameter_mm
            if economic_comparison is not None
            else None
        )
        other_exceptional = [
            item
            for item in exceptional
            if economic_wire is None
            or abs(item.wire_diameter_mm - economic_wire) > EPSILON
        ]
        displayed = selected_preferred + other_exceptional[:remaining_slots]
    else:
        displayed = preferred[:max_results]

    return RecommendationSet(
        preferred=tuple(preferred),
        exceptional=tuple(exceptional if expansion_triggered else ()),
        displayed=tuple(displayed),
        economic_comparison=economic_comparison,
        expansion_triggered=expansion_triggered,
    )
