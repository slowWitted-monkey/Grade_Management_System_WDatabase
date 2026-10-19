class StandardGradeCalculator:

    @staticmethod
    def get_grade_point(percentage: float) -> tuple[float, str]:
        """Converts percentage to Grade Point Equivalent and Remarks."""
        if percentage is None:
            return None, "Incomplete"

        p = round(percentage, 2)
        if 97.00 <= p <= 100.00:
            return 1.00, "Passed"
        elif 94.00 <= p < 97.00:
            return 1.25, "Passed"
        elif 91.00 <= p < 94.00:
            return 1.50, "Passed"
        elif 88.00 <= p < 91.00:
            return 1.75, "Passed"
        elif 85.00 <= p < 88.00:
            return 2.00, "Passed"
        elif 82.00 <= p < 85.00:
            return 2.25, "Passed"
        elif 79.00 <= p < 82.00:
            return 2.50, "Passed"
        elif 76.00 <= p < 79.00:
            return 2.75, "Passed"
        elif 75.00 <= p < 76.00:
            return 3.00, "Passed"
        else:
            return 5.00, "Failed"

    def compute_period_grade(self, scores: list, percentages: list) -> float:
        """Computes weighted period grade from component scores and weights."""
        if not scores or not percentages:
            return 0.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for score_info, weight_info in zip(scores, percentages):
            score = score_info["score"]
            max_score = score_info["max_score"]
            weight = weight_info["percentage"]

            if max_score > 0:
                weighted_component = (score / max_score) * weight
                total_weighted_score += weighted_component
                total_weight += weight

        return round(total_weighted_score, 2)

    def compute_overall_grade(self, midterm_pct: float, finals_pct: float) -> tuple[float, float, str]:
        """Computes Overall % = (Midterm * 0.40) + (Finals * 0.60) and derives Grade Point."""
        if midterm_pct is None or finals_pct is None:
            return None, None, "Incomplete"

        overall_pct = round((midterm_pct * 0.40) + (finals_pct * 0.60), 2)
        grade_point, remarks = self.get_grade_point(overall_pct)
        return overall_pct, grade_point, remarks