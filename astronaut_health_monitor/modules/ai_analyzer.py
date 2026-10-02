class AIAnalyzer:
    def analyze_health(self, telemetry, anomalies):
        # Calculate base component scores (100 is perfect)
        hr_score = max(0, 100 - abs(telemetry['heart_rate'] - 72) * 1.5)
        spo2_score = max(0, 100 - (100 - telemetry['spo2']) * 5)
        stress_score = max(0, 100 - telemetry['stress'])
        fatigue_score = max(0, 100 - telemetry['fatigue'])
        sleep_score = telemetry['sleep_score']
        
        # Weighted average for overall health score
        health_score = (hr_score * 0.25 + spo2_score * 0.30 + stress_score * 0.15 + 
                        fatigue_score * 0.15 + sleep_score * 0.15)
                        
        cardiovascular_risk = min(100, 100 - hr_score + (telemetry['stress'] * 0.2))
        respiratory_risk = min(100, 100 - spo2_score)
        recovery_score = (sleep_score + (100 - telemetry['fatigue'])) / 2
        
        risk_level = "LOW"
        if health_score < 65 or len([a for a in anomalies if a['severity'] == 'CRITICAL']) > 0:
            risk_level = "CRITICAL"
        elif health_score < 82 or len(anomalies) > 0:
            risk_level = "ELEVATED"
            
        factors = []
        if hr_score < 80: factors.append(f"Heart rate deviation ({telemetry['heart_rate']} BPM)")
        if spo2_score < 85: factors.append(f"Sub-optimal blood oxygen ({telemetry['spo2']}%)")
        if fatigue_score < 75: factors.append(f"High cumulative fatigue ({telemetry['fatigue']}%)")
        if stress_score < 80: factors.append(f"Elevated physiological stress ({telemetry['stress']})")
        if sleep_score < 70: factors.append(f"Poor sleep quality score ({telemetry['sleep_score']})")
        
        if not factors:
            factors.append("All metrics within nominal baseline ranges.")
            explanation = "The astronaut's telemetry indicates a stable physiological state. Cardiovascular and respiratory metrics are tracking closely to established baselines without significant deviation."
        else:
            explanation = f"Detected {len(factors)} sub-optimal physiological factors. "
            if cardiovascular_risk > 50:
                explanation += "Cardiovascular strain is evident, likely due to physical exertion or acute stress response. "
            if respiratory_risk > 40:
                explanation += "Respiratory efficiency has decreased, requiring monitoring. "
            if recovery_score < 60:
                explanation += "Recovery metrics indicate a growing sleep deficit which may impair cognitive function."
                
        return {
            'health_score': int(health_score),
            'risk_level': risk_level,
            'cardiovascular_risk': int(cardiovascular_risk),
            'respiratory_risk': int(respiratory_risk),
            'fatigue_probability': int(telemetry['fatigue']),
            'stress_level': int(telemetry['stress']),
            'recovery_score': int(recovery_score),
            'explanation': explanation,
            'contributing_factors': factors
        }
