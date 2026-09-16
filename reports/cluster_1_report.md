# 🚨 Incident Response Report
**Cluster ID:** cluster_1  
**Generated On:** 2026-08-15 13:00:09 UTC  

## 1. Executive Summary
Executive Summary:

On August 5, 2026, an initial breach occurred when an email was received by an internal user, Tsingh, from what appeared to be a legitimate HR department email address but was actually sent from a malicious domain, `hr-update@attacker-redirect.com`. The email contained a link to a phishing website (`http://login-payroll-update.com/auth/login.php?id=99281`) and a spoofed company logo, which was accessed by Tsingh through the web proxy. 

Following the phishing attempt, Tsingh authenticated using a known malicious Virtual Private Network (VPN) exit node, Mullvad_VPN_Exit_Node, with the passkey bypassed via downgrade. This indicates an attempt to gain unauthorized access to internal systems using compromised credentials. Shortly after, an AWS CloudTrail log showed a successful GetCallerIdentity API call from the same IP address (198.51.100.42) associated with the compromised user account, `tsingh`, suggesting that the attacker successfully accessed and potentially exploited the AWS environment, likely for further reconnaissance or control.

## 2. Compromised Entities
- **Users:** tsingh
- **IP Addresses:** 10.0.1.50, 198.51.100.42
- **Domains:** login-payroll-update.com

## 3. Chronological Incident Timeline

### [2026-08-05 14:00:10.120000] email_reception
- **Log Source:** `email_gateway`
- **User:** N/A
- **Source IP:** N/A

- **Extracted Details:**

  - *sender:* hr-update@attacker-redirect.com

  - *header_from:* hr-department@corp.internal

  - *sender_ip:* 198.51.100.42

  - *mail_server_hostname:* mail.attacker-redirect.com

  - *recipient:* tsingh@corp.internal

  - *subject:* URGENT: Verify Your Direct Deposit Information

  - *message_id:* <202608051400.x88120@attacker-redirect.com>

  - *return_path:* <hr-update@attacker-redirect.com>

  - *content_type:* multipart/related; boundary="----=_NextPart_000_01D9"

  - *x_mailer:* Custom Python Script v2.1

  - *authentication_results:* {'spf': 'softfail', 'dkim': 'fail', 'dmarc': 'fail'}

  - *urls_detected:* ['http://login-payroll-update.com/auth/login.php?id=99281']

  - *images_embedded:* [{'filename': 'company_logo_spoofed.png', 'cid': 'image001.png@01D9881A', 'mime_type': 'image/png', 'size_bytes': 14200}]

  - *action_taken:* delivered_to_inbox



### [2026-08-05 14:02:15.104000] dns_query
- **Log Source:** `dns_query`
- **User:** N/A
- **Source IP:** 10.0.1.50

- **Extracted Details:**

  - *query:* login-payroll-update.com

  - *query_type:* A

  - *response_status:* NOERROR

  - *response_ip:* 103.21.244.12



### [2026-08-05 14:02:18] phishing_attempt
- **Log Source:** `web_proxy`
- **User:** tsingh
- **Source IP:** 10.0.1.50

- **Extracted Details:**

  - *url:* http://login-payroll-update.com/auth/login.php?id=99281

  - *user_agent:* Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/127.0.0.0

  - *action_status:* allowed

  - *method:* POST



### [2026-08-05 14:05:10.880000] High Risk Identity Sign-in: Successful login via known malicious VPN exit node with passkey bypass / downgrade.
- **Log Source:** `wazuh`
- **User:** tsingh
- **Source IP:** 198.51.100.42

- **Extracted Details:**

  - *auth_method:* Password_Plus_SMS_Fallback

  - *passkey_status:* BYPASSED_VIA_DOWNGRADE

  - *vpn_provider:* Mullvad_VPN_Exit_Node

  - *device:* Linux x86_64

  - *browser:* Firefox 128.0



### [2026-08-05 14:08:30] GetCallerIdentity
- **Log Source:** `cloudtrail`
- **User:** tsingh
- **Source IP:** 198.51.100.42

- **Extracted Details:**

  - *user_agent:* aws-cli/2.15.0 Python/3.11.8 Linux/6.6.0-fedora-x86_64

  - *arn:* arn:aws:iam::123456789012:user/tsingh

  - *account_id:* 123456789012




## 4. Raw Evidence
*For deeper forensic analysis, raw log references are preserved in the pipeline database.*