from modules.database import save_alert, get_active_alerts
import pandas as pd

class AlertManager:
    def __init__(self):
        pass
        
    def process_anomalies(self, anomalies):
        """
        Takes detected anomalies and creates database alerts if they don't already exist 
        for that specific parameter in an ACTIVE state.
        """
        if not anomalies:
            return
            
        current_active_df = get_active_alerts()
        active_params = set()
        
        if not current_active_df.empty:
            active_params = set(current_active_df['parameter'].tolist())
            
        for anomaly in anomalies:
            # Simple dedup mechanism - don't fire if an alert for this parameter is already active
            if anomaly['parameter'] not in active_params:
                save_alert(anomaly)
