import random
import numpy as np
from datetime import datetime

class TelemetryEngine:
    def __init__(self):
        self.reset_baselines()
        
    def reset_baselines(self):
        self.state = {
            'heart_rate': 72.0,
            'spo2': 98.5,
            'temperature': 36.8,
            'blood_pressure_sys': 118.0,
            'blood_pressure_dia': 78.0,
            'respiratory_rate': 14.0,
            'stress': 18.0,
            'fatigue': 12.0,
            'hydration': 96.0,
            'sleep_score': 88.0,
            'activity': 5.0
        }
        
    def generate_telemetry(self, scenario="Normal"):
        # Apply scenario effects dynamically over time
        if scenario == "High Fatigue":
            self.state['sleep_score'] = max(35, self.state['sleep_score'] - 0.4)
            self.state['fatigue'] = min(92, self.state['fatigue'] + 0.5)
            self.state['stress'] = min(75, self.state['stress'] + 0.3)
            self.state['heart_rate'] = min(88, self.state['heart_rate'] + 0.15)
        elif scenario == "Cardiac Stress":
            self.state['heart_rate'] += random.uniform(0.5, 1.8)
            self.state['stress'] = min(95, self.state['stress'] + 0.6)
            self.state['blood_pressure_sys'] += random.uniform(0.3, 1.2)
            self.state['spo2'] = max(93, self.state['spo2'] - 0.08)
        elif scenario == "Low Oxygen":
            self.state['spo2'] -= random.uniform(0.1, 0.6)
            self.state['respiratory_rate'] += random.uniform(0.1, 0.4)
            self.state['heart_rate'] += random.uniform(0.2, 0.7)
            self.state['stress'] = min(85, self.state['stress'] + 0.4)
        elif scenario == "Normal":
            # Slowly drift back to normal baselines
            self.state['heart_rate'] += (72 - self.state['heart_rate']) * 0.05
            self.state['spo2'] += (98.5 - self.state['spo2']) * 0.05
            self.state['stress'] += (18 - self.state['stress']) * 0.05
            self.state['fatigue'] += (12 - self.state['fatigue']) * 0.05
            self.state['respiratory_rate'] += (14 - self.state['respiratory_rate']) * 0.05
            self.state['blood_pressure_sys'] += (118 - self.state['blood_pressure_sys']) * 0.05
            
        # Add physiological gaussian noise
        noise = {
            'heart_rate': np.random.normal(0, 1.2),
            'spo2': np.random.normal(0, 0.15),
            'temperature': np.random.normal(0, 0.03),
            'blood_pressure_sys': np.random.normal(0, 1.5),
            'blood_pressure_dia': np.random.normal(0, 1.0),
            'respiratory_rate': np.random.normal(0, 0.3),
            'stress': np.random.normal(0, 0.8),
            'fatigue': np.random.normal(0, 0.4),
            'hydration': np.random.normal(0, 0.1),
            'sleep_score': 0,
            'activity': np.random.normal(0, 1.5)
        }
        
        telemetry = {}
        for key in self.state:
            val = self.state[key] + noise[key]
            # Ensure physiological bounds
            if key == 'spo2': val = min(100, max(0, val))
            if key in ['stress', 'fatigue', 'hydration', 'sleep_score']: val = min(100, max(0, val))
            if key == 'activity': val = max(0, val)
            telemetry[key] = round(val, 2)
            
        telemetry['scenario'] = scenario
        telemetry['timestamp'] = datetime.now().isoformat()
        
        return telemetry

    def generate_environment(self, scenario="Normal"):
        env = {
            'cabin_pressure': 14.7 + np.random.normal(0, 0.02), # psi
            'co2': 400 + np.random.normal(0, 5), # ppm
            'oxygen_level': 21.0 + np.random.normal(0, 0.05), # %
            'temperature': 22.0 + np.random.normal(0, 0.1), # C
            'humidity': 40.0 + np.random.normal(0, 0.5), # %
            'radiation': 0.5 + np.random.normal(0, 0.02) # mSv
        }
        
        if scenario == "Environmental Anomaly":
            self.env_anomaly_progression = getattr(self, 'env_anomaly_progression', 0) + 1
            env['co2'] += self.env_anomaly_progression * 15
            env['cabin_pressure'] -= self.env_anomaly_progression * 0.05
            env['oxygen_level'] -= self.env_anomaly_progression * 0.02
        else:
            self.env_anomaly_progression = 0
            
        env['scenario'] = scenario
        env['timestamp'] = datetime.now().isoformat()
        return {k: round(v, 2) if isinstance(v, float) else v for k, v in env.items()}
