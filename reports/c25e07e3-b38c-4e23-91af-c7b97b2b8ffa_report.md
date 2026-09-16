# 🚨 Incident Response Report
**Cluster ID:** cluster_1  
**Generated On:** 2026-09-14 09:19:57 UTC  

## 1. Executive Summary
Executive Summary:

The incident timeline indicates an initial compromise through a phishing email, which was delivered to the inbox of user tsingh from an IP address 198.51.100.42. The email, purporting to be from the HR department, contained a link to a malicious login page. User tsingh accessed this phishing website, likely providing credentials in the process.

Following the initial access, there was a DNS query to resolve the domain of the phishing site, and the site resolved to an IP address 103.21.244.12, which is likely the malicious server hosting the phishing page. A web proxy log shows that user tsingh interacted with the phishing site via a POST request, indicating that credentials were potentially submitted.

The incident then progressed to an unauthorized login via a known malicious VPN exit node, with the passkey bypassed via a downgrade attack. This lateral movement occurred using the IP address 198.51.100.42, and it involved a high-risk sign-in event where the user tsingh successfully logged in from a location in the Netherlands using the Amazon Web Services (AWS) STS GetCallerIdentity operation. The nature of the actions on objectives, specifically the use of the AWS STS API, suggests that the attacker may have gained access to the victim's AWS account, which could lead to further lateral movement or data exfiltration.

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