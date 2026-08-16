from ai.performance_analysis import calculate_student_performance
from ai.risk_prediction import evaluate_academic_risk

def predict_performance_and_risk(student_id, target_att=None, target_assign=None, target_internal=None, target_final=None, target_desired_score=80.0):
    """
    Simulates academic score and risk status based on target / hypothetical inputs.
    Formula: 20% Attendance + 20% Assignment + 20% Internal + 40% Final Exam
    """
    base_perf = calculate_student_performance(student_id)
    if not base_perf:
        return None

    target_desired_score = float(target_desired_score or 80.0)

    # Default to actual values if not supplied
    att = float(target_att) if target_att is not None else base_perf['att_pct']
    assign = float(target_assign) if target_assign is not None else base_perf['assign_score']
    internal = float(target_internal) if target_internal is not None else base_perf['internal_score']
    final = float(target_final) if target_final is not None else base_perf['final_score']

    # Clamp values between 0 and 100
    att = max(0.0, min(100.0, att))
    assign = max(0.0, min(100.0, assign))
    internal = max(0.0, min(100.0, internal))
    final = max(0.0, min(100.0, final))

    # Calculate predicted composite overall score
    predicted_overall = round(
        (att * 0.20) + 
        (assign * 0.20) + 
        (internal * 0.20) + 
        (final * 0.40), 1
    )

    # Mock performance object to run risk prediction evaluator
    simulated_perf = dict(base_perf)
    simulated_perf['att_pct'] = att
    simulated_perf['assign_score'] = assign
    simulated_perf['internal_score'] = internal
    simulated_perf['final_score'] = final
    simulated_perf['overall_score'] = predicted_overall

    # Update subject scores based on simulated final score
    sim_subjects = []
    sim_weak = []
    for sub in base_perf.get('subject_performance', []):
        sim_score = max(sub['score'], final)
        sub_copy = dict(sub)
        sub_copy['score'] = sim_score
        if sim_score < 60:
            sim_weak.append(sub_copy)
        sim_subjects.append(sub_copy)
    
    simulated_perf['subject_performance'] = sim_subjects
    simulated_perf['weak_subjects'] = sim_weak

    # Recalculate trend if prev_mark exists
    prev_mark = base_perf.get('prev_mark')
    if prev_mark is not None:
        sim_delta = round(final - prev_mark, 1)
        simulated_perf['trend_delta'] = sim_delta
        if sim_delta <= -5.0:
            simulated_perf['trend_status'] = "Declining"
        elif sim_delta >= 5.0:
            simulated_perf['trend_status'] = "Improving"
        else:
            simulated_perf['trend_status'] = "Stable"

    predicted_risk = evaluate_academic_risk(simulated_perf)

    # Calculate targets required to achieve LOW RISK (overall >= 75 and attendance >= 75)
    target_att_needed = max(75.0, att)
    fixed_component = (target_att_needed * 0.20) + (assign * 0.20) + (internal * 0.20)
    needed_for_75 = max(0.0, 75.0 - fixed_component)
    required_final_for_low_risk = round(needed_for_75 / 0.40, 1)

    # Calculate required final exam score delta to hit user's target_desired_score
    fixed_current_comp = (att * 0.20) + (assign * 0.20) + (internal * 0.20)
    needed_for_target = max(0.0, target_desired_score - fixed_current_comp)
    required_final_for_target = round(needed_for_target / 0.40, 1)
    required_final_delta = round(required_final_for_target - base_perf['final_score'], 1)

    return {
        'base_perf': base_perf,
        'simulated_inputs': {
            'att': att,
            'assign': assign,
            'internal': internal,
            'final': final,
            'target_desired_score': target_desired_score
        },
        'predicted_overall': predicted_overall,
        'predicted_risk': predicted_risk,
        'target_att_needed': target_att_needed,
        'required_final_for_low_risk': min(100.0, required_final_for_low_risk),
        'is_low_risk_achievable': required_final_for_low_risk <= 100.0,
        'target_desired_score': target_desired_score,
        'required_final_for_target': min(100.0, required_final_for_target),
        'required_final_delta': required_final_delta,
        'chart_comparison': {
            'labels': ['Current Overall', 'Predicted Overall', 'Target Goal'],
            'values': [base_perf['overall_score'], predicted_overall, target_desired_score]
        }
    }

