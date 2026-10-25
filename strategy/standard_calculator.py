from decimal import Decimal, ROUND_HALF_UP


def _value(item, key):
    return item[key] if isinstance(item, dict) else getattr(item, key)


class StandardGradeCalculator:
    """The grading scale and weighting rules used by the project."""

    @staticmethod
    def get_grade_point(percentage: float):
        if percentage is None:
            return None, "Incomplete"

        # The professor's scale uses the unrounded percentage at every boundary.
        p = Decimal(str(percentage))
        bands = (
            (97, 1.00), (94, 1.25), (91, 1.50), (88, 1.75),
            (85, 2.00), (82, 2.25), (79, 2.50), (76, 2.75), (75, 3.00),
        )
        for minimum, point in bands:
            if p >= Decimal(str(minimum)):
                return point, "Passed"
        return 5.00, "Failed"

    def compute_period_grade(self, scores: list, percentages: list):
        if not percentages:
            raise ValueError("Grading weights have not been configured.")

        weights = {}
        for item in percentages:
            component_id = str(_value(item, "component_id"))
            weight = Decimal(str(_value(item, "percentage")))
            if weight < 0 or weight > 100:
                raise ValueError("Each component weight must be between 0 and 100%.")
            if component_id in weights:
                raise ValueError(f"Duplicate weight for component {component_id}.")
            weights[component_id] = weight

        if sum(weights.values()) != Decimal("100"):
            raise ValueError(
                f"Weights must total 100%; the current total is {sum(weights.values())}%."
            )

        score_by_component = {str(_value(s, "component_id")): s for s in scores}
        missing = set(weights) - set(score_by_component)
        if missing:
            return None

        total = Decimal("0")
        for component_id, weight in weights.items():
            item = score_by_component[component_id]
            score = Decimal(str(_value(item, "score")))
            max_score_value = _value(item, "max_score")
            if max_score_value is None or Decimal(str(max_score_value)) <= 0:
                raise ValueError(f"Invalid maximum score for component {component_id}.")
            maximum = Decimal(str(max_score_value))
            if score < 0 or score > maximum:
                raise ValueError(f"Score for component {component_id} must be between 0 and {maximum}.")
            total += (score / maximum) * weight

        return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    def compute_overall_grade(self, midterm_pct: float, finals_pct: float):
        if midterm_pct is None or finals_pct is None:
            return None, None, "Incomplete"
        overall = (
            Decimal(str(midterm_pct)) * Decimal("0.40")
            + Decimal(str(finals_pct)) * Decimal("0.60")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        grade_point, remarks = self.get_grade_point(overall)
        return float(overall), grade_point, remarks
