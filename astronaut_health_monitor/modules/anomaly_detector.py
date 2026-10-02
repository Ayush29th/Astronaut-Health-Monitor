from datetime import datetime
import numpy as np

class AnomalyDetector:
    def __init__(self):
        self.history = []
        
    def add_telemetry(self, telemetry):
        self.history.append(telemetry)
        if len(self.history) > 100: # keep last 100 readings for moving averages
            self.history.pop(0)
            
    def check_anomalies(self, telemetry):
        anomalies = []
        
        # 1. Heart Rate
        hr = telemetry['heart_rate']
        if hr > 115:
            anomalies.append(self._create_anomaly('Heart Rate', hr, '60-100', 'CRITICAL',
                f'Heart rate ({hr} BPM) significantly above resting baseline.', 
                'Immediate rest and medical evaluation required.'))
        elif hr > 95:
            # Check if it's a sustained elevation (last 5 readings)
            if len(self.history) >= 5 and all(t['heart_rate'] > 90 for t in self.history[-5:]):
                anomalies.append(self._create_anomaly('Heart Rate', hr, '60-100', 'WARNING',
                    'Sustained elevated heart rate detected.', 
                    'Monitor for next 10 minutes. Reduce physical workload.'))
                
        # 2. SpO2
        spo2 = telemetry['spo2']
        if spo2 < 92:
            anomalies.append(self._create_anomaly('SpO2', spo2, '95-100', 'CRITICAL',
                f'Critically low blood oxygen saturation ({spo2}%).',
                'Check cabin oxygen levels. Administer supplemental oxygen if necessary.'))
        elif spo2 < 95:
             anomalies.append(self._create_anomaly('SpO2', spo2, '95-100', 'WARNING',
                'Decreasing blood oxygen trend detected.',
                'Perform deep breathing exercises. Monitor closely.'))
                
        # 3. Stress & Fatigue
        if telemetry['stress'] > 85:
             anomalies.append(self._create_anomaly('Stress', telemetry['stress'], '< 50', 'WARNING',
                'High physiological stress levels detected.',
                'Recommend psychological evaluation or physical break.'))
                
        if telemetry['fatigue'] > 80:
             anomalies.append(self._create_anomaly('Fatigue', telemetry['fatigue'], '< 60', 'WARNING',
                'Severe fatigue level predicted based on sleep and activity patterns.',
                'Mandatory rest period advised to prevent cognitive decline.'))
                
        # 4. Respiratory Rate
        rr = telemetry['respiratory_rate']
        if rr > 24:
            anomalies.append(self._create_anomaly('Respiratory Rate', rr, '12-20', 'WARNING',
                'Tachypnea detected (elevated breathing rate).',
                'Assess for physical exertion or environmental CO2 levels.'))

        return anomalies
        
    def _create_anomaly(self, param, value, expected, severity, explanation, recommendation):
        return {
            'parameter': param,
            'current_value': round(value, 2),
            'expected_range': expected,
            'severity': severity,
            'message': f"{param} Anomaly ({value})",
            'ai_explanation': explanation,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }
