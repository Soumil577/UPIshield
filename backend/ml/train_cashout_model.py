
"""
Standalone training and evaluation script for the Cash-Out Location Predictor.
"""

from backend.ml.cashout_predictor import predictor


def run_training_and_evaluation():
    print("=" * 60)
    print("SIH26184: Training Cash-Out Location Predictor")
    print("=" * 60)
    
    predictor._train_default_model()
    if predictor.is_trained:
        print("[SUCCESS] GradientBoosting model trained successfully on synthetic historical cashouts.")
    else:
        print("[WARNING] Model initialized with heuristic calibration.")

    test_coord = (28.7100, 77.1200)
    predictions = predictor.predict_top_locations(case_amount=270000.0, last_known_coord=test_coord, top_k=4)

    print("\n--- SAMPLE INFERENCE TEST (Target: CASE-2026-4401, Amount: Rs 2,70,000) ---")
    for item in predictions:
        print(f"Rank #{item['rank']} | {item['name']} ({item['type']})")
        print(f"  Confidence: {item['probability_score']}% [{item['risk_level']}] | Distance: {item['distance_km']} km")
        print(f"  Time Window: {item['estimated_time_window']}")
        print(f"  Reasons: {', '.join(item['reason_factors'])}")
        print()


if __name__ == "__main__":
    run_training_and_evaluation()

