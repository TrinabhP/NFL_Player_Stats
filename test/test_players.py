from src.api.players import (
    _combine_pair_similarity_metrics,
    _non_null_combine_measurements,
    _rank_by_combine_similarity,
    _prediction_vs_ideal_baseline,
)


def test_similarity_identical_profiles() -> None:
    anchor = {"forty_yard_dash": 4.4, "bench_press_reps": 25.0}
    candidate = {"forty_yard_dash": 4.4, "bench_press_reps": 25.0}

    score, count = _combine_pair_similarity_metrics(anchor, candidate)

    assert score == 100.0
    assert count == 2


def test_similarity_no_overlap() -> None:
    anchor = {"forty_yard_dash": 4.4}
    candidate = {"bench_press_reps": 20.0}

    score, count = _combine_pair_similarity_metrics(anchor, candidate)

    assert score == 0.0
    assert count == 0


def test_similarity_different_values_score_lower_than_identical() -> None:
    identical_score, _ = _combine_pair_similarity_metrics(
        {"forty_yard_dash": 4.4}, {"forty_yard_dash": 4.4}
    )
    different_score, _ = _combine_pair_similarity_metrics(
        {"forty_yard_dash": 4.4}, {"forty_yard_dash": 5.5}
    )

    assert different_score < identical_score


def test_non_null_measurements_removes_none_values() -> None:
    row = {
        "forty_yard_dash": 4.4,
        "bench_press_reps": None,
        "weight_lbs": 220.0,
    }

    result = _non_null_combine_measurements(row)

    assert "forty_yard_dash" in result
    assert "weight_lbs" in result
    assert "bench_press_reps" not in result


def test_non_null_measurements_all_none_returns_empty() -> None:
    row = {
        "forty_yard_dash": None,
        "bench_press_reps": None,
        "weight_lbs": None,
    }

    result = _non_null_combine_measurements(row)

    assert result == {}


def test_rank_orders_best_match_first() -> None:
    anchor = {"id": 1, "name": "Anchor", "position": "WR", "team": "DAL", "draft_year": 2022, "forty_yard_dash": 4.4}
    close = {"id": 2, "name": "Close", "position": "WR", "team": "KC", "draft_year": 2021, "forty_yard_dash": 4.4}
    far = {"id": 3, "name": "Far", "position": "WR", "team": "NE", "draft_year": 2020, "forty_yard_dash": 6.0}

    results = _rank_by_combine_similarity(anchor, [far, close], 10)

    assert results[0].name == "Close"
    assert results[1].name == "Far"


def test_rank_respects_limit() -> None:
    anchor = {"id": 1, "name": "Anchor", "position": "QB", "team": "GB", "draft_year": 2022, "forty_yard_dash": 4.5}
    player_a = {"id": 2, "name": "PlayerA", "position": "QB", "team": "DAL", "draft_year": 2020, "forty_yard_dash": 4.5}
    player_b = {"id": 3, "name": "PlayerB", "position": "QB", "team": "DAL", "draft_year": 2020, "forty_yard_dash": 4.6}
    player_c = {"id": 4, "name": "PlayerC", "position": "QB", "team": "DAL", "draft_year": 2020, "forty_yard_dash": 4.7}
    player_d = {"id": 5, "name": "PlayerD", "position": "QB", "team": "DAL", "draft_year": 2020, "forty_yard_dash": 4.8}

    results = _rank_by_combine_similarity(anchor, [player_a, player_b, player_c, player_d], 2)

    assert len(results) == 2


def test_rank_skips_candidates_with_no_combine_data() -> None:
    anchor = {"id": 1, "name": "Anchor", "position": "RB", "team": "SF", "draft_year": 2021, "forty_yard_dash": 4.4}
    no_data = {"id": 2, "name": "Empty", "position": "RB", "team": "BUF", "draft_year": 2021}

    results = _rank_by_combine_similarity(anchor, [no_data], 10)

    assert len(results) == 0


def test_prediction_identical_measurements_is_elite() -> None:
    measurements = {"forty_yard_dash": 4.4}

    block, based_on = _prediction_vs_ideal_baseline(
        prospect_measurements=measurements,
        ideal_measurements=measurements,
        ideal_name="Baseline",
    )

    assert block.success_tier == "elite_fit"
    assert block.success_score == 100.0


def test_prediction_moderate_difference_is_above_average() -> None:
    ideal = {"forty_yard_dash": 4.0}
    prospect = {"forty_yard_dash": 5.5}

    block, _ = _prediction_vs_ideal_baseline(
        prospect_measurements=prospect,
        ideal_measurements=ideal,
        ideal_name="Baseline",
    )

    assert block.success_tier == "above_average_fit"


def test_prediction_extreme_difference_is_poor() -> None:
    ideal = {"forty_yard_dash": 4.4}
    prospect = {"forty_yard_dash": 40.0}

    block, _ = _prediction_vs_ideal_baseline(
        prospect_measurements=prospect,
        ideal_measurements=ideal,
        ideal_name="Baseline",
    )

    assert block.success_tier == "poor_fit"


def test_prediction_based_on_has_correct_baseline_name() -> None:
    measurements = {"forty_yard_dash": 4.4}

    _, based_on = _prediction_vs_ideal_baseline(
        prospect_measurements=measurements,
        ideal_measurements=measurements,
        ideal_name="John Doe",
    )

    assert len(based_on) == 1
    assert based_on[0].name == "John Doe"
