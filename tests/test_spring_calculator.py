import pytest

from spring_calculator import (
    SpringInputs,
    derive_geometry,
    generate_recommendations,
    pressure_for_deflection_psi,
    spring_rate_lb_per_in,
    validate_inputs,
)


def excel_example(target_pressure_psi: float = 300.0) -> SpringInputs:
    return SpringInputs(
        outside_diameter_mm=50.0,
        inside_diameter_mm=30.0,
        wire_diameter_mm=10.0,
        active_coils=7.0,
        total_coils=9.0,
        average_gap_mm=10.0,
        free_height_mm=150.0,
        nozzle_diameter_mm=40.0,
        target_pressure_psi=target_pressure_psi,
        shear_modulus_mpsi=11.6,
    )


def test_excel_formula_is_reproduced_exactly() -> None:
    inputs = excel_example()
    geometry = derive_geometry(inputs)

    assert geometry.spring_rate_lb_per_in == pytest.approx(652.4184476940382)
    assert geometry.available_deflection_mm == pytest.approx(60.0)
    assert geometry.pressure_at_25_psi == pytest.approx(197.81269184420543)
    assert geometry.pressure_at_40_psi == pytest.approx(316.5003069507287)
    assert geometry.pressure_at_60_psi == pytest.approx(474.7504604260931)


def test_pressure_is_linear_with_deflection() -> None:
    inputs = excel_example()
    rate = spring_rate_lb_per_in(10.0, 50.0, 7.0, 11.6)
    pressure_15_mm = pressure_for_deflection_psi(rate, 15.0, 40.0)
    pressure_30_mm = pressure_for_deflection_psi(rate, 30.0, 40.0)
    assert pressure_30_mm == pytest.approx(2.0 * pressure_15_mm)


def test_recommendations_use_half_millimetre_steps_and_keep_outside_diameter() -> None:
    inputs = excel_example(target_pressure_psi=300.0)
    result = generate_recommendations(inputs)

    assert result.displayed
    for candidate in result.displayed:
        assert candidate.wire_diameter_mm * 2 == pytest.approx(
            round(candidate.wire_diameter_mm * 2)
        )
        assert candidate.resulting_inside_diameter_mm == pytest.approx(
            inputs.outside_diameter_mm - 2 * candidate.wire_diameter_mm
        )
        assert 25.0 <= candidate.deflection_percent <= 60.0


def test_exceptional_options_are_hidden_when_preferred_change_is_small() -> None:
    inputs = excel_example(target_pressure_psi=300.0)
    result = generate_recommendations(inputs)
    assert result.preferred
    assert abs(result.preferred[0].wire_change_mm) <= 1.0
    assert result.expansion_triggered is False
    assert result.exceptional == ()
    assert all(item.classification == "Preferida" for item in result.displayed)


def test_exceptional_options_never_exceed_sixty_percent() -> None:
    inputs = excel_example(target_pressure_psi=100.0)
    result = generate_recommendations(inputs)
    for candidate in result.displayed:
        assert candidate.deflection_percent <= 60.0


def test_impossible_geometry_is_blocked() -> None:
    inputs = SpringInputs(
        outside_diameter_mm=20.0,
        inside_diameter_mm=5.0,
        wire_diameter_mm=10.0,
        active_coils=7.0,
        total_coils=9.0,
        average_gap_mm=1.0,
        free_height_mm=80.0,
        nozzle_diameter_mm=40.0,
        target_pressure_psi=300.0,
    )
    issues = validate_inputs(inputs)
    assert any(issue.severity == "error" for issue in issues)
    with pytest.raises(ValueError):
        generate_recommendations(inputs)


def test_measurement_discrepancies_are_warnings() -> None:
    inputs = SpringInputs(
        outside_diameter_mm=50.0,
        inside_diameter_mm=34.0,
        wire_diameter_mm=10.0,
        active_coils=7.0,
        total_coils=10.0,
        average_gap_mm=3.0,
        free_height_mm=150.0,
        nozzle_diameter_mm=40.0,
        target_pressure_psi=300.0,
    )
    issues = validate_inputs(inputs)
    warning_codes = {issue.code for issue in issues if issue.severity == "warning"}
    assert warning_codes == {
        "wire_geometry_mismatch",
        "coil_count_mismatch",
        "deflection_mismatch",
    }
