export const DEMO_INCIDENT = {
  id: "DEMO-CLUSTER-01",
  title: "Phishing-to-Cloud Reconnaissance Investigation",
  status: "completed",
  created_at: new Date().toISOString(),
  summary: "On August 05, 2026, a security incident was detected involving unauthorized identity access and cloud reconnaissance targeting corporate user 'tsingh'. The initial attack vector was an inbound phishing email containing a spoofed direct deposit verification link. Following credential submission on an external domain, authentication was achieved via legacy SMS fallback bypassing enrolled FIDO2 passkeys from a Dutch VPN exit node. Subsequent AWS CloudTrail telemetry confirmed unauthorized reconnaissance (GetCallerIdentity). Rapid containment revoked active sessions and blacklisted pivot IOCs.",
  metrics: {
    total_events: 6,
    compromised_users: 1,
    malicious_ips: 3,
    phishing_domains: 3,
    duration_minutes: 8.3
  },
  entities: {
    users: ["tsingh"],
    ips: ["10.0.1.50", "103.21.244.12", "198.51.100.42"],
    domains: ["attacker-redirect.com", "login-payroll-update.com", "mail.attacker-redirect.com"]
  },
  events: [
    {
      id: "demo-evt-1",
      log_source: "email_gateway",
      event_type: "email_reception",
      timestamp_utc: "2026-08-05 14:00:10 UTC",
      user: "tsingh",
      source_ip: "198.51.100.42",
      host: "mail.attacker-redirect.com",
      metadata: {
        sender: "hr-update@attacker-redirect.com",
        header_from: "hr-department@corp.internal",
        subject: "URGENT: Verify Your Direct Deposit Information",
        spf: "softfail",
        dkim: "fail",
        dmarc: "fail",
        url: "http://login-payroll-update.com/auth/login.php?id=99281",
        action: "delivered_to_inbox"
      },
      raw_ref: '{"timestamp": "2026-08-05T14:00:10.120Z", "sender": "hr-update@attacker-redirect.com", "subject": "URGENT: Verify Your Direct Deposit Information", "auth": "spf=softfail dkim=fail dmarc=fail"}'
    },
    {
      id: "demo-evt-2",
      log_source: "dns_query",
      event_type: "dns_query",
      timestamp_utc: "2026-08-05 14:02:15 UTC",
      user: null,
      source_ip: "10.0.1.50",
      host: "internal_dns_resolver",
      metadata: {
        query: "login-payroll-update.com",
        qtype: "A",
        client: "10.0.1.50#52140"
      },
      raw_ref: "05-Aug-2026 14:02:15.104 client 10.0.1.50#52140 (login-payroll-update.com): query: login-payroll-update.com IN A + (10.0.1.1)"
    },
    {
      id: "demo-evt-3",
      log_source: "dns_query",
      event_type: "dns_response",
      timestamp_utc: "2026-08-05 14:02:15 UTC",
      user: null,
      source_ip: "10.0.1.50",
      host: "internal_dns_resolver",
      metadata: {
        query: "login-payroll-update.com",
        response_status: "NOERROR",
        response_ip: "103.21.244.12"
      },
      raw_ref: "05-Aug-2026 14:02:15.188 client 10.0.1.50#52140 (login-payroll-update.com): response: NOERROR 103.21.244.12"
    },
    {
      id: "demo-evt-4",
      log_source: "web_proxy",
      event_type: "phishing_attempt",
      timestamp_utc: "2026-08-05 14:02:18 UTC",
      user: "tsingh",
      source_ip: "10.0.1.50",
      host: "web_proxy_gateway",
      metadata: {
        method: "POST",
        url: "http://login-payroll-update.com/auth/login.php?id=99281",
        category: "Phishing",
        action_status: "allowed"
      },
      raw_ref: '10.0.1.50 - tsingh [05/Aug/2026:14:02:18 +0000] "POST /auth/login.php HTTP/1.1" 200 1420 "http://login-payroll-update.com/auth/login.php?id=99281" CATEGORY="Phishing" ACTION="allowed"'
    },
    {
      id: "demo-evt-5",
      log_source: "wazuh",
      event_type: "High Risk Identity Sign-in: Successful login via known malicious VPN exit node with passkey bypass / downgrade.",
      timestamp_utc: "2026-08-05 14:05:10 UTC",
      user: "tsingh",
      source_ip: "198.51.100.42",
      host: "idp-sso-gateway",
      metadata: {
        auth_method: "Password_Plus_SMS_Fallback",
        passkey_status: "BYPASSED_VIA_DOWNGRADE",
        vpn_provider: "Mullvad_VPN_Exit_Node",
        device: "Linux x86_64",
        browser: "Firefox 128.0"
      },
      raw_ref: '{"rule": {"id": "88204", "description": "High Risk Identity Sign-in: Successful login via known malicious VPN exit node with passkey bypass / downgrade."}, "network": {"srcip": "198.51.100.42", "vpn_provider": "Mullvad_VPN_Exit_Node"}}'
    },
    {
      id: "demo-evt-6",
      log_source: "cloudtrail",
      event_type: "GetCallerIdentity",
      timestamp_utc: "2026-08-05 14:08:30 UTC",
      user: "tsingh",
      source_ip: "198.51.100.42",
      host: "us-east-1",
      metadata: {
        arn: "arn:aws:iam::123456789012:user/tsingh",
        account_id: "123456789012",
        user_agent: "aws-cli/2.15.0 Python/3.11.8 Linux/6.6.0-fedora-x86_64"
      },
      raw_ref: '{"eventVersion": "1.08", "eventName": "GetCallerIdentity", "awsRegion": "us-east-1", "sourceIPAddress": "198.51.100.42", "userIdentity": {"userName": "tsingh"}}'
    }
  ],
  report_markdown: `# Security Incident Root Cause Analysis (RCA) Report

## 1. Incident Information

**Incident ID:** CLUSTER_1  
**Incident Name:** Spearphishing & Credential Harvest / Account Takeover Incident  
**Severity:** Critical  
**Category:** Spearphishing & Credential Harvest / Account Takeover  
**Prepared By:** RootTrace Automated Incident Response & RCA Engine  
**Date:** 2026-09-16 09:45:32 UTC  
**Status:** Closed / Remediated

---

## 2. Executive Summary

On August 05, 2026, a security incident was detected involving unauthorized identity access and cloud reconnaissance targeting corporate user 'tsingh'. The initial attack vector was an inbound phishing email containing a spoofed direct deposit verification link. Following credential submission on an external domain, authentication was achieved via legacy SMS fallback bypassing enrolled FIDO2 passkeys from a Dutch VPN exit node. Subsequent AWS CloudTrail telemetry confirmed unauthorized reconnaissance (GetCallerIdentity). Rapid containment revoked active sessions and blacklisted pivot IOCs.

---

## 3. Incident Overview

**Detection Source:** EMAIL_GATEWAY (email_reception)  
**Detection Time:** 2026-08-05 14:00:10 UTC  
**Affected Assets:** AWS Account: 123456789012, arn:aws:iam::123456789012:user/tsingh, idp-sso-gateway, internal_dns_resolver, mail.attacker-redirect.com, us-east-1, web_proxy_gateway  
**Affected Users:** tsingh  
**Business Impact:** Unauthorized access to corporate identity and AWS cloud environment. Risk of lateral movement and privilege escalation; no confirmed data breach.

---

## 4. Timeline

| Time | Event |
| :--- | :--- |
| 2026-08-05 14:00:10 UTC | [email_gateway] email_reception (User: tsingh, IP: 198.51.100.42) |
| 2026-08-05 14:02:15 UTC | [dns_query] dns_query (IP: 10.0.1.50) |
| 2026-08-05 14:02:15 UTC | [dns_query] dns_response (IP: 10.0.1.50) |
| 2026-08-05 14:02:18 UTC | [web_proxy] phishing_attempt (User: tsingh, IP: 10.0.1.50) |
| 2026-08-05 14:05:10 UTC | [wazuh] High Risk Identity Sign-in: Successful login via known malicious VPN exit node with passkey bypass / downgrade. (User: tsingh, IP: 198.51.100.42) |
| 2026-08-05 14:08:30 UTC | [cloudtrail] GetCallerIdentity (User: tsingh, IP: 198.51.100.42) |

---

## 5. Investigation

**Alert Details:**  
- Email Gateway: Inbound spoofed message from 'hr-update@attacker-redirect.com' disguised as 'hr-department@corp.internal' (Auth: {'spf': 'softfail', 'dkim': 'fail', 'dmarc': 'fail'})
- Wazuh SIEM Alert: High Risk Identity Sign-in: Successful login via known malicious VPN exit node with passkey bypass / downgrade. (Target: tsingh, Source IP: 198.51.100.42, Auth Method: Password_Plus_SMS_Fallback, Passkey Status: BYPASSED_VIA_DOWNGRADE)

**Evidence Collected:**  
- DNS Resolution: Query for 'login-payroll-update.com' resolved to '103.21.244.12'
- Web Proxy: POST request to credential harvester 'http://login-payroll-update.com/auth/login.php?id=99281' categorized as 'Phishing'
- AWS CloudTrail: STS API call 'GetCallerIdentity' by IAM user 'tsingh' from IP '198.51.100.42' using 'aws-cli/2.15.0 Python/3.11.8 Linux/6.6.0-fedora-x86_64'

**Analysis Performed:**  
1. Ingested heterogeneous telemetry across 5 independent log sources.
2. Normalized all log entries into a standardized Canonical Event schema with microsecond-level UTC timestamps.
3. Correlated disparate events through pivot chaining: shared username ('tsingh'), malicious source IP ('10.0.1.50'), and phishing domain ('attacker-redirect.com').
4. Reconstructed the full attack chain from initial phishing delivery, internal DNS query, web proxy POST, IdP passkey downgrade bypass, to cloud reconnaissance.

---

## 6. Root Cause Analysis

**Immediate Cause:**  
Target user 'tsingh' received an urgent phishing email, navigated to a spoofed payroll login page, and submitted their credentials.

**Technical Root Cause:**  
The corporate Identity Provider permitted a legacy MFA fallback (SMS verification) when passkey verification was bypassed; additionally, the corporate perimeter proxy categorized the external payroll URL as Phishing but marked action as 'allowed'.

**Process Root Cause:**  
Email gateway configuration allowed messages with SPF softfail, DKIM fail, and DMARC fail to be delivered directly into the employee inbox ('delivered_to_inbox') rather than being quarantined or rejected.

**Human Root Cause:**  
The user fell victim to social engineering utilizing an urgency pretext related to payroll and direct deposit verification.

---

## 7. MITRE ATT&CK Mapping

| Tactic | Technique | ID |
| :--- | :--- | :--- |
| Initial Access | Phishing: Spearphishing Link | T1566.002 |
| Execution | User Execution: Malicious Link | T1204.001 |
| Credential Access | Adversary-in-the-Middle / Phishing | T1539 |
| Defense Evasion | Modify Authentication: MFA Downgrade | T1556.006 |
| Command and Control | Proxy: Anonymization Network / VPN | T1090.003 |
| Discovery | Cloud Service Discovery: GetCallerIdentity | T1526 |

---

## 8. Scope of Impact

**Systems:** AWS Account: 123456789012, arn:aws:iam::123456789012:user/tsingh, idp-sso-gateway, internal_dns_resolver, mail.attacker-redirect.com, us-east-1, web_proxy_gateway  
**Accounts:** Corporate Identity: tsingh, AWS IAM User: tsingh  
**Data:** Target user credentials harvested. AWS STS caller identity and account infrastructure metadata exposed. No confirmed unauthorized mass data exfiltration.  
**Business Services:** Single Sign-On (SSO) authentication gateway, Corporate Email routing, AWS Cloud infrastructure services.

---

## 9. Containment

**Actions Taken:**  
- Revoked all active SSO and AWS IAM sessions for user 'tsingh'.
- Implemented perimeter firewall blocks on IP addresses: 10.0.1.50, 103.21.244.12, 198.51.100.42.
- Sinkholed and blacklisted malicious domains: attacker-redirect.com, login-payroll-update.com, mail.attacker-redirect.com at internal DNS resolvers.
- Invalidated all pending MFA verification tokens and active session cookies.

---

## 10. Eradication

**Actions Taken:**  
- Purged malicious phishing email messages referencing sender 'attacker-redirect.com' from all organization mailboxes.
- Removed legacy SMS MFA fallback options from the compromised user's identity profile.
- Rotated AWS IAM user access keys and Active Directory passwords for 'tsingh'.

---

## 11. Recovery

**Validation Steps:**  
- Forced hardware passkey (FIDO2/WebAuthn) re-enrollment for 'tsingh'.
- Verified AWS CloudTrail logs across all regions for the last 24 hours to confirm zero unauthorized API calls.
- Validated perimeter web proxy block enforcement against all extracted phishing domains.

---

## 12. Indicators of Compromise

| Type | Value |
| :--- | :--- |
| IPv4 Address | \`198.51.100.42 (Attacker VPN Node (Mullvad_VPN_Exit_Node))\` |
| Domain | \`mail.attacker-redirect.com\` |
| Domain | \`login-payroll-update.com\` |
| Domain | \`attacker-redirect.com\` |
| User-Agent String | \`aws-cli/2.15.0 Python/3.11.8 Linux/6.6.0-fedora-x86_64\` |
| Malicious URL | \`http://login-payroll-update.com/auth/login.php?id=99281\` |
| IPv4 Address | \`10.0.1.50 (Source / Client IP)\` |
| User-Agent String | \`Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/127.0.0.0\` |
| IPv4 Address | \`103.21.244.12 (Phishing Infrastructure Resolved IP)\` |

---

## 13. Corrective & Preventive Actions (CAPA)

| Action | Owner | Due Date | Status |
| :--- | :--- | :--- | :--- |
| Enforce strict FIDO2/Passkey authentication with no legacy SMS downgrade fallback | Identity & Access Team | 2026-08-15 | In Progress |
| Update Email Gateway inbound DMARC/SPF policy to quarantine or reject unauthenticated mail | Mail Security Ops | 2026-08-10 | Completed |
| Configure web proxy to automatically terminate connections to URLs categorized as Phishing | Network Security Team | 2026-08-12 | Completed |
| Deliver targeted social engineering awareness training on payroll verification pretexts | Security Awareness | 2026-08-20 | Planned |

---

## 14. Lessons Learned

**What went well:**  
- Wazuh SIEM successfully detected anomalous authentication from a known VPN exit node with passkey downgrade (Level 12 alert).
- CloudTrail accurately audited AWS STS API reconnaissance immediately upon execution.
- Full audit logs across email, DNS, proxy, SIEM, and cloud were available for automated correlation.

**Improvements:**  
- Email gateway should not deliver emails failing DMARC and DKIM to user inboxes.
- Web proxy should block categorized phishing sites rather than allowing traffic.
- SSO Identity Provider should reject legacy MFA fallback when user is already enrolled in FIDO2 passkeys.

---

## 15. Final Conclusion

The incident resulted from a targeted spearphishing email that bypassed email gateway controls, leading to credential harvesting and subsequent unauthorized authentication through legacy MFA downgrade from an anonymized VPN exit node. Cloud reconnaissance API calls were recorded via AWS CloudTrail. Rapid containment revoked user sessions, blacklisted IOCs, and prevented lateral movement or persistent compromise. Root cause remediations have been scheduled under CAPA ticket tracking.

---

## 16. Appendix

### Log Excerpts & Forensic Evidence

\`\`\`
[2026-08-05 14:00:10 UTC] [email_gateway] email_reception
Raw Ref: {'timestamp': '2026-08-05T14:00:10.120Z', 'sender': 'hr-update@attacker-redirect.com', 'recipient': 'tsingh@corp.internal'}
\`\`\`

\`\`\`
[2026-08-05 14:02:15 UTC] [dns_query] dns_query
Raw Ref: 05-Aug-2026 14:02:15.104 client 10.0.1.50#52140 (login-payroll-update.com): query: login-payroll-update.com IN A + (10.0.1.1)
\`\`\`

\`\`\`
[2026-08-05 14:02:18 UTC] [web_proxy] phishing_attempt
Raw Ref: 10.0.1.50 - tsingh [05/Aug/2026:14:02:18 +0000] "POST /auth/login.php HTTP/1.1" 200 1420 "http://login-payroll-update.com/auth/login.php?id=99281" CATEGORY="Phishing" ACTION="allowed"
\`\`\`

\`\`\`
[2026-08-05 14:05:10 UTC] [wazuh] High Risk Identity Sign-in
Raw Ref: {'rule': {'id': '88204'}, 'network': {'srcip': '198.51.100.42', 'vpn_provider': 'Mullvad_VPN_Exit_Node'}}
\`\`\`

\`\`\`
[2026-08-05 14:08:30 UTC] [cloudtrail] GetCallerIdentity
Raw Ref: {'eventVersion': '1.08', 'eventName': 'GetCallerIdentity', 'sourceIPAddress': '198.51.100.42', 'userIdentity': {'userName': 'tsingh'}}
\`\`\`

### Detection & Hunting Queries
\`\`\`kql
DeviceNetworkEvents
| where RemoteIP in ('10.0.1.50', '103.21.244.12', '198.51.100.42')
| project Timestamp, DeviceName, RemoteIP, RemoteUrl

DnsEvents
| where Name in ('attacker-redirect.com', 'login-payroll-update.com', 'mail.attacker-redirect.com')
| project Timestamp, ClientIP, Name, IPAddresses

AWSCloudTrail
| where SourceIpAddress in ('10.0.1.50', '103.21.244.12', '198.51.100.42') or UserIdentityUserName == 'tsingh'
| project EventTime, EventName, SourceIpAddress, UserIdentityUserName, UserAgent
\`\`\`

### References & Forensic Documentation
- MITRE ATT&CK Framework: https://attack.mitre.org/
- NIST SP 800-61 Rev. 2: Computer Security Incident Handling Guide
- Wazuh Rule Documentation (Rule ID 88204): Risky Identity Sign-in
- AWS CloudTrail User Guide: Working with AWS STS API Events`
};
