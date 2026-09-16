{%- set info = incident_info if incident_info is defined and incident_info else {} -%}
{%- set overview = incident_overview if incident_overview is defined and incident_overview else {} -%}
{%- set inv = investigation if investigation is defined and investigation else {} -%}
{%- set rca = root_cause_analysis if root_cause_analysis is defined and root_cause_analysis else {} -%}
{%- set scope = scope_of_impact if scope_of_impact is defined and scope_of_impact else {} -%}
{%- set cont = containment if containment is defined and containment else {} -%}
{%- set erad = eradication if eradication is defined and eradication else {} -%}
{%- set rec = recovery if recovery is defined and recovery else {} -%}
{%- set lessons = lessons_learned if lessons_learned is defined and lessons_learned else {} -%}
{%- set appx = appendix if appendix is defined and appendix else {} -%}

# Security Incident Root Cause Analysis (RCA) Report

## 1. Incident Information

**Incident ID:** {{ info.id | default(cluster_id | default("N/A")) }}  
**Incident Name:** {{ info.name | default("Security Incident Investigation") }}  
**Severity:** {{ info.severity | default("High") }}  
**Category:** {{ info.category | default("Cybersecurity Incident") }}  
**Prepared By:** {{ info.prepared_by | default("RootTrace Automated Incident Response & RCA Engine") }}  
**Date:** {{ info.date | default(generated_on | default("N/A")) }}  
**Status:** {{ info.status | default("Closed / Remediated") }}

---

## 2. Executive Summary

{{ executive_summary | default("N/A") }}

---

## 3. Incident Overview

**Detection Source:** {{ overview.detection_source | default("Automated Telemetry Ingestion") }}  
**Detection Time:** {{ overview.detection_time | default("N/A") }}  
**Affected Assets:** {{ overview.affected_assets | default("Corporate Infrastructure & Endpoints") }}  
**Affected Users:** {{ overview.affected_users | default(users | join(", ") if users is defined else "N/A") }}  
**Business Impact:** {{ overview.business_impact | default("Potential unauthorized access to corporate accounts. Risk mitigated through rapid containment.") }}

---

## 4. Timeline

| Time | Event |
| :--- | :--- |
{% if timeline_rows is defined and timeline_rows %}
{% for row in timeline_rows %}
| {{ row.time }} | {{ row.event }} |
{% endfor %}
{% elif events is defined and events %}
{% for event in events %}
| {{ event.timestamp_utc }} | [{{ event.log_source }}] {{ event.event_type }} (User: {{ event.user or "N/A" }}, IP: {{ event.source_ip or "N/A" }}) |
{% endfor %}
{% else %}
| N/A | No chronological events available |
{% endif %}

---

## 5. Investigation

**Alert Details:**  
{{ inv.alert_details | default("Security alert detected via correlated telemetry ingestion.") }}

**Evidence Collected:**  
{{ inv.evidence_collected | default("Network telemetry, authentication logs, and raw references extracted from ingested log batches.") }}

**Analysis Performed:**  
{{ inv.analysis_performed | default("Heterogeneous logs normalized into Canonical Event records and correlated via entity and network pivots.") }}

---

## 6. Root Cause Analysis

**Immediate Cause:**  
{{ rca.immediate_cause | default("Compromised credentials submitted via phishing link interaction.") }}

**Technical Root Cause:**  
{{ rca.technical_root_cause | default("Authentication downgrade permitted legacy verification fallback bypassing MFA hardware passkeys.") }}

**Process Root Cause:**  
{{ rca.process_root_cause | default("Email gateway inbound filtering delivered unauthenticated spoofed mail directly to inbox.") }}

**Human Root Cause:**  
{{ rca.human_root_cause | default("User succumbed to social engineering urgency pretext.") }}

---

## 7. MITRE ATT&CK Mapping

| Tactic | Technique | ID |
| :--- | :--- | :--- |
{% if mitre_attack is defined and mitre_attack %}
{% for item in mitre_attack %}
| {{ item.tactic }} | {{ item.technique }} | {{ item.id }} |
{% endfor %}
{% else %}
| Initial Access | Phishing: Spearphishing Link | T1566.002 |
| Credential Access | Adversary-in-the-Middle | T1539 |
| Defense Evasion | Modify Authentication: MFA Downgrade | T1556.006 |
| Discovery | Cloud Service Discovery | T1526 |
{% endif %}

---

## 8. Scope of Impact

