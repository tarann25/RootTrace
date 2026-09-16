import re
from datetime import timedelta
from typing import List, Dict, Set
from urllib.parse import urlparse
from src.schema import CanonicalEventRecord

DOMAIN_REGEX = re.compile(r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')
URL_REGEX = re.compile(r'https?://[^\s\'"<>]+')
IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

IGNORED_DOMAINS = {
    "sts.amazonaws.com", "amazonaws.com", "w3.org", "schema.org", "example.com"
}
IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".php", ".html", ".htm", ".css", ".js", ".json", ".txt", ".log", ".ico"
}

def extract_domains(text: str) -> Set[str]:
    """Dynamically extracts domains from text and URLs, filtering noise."""
    domains = set()
    if not text:
        return domains
        
    # Extract from full URLs first
    for match in URL_REGEX.findall(text):
        try:
            parsed = urlparse(match)
            hostname = parsed.hostname
            if hostname and hostname.lower() not in IGNORED_DOMAINS:
                domains.add(hostname.lower())
        except Exception:
            pass
            
    # Extract from standalone domain mentions (e.g. DNS queries or email domains)
    for match in DOMAIN_REGEX.findall(text):
        lowered = match.lower()
        if (
            lowered not in IGNORED_DOMAINS 
            and not lowered.endswith(".internal")
            and not any(lowered.endswith(ext) for ext in IGNORED_EXTENSIONS)
        ):
            # Avoid matching pure IP strings
            if not IP_REGEX.match(lowered):
                domains.add(lowered)
                
    return domains

def extract_entities_from_event(event: CanonicalEventRecord) -> Set[str]:
    """Dynamically extracts all identity, network, and resource entities from an event."""
    entities: Set[str] = set()

    # 1. User & Identity
    if event.user:
        entities.add(f"user:{event.user.strip().lower()}")

    # Check metadata for additional identities
    if isinstance(event.metadata, dict):
        recipient = event.metadata.get("recipient")
        if recipient and "@" in recipient:
            user_part = recipient.split("@")[0].lower()
            entities.add(f"user:{user_part}")
            
        target_user = event.metadata.get("target_user")
        if target_user:
            entities.add(f"user:{target_user.strip().lower()}")

    # 2. Network: Source IP and metadata IPs
    if event.source_ip:
        entities.add(f"ip:{event.source_ip.strip()}")

    if isinstance(event.metadata, dict):
        for key in ["sender_ip", "response_ip", "client_ip", "srcip", "destination_ip"]:
            val = event.metadata.get(key)
            if val and isinstance(val, str) and IP_REGEX.match(val):
                entities.add(f"ip:{val.strip()}")

    # 3. Domains & URLs
    raw_str = str(event.raw_ref) if event.raw_ref else ""
    meta_str = str(event.metadata) if event.metadata else ""
    combined_text = f"{raw_str} {meta_str}"
    
    extracted_domains = extract_domains(combined_text)
    for domain in extracted_domains:
        entities.add(f"domain:{domain}")

    return entities

class IncidentCluster:
    def __init__(self, cluster_id: str):
        self.cluster_id = cluster_id
        self.events: List[CanonicalEventRecord] = []
        self.entities: Set[str] = set()
        
    def add_event(self, event: CanonicalEventRecord):
        if event not in self.events:
            self.events.append(event)
            event_entities = extract_entities_from_event(event)
            self.entities.update(event_entities)

    def merge(self, other_cluster: 'IncidentCluster'):
        for event in other_cluster.events:
            self.add_event(event)

    def to_dict(self):
        # Sort events chronologically
        sorted_events = sorted(self.events, key=lambda x: x.timestamp_utc.replace(tzinfo=None) if x.timestamp_utc.tzinfo else x.timestamp_utc)
        return {
            "cluster_id": self.cluster_id,
            "entities": sorted(list(self.entities)),
            "events": [e.model_dump() for e in sorted_events]
        }

def correlate_events(events: List[CanonicalEventRecord]) -> List[IncidentCluster]:
    """
    Dynamic correlation logic joining events by shared identity, network, or domain entities.
    """
    clusters: List[IncidentCluster] = []
    
    for event in events:
        matched_clusters = []
        current_entities = extract_entities_from_event(event)
            
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
                    if other in clusters:
                        clusters.remove(other)
                        
    return clusters

def time_window_clustering(events: List[CanonicalEventRecord], window_minutes: int = 15) -> List[List[CanonicalEventRecord]]:
    """
    Sliding Time-Window Clustering:
    Groups a list of events into temporal clusters where events occur within X minutes of the previous one.
    """
    if not events:
        return []
        
    def get_naive(dt):
        return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt

    sorted_events = sorted(events, key=lambda x: get_naive(x.timestamp_utc))
    temporal_clusters = []
    current_cluster = [sorted_events[0]]
    
    for event in sorted_events[1:]:
        time_diff = get_naive(event.timestamp_utc) - get_naive(current_cluster[-1].timestamp_utc)
        if time_diff <= timedelta(minutes=window_minutes):
            current_cluster.append(event)
        else:
            temporal_clusters.append(current_cluster)
            current_cluster = [event]
            
    temporal_clusters.append(current_cluster)
    return temporal_clusters
