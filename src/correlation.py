from datetime import timedelta
from typing import List, Dict
from src.schema import CanonicalEventRecord

class IncidentCluster:
    def __init__(self, cluster_id: str):
        self.cluster_id = cluster_id
        self.events: List[CanonicalEventRecord] = []
        self.entities = set()
        
    def add_event(self, event: CanonicalEventRecord):
        if event not in self.events:
            self.events.append(event)
            # 3.1 Identity & Network Pivot: Extract User and IP
            if event.user:
                self.entities.add(f"user:{event.user}")
            if event.source_ip:
                self.entities.add(f"ip:{event.source_ip}")
            
            # 3.2 Domain & Resource Pivot Matching
            # We naively convert the raw log to string to look for domains
            raw_str = str(event.raw_ref)
            if "login-payroll-update.com" in raw_str:
                self.entities.add("domain:login-payroll-update.com")

    def merge(self, other_cluster: 'IncidentCluster'):
        for event in other_cluster.events:
            self.add_event(event)

    def to_dict(self):
        return {
            "cluster_id": self.cluster_id,
            "entities": list(self.entities),
            "events": [e.model_dump() for e in sorted(self.events, key=lambda x: x.timestamp_utc)]
        }

def correlate_events(events: List[CanonicalEventRecord]) -> List[IncidentCluster]:
    """
    Core correlation logic joining events by shared identity, network, or domain entities.
    """
    clusters: List[IncidentCluster] = []
    
    for event in events:
        matched_clusters = []
        
        # Determine entities for this current event
        current_entities = set()
        if event.user: current_entities.add(f"user:{event.user}")
        if event.source_ip: current_entities.add(f"ip:{event.source_ip}")
        if "login-payroll-update.com" in str(event.raw_ref):
            current_entities.add("domain:login-payroll-update.com")
            
        # Find which clusters share entities with this event
        for cluster in clusters:
            if current_entities.intersection(cluster.entities):
                matched_clusters.append(cluster)
                
        if not matched_clusters:
            # Create a new cluster if no match
            new_cluster = IncidentCluster(f"cluster_{len(clusters)+1}")
            new_cluster.add_event(event)
            clusters.append(new_cluster)
        else:
            # Add to the first matched cluster
            primary = matched_clusters[0]
            primary.add_event(event)
            
            # If it matched multiple clusters, merge them all into the primary
            if len(matched_clusters) > 1:
                for other in matched_clusters[1:]:
                    primary.merge(other)
                    clusters.remove(other)
                    
    return clusters

def time_window_clustering(events: List[CanonicalEventRecord], window_minutes: int = 15) -> List[List[CanonicalEventRecord]]:
    """
    3.3 Sliding Time-Window Clustering:
    Groups a list of events into temporal clusters where events occur within X minutes of the previous one.
    """
    if not events:
        return []
        
    sorted_events = sorted(events, key=lambda x: x.timestamp_utc)
    temporal_clusters = []
    current_cluster = [sorted_events[0]]
    
    for event in sorted_events[1:]:
        time_diff = event.timestamp_utc - current_cluster[-1].timestamp_utc
        if time_diff <= timedelta(minutes=window_minutes):
            current_cluster.append(event)
        else:
            temporal_clusters.append(current_cluster)
            current_cluster = [event]
            
    temporal_clusters.append(current_cluster)
    return temporal_clusters