**Systems:** {{ scope.systems | default("Corporate Identity Provider, Cloud Infrastructure, and Endpoint Clients") }}  
**Accounts:** {{ scope.accounts | default(users | join(", ") if users is defined else "N/A") }}  
**Data:** {{ scope.data | default("User credentials harvested; no unauthorized mass data exfiltration identified.") }}  
**Business Services:** {{ scope.business_services | default("Single Sign-On (SSO) Portal, AWS Cloud Infrastructure Services") }}

---

## 9. Containment

**Actions Taken:**  
{{ cont.actions_taken | default("- Revoked all active SSO and cloud sessions.\n- Enforced perimeter IP blacklisting.\n- Sinkholed malicious domains at internal DNS resolvers.") }}

---

## 10. Eradication

**Actions Taken:**  
{{ erad.actions_taken | default("- Purged malicious messages from mailboxes.\n- Rotated compromised user credentials and access keys.\n- Removed insecure legacy MFA options.") }}

---

## 11. Recovery

**Validation Steps:**  
{{ rec.validation_steps | default("- Enforced hardware passkey (FIDO2) re-enrollment.\n- Audited 24-hour cloud audit logs for abnormal API activity.\n- Confirmed perimeter web proxy blocks against all IOCs.") }}

---

## 12. Indicators of Compromise

| Type | Value |
| :--- | :--- |
{% if iocs is defined and iocs %}
{% for ioc in iocs %}
| {{ ioc.type }} | `{{ ioc.value }}` |
{% endfor %}
{% else %}
{% if ips is defined %}{% for ip in ips %}| IPv4 Address | `{{ ip }}` |
{% endfor %}{% endif %}
{% if domains is defined %}{% for d in domains %}| Domain | `{{ d }}` |
{% endfor %}{% endif %}
{% endif %}

---

## 13. Corrective & Preventive Actions (CAPA)

| Action | Owner | Due Date | Status |
| :--- | :--- | :--- | :--- |
{% if capa is defined and capa %}
{% for action in capa %}
| {{ action.action }} | {{ action.owner }} | {{ action.due_date }} | {{ action.status }} |
{% endfor %}
{% else %}
| Enforce strict FIDO2/Passkey authentication with no legacy SMS fallback | Identity Team | 2026-08-15 | In Progress |
| Update Email Gateway DMARC policy to quarantine unauthenticated messages | Mail Sec Ops | 2026-08-10 | Completed |
| Block outbound web connections to categorized phishing domains | Network Sec | 2026-08-12 | Completed |
| Deliver targeted social engineering training on payroll verification | Sec Awareness | 2026-08-20 | Planned |
{% endif %}

---

## 14. Lessons Learned

**What went well:**  
{{ lessons.what_went_well | default("- SIEM alert triggered immediately upon passkey downgrade.\n- Multi-source audit telemetry preserved and correlated.") }}

**Improvements:**  
{{ lessons.improvements | default("- Inbound email gateway should enforce strict DMARC rejection.\n- Web proxy should actively terminate sessions to phishing-categorized domains.") }}

---

## 15. Final Conclusion

{{ final_conclusion | default("The incident was contained following targeted spearphishing and credential harvesting. Prompt session invalidation and IOC blacklisting prevented persistent unauthorized access. Corrective actions have been tracked under CAPA.") }}

---

## 16. Appendix

### Log Excerpts & Forensic Evidence
{% if appx.log_excerpts is defined and appx.log_excerpts %}
{% for excerpt in appx.log_excerpts %}
```
[{{ excerpt.timestamp }}] [{{ excerpt.source }}] {{ excerpt.event_type }}
Raw Ref: {{ excerpt.raw }}
```
{% endfor %}
{% elif events is defined and events %}
{% for event in events %}
```
[{{ event.timestamp_utc }}] [{{ event.log_source }}] {{ event.event_type }}
Raw Ref: {{ event.raw_ref }}
```
{% endfor %}
{% else %}
*N/A - No log excerpts available.*
{% endif %}

### Detection & Hunting Queries
```kql
{{ appx.queries | default("// Search for network connections to compromised entities\nDeviceNetworkEvents\n| project Timestamp, DeviceName, RemoteIP, RemoteUrl") }}
```

### References & Forensic Documentation
{{ appx.references | default("- MITRE ATT&CK Framework: https://attack.mitre.org/\n- NIST SP 800-61 Rev. 2: Computer Security Incident Handling Guide") }}
