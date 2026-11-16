# Suggested 5–7 Minute Demonstration Script — RelaySMS with SMSGate

1. **Introduction (30–45 sec):** Explain that RelaySMS is a Django web application that sends SMS through the SMSGate Android gateway.
2. **Dashboard (30 sec):** Show message statistics and recent activity.
3. **Validation (45 sec):** Demonstrate empty fields and an invalid phone number.
4. **Gateway workflow (1 min):** Explain that Django calls the SMSGate Cloud REST API; SMSGate routes the request to the connected Android phone; the phone sends it through the selected SIM and carrier.
5. **Actual SMS (1 min):** Enter an authorized test number and send a short message. Show the received SMS if delivery succeeds.
6. **History/details (45 sec):** Show the saved attempt, SMSGate message ID, current status, and status refresh.
7. **Security (45 sec):** Explain that Cloud Server credentials are stored in `.env`, excluded from Git, and never rendered in the browser.
8. **Additional features (30 sec):** Show search, status filtering, character counter, preview, and dashboard statistics.
9. **Technology/team (45 sec):** Explain Django, Python, SQLite, SMSGate REST API, Android/SIM, frontend technologies, and member responsibilities.

Keep the video between 3 and 10 minutes. Hide credentials and private recipient information. Do not describe a queued/accepted request as delivered unless a delivery status confirms it.
