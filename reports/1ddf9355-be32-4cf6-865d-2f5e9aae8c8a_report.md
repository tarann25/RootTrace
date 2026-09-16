# 🚨 Incident Response Report
**Cluster ID:** cluster_1  
**Generated On:** 2026-09-14 09:27:00 UTC  

## 1. Executive Summary
The incident began on August 5, 2026, when an email was received by user tsingh. The email appeared legitimate, originating from the internal HR department, but was actually sent from an attacker-controlled mail server. The email contained a URL that, upon inspection, was associated with a phishing attempt. User tsingh accessed the malicious URL, initiating a web request. While the request was allowed through the web proxy, it was categorized as a phishing attempt. 

Following this, a high-risk identity sign-in event was recorded at 14:05:10, indicating a successful login via a known malicious Virtual Private Network (VPN) exit node, where the passkey was bypassed via a downgrade attack. The login was performed from an IP address (198.51.100.42) that matched the email sender's IP. 

The final event, at 14:08:30, recorded a GetCallerIdentity API call made by user tsingh from the same IP address (198.51.100.42), suggesting potential lateral movement or credential compromise as the user accessed AWS services, indicating the attacker may have obtained valid credentials.

## 2. Compromised Entities
- **Users:** tsingh
- **IP Addresses:** 10.0.1.50, 103.21.244.12, 198.51.100.42
- **Domains:** attacker-redirect.com, login-payroll-update.com, mail.attacker-redirect.com

## 3. Chronological Incident Timeline

### [2026-08-05 14:00:10.120000+00:00] email_reception
- **Log Source:** `email_gateway`
- **User:** tsingh
- **Source IP:** 198.51.100.42

- **Extracted Details:**

  - *sender:* hr-update@attacker-redirect.com

  - *header_from:* hr-department@corp.internal

  - *sender_ip:* 198.51.100.42

  - *mail_server_hostname:* mail.attacker-redirect.com

  - *recipient:* tsingh@corp.internal

  - *subject:* URGENT: Verify Your Direct Deposit Information

  - *authentication_results:* {'spf': 'softfail', 'dkim': 'fail', 'dmarc': 'fail'}

  - *urls_detected:* ['http://login-payroll-update.com/auth/login.php?id=99281']

  - *action_taken:* delivered_to_inbox



### [2026-08-05 14:02:15.104000+00:00] dns_query
- **Log Source:** `dns_query`
- **User:** N/A
- **Source IP:** 10.0.1.50

- **Extracted Details:**

  - *query:* login-payroll-update.com

  - *dns_action:* query

  - *detail:* login-payroll-update.com IN A + (10.0.1.1)



### [2026-08-05 14:02:15.188000+00:00] dns_response
- **Log Source:** `dns_query`
- **User:** N/A
- **Source IP:** 10.0.1.50

- **Extracted Details:**

  - *query:* login-payroll-update.com

  - *dns_action:* response

  - *detail:* NOERROR 103.21.244.12

  - *response_status:* NOERROR

  - *response_ip:* 103.21.244.12



### [2026-08-05 14:02:18+00:00] phishing_attempt
- **Log Source:** `web_proxy`
- **User:** tsingh
- **Source IP:** 10.0.1.50

- **Extracted Details:**

  - *method:* POST

  - *path:* /auth/login.php

  - *status_code:* 200

  - *url:* http://login-payroll-update.com/auth/login.php?id=99281

  - *user_agent:* Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/127.0.0.0

  - *category:* Phishing

  - *action_status:* allowed



### [2026-08-05 14:05:10.880000+00:00] High Risk Identity Sign-in: Successful login via known malicious VPN exit node with passkey bypass / downgrade.
- **Log Source:** `wazuh`
- **User:** tsingh
- **Source IP:** 198.51.100.42

- **Extracted Details:**

  - *auth_method:* Password_Plus_SMS_Fallback

  - *passkey_status:* BYPASSED_VIA_DOWNGRADE

  - *vpn_provider:* Mullvad_VPN_Exit_Node

  - *device:* Linux x86_64

  - *browser:* Firefox 128.0

  - *geo_location:* {'country': 'Netherlands', 'city': 'Amsterdam', 'latitude': 52.3676, 'longitude': 4.9041}



### [2026-08-05 14:08:30+00:00] GetCallerIdentity
- **Log Source:** `cloudtrail`
- **User:** tsingh
- **Source IP:** 198.51.100.42

- **Extracted Details:**

  - *user_agent:* aws-cli/2.15.0 Python/3.11.8 Linux/6.6.0-fedora-x86_64

  - *arn:* arn:aws:iam::123456789012:user/tsingh

  - *account_id:* 123456789012

  - *event_source:* sts.amazonaws.com




## 4. Raw Evidence
*For deeper forensic analysis, raw log references are preserved in the pipeline database.*