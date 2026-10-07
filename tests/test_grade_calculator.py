import pytest
from strategy.standard_calculator import StandardGradeCalculator
from domain.grade_component_score import GradeComponentScore
from domain.grade_percentage import GradePercentage

def test_weighted_grade_calculation():
    calculator = StandardGradeCalculator()

    # 20% Quizzes, 30% Lab Projects, 50% Exam
    percentages = [
        GradePercentage('PCT001', 20.0, 'OFF001', 'CMP001'),
        GradePercentage('PCT002', 30.0, 'OFF001', 'CMP002'),
        GradePercentage('PCT003', 50.0, 'OFF001', 'CMP003'),
    ]

    # Scores: Quiz 80/100 (16%), Lab 90/100 (27%), Exam 85/100 (42.5%) = 85.5%
    scores = [
        GradeComponentScore('SCR001', 80.0, 'GRD001', 'CMP001', max_score=100.0),
        GradeComponentScore('SCR002', 90.0, 'GRD001', 'CMP002', max_score=100.0),
        GradeComponentScore('SCR003', 85.0, 'GRD001', 'CMP003', max_score=100.0),
    ]

    result = calculator.compute_period_grade(scores, percentages)
    assert result == 85.5

def test_invalid_weight_total_raises_error():
    calculator = StandardGradeCalculator()
    invalid_percentages = [
        GradePercentage('PCT001', 50.0, 'OFF001', 'CMP001'),
        GradePercentage('PCT002', 40.0, 'OFF001', 'CMP002'), # Sums to 90%, not 100%
    ]
    scores = [GradeComponentScore('SCR001', 80.0, 'GRD001', 'CMP001')]

    with pytest.raises(ValueError):
        calculator.compute_period_grade(scores, invalid_percentages)