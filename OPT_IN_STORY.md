# **Proof of Consent: Opt-In Process for LangGang's Charades Game**

LangGang ensures that users explicitly consent to receiving text messages for the Charades game through a straightforward and transparent opt-in process. Below is an outline of how we collect and document consent from our users:

---

## **Overview of the Opt-In Process**
LangGang offers users the ability to participate in the interactive Charades game via SMS. To ensure compliance with messaging regulations and maintain user trust, we require all participants to provide explicit consent before receiving any messages. Users can opt in through the following steps:

1. **SMS-Based Consent**
   - Users initiate the opt-in process by texting the LangGang phone number with the message 'LangGang' (case-insensitive).
   - Upon receiving the user's initial message, an automated reply is sent providing instructions on how to play the Charades game and informing them that they can opt out at any time by texting 'OptOut'.
   - This automated reply will include a brief introduction to the game, explaining the rules and the interactive nature of the SMS-based experience. Users will receive their first game prompt immediately after opting in, ensuring a seamless onboarding experience.

2. **Backend Confirmation and Record Keeping**
   - When a user opts in by sending 'LangGang,' their phone number and consent details are securely logged in our database. This ensures we have a verifiable record of their opt-in request, which is necessary for compliance and quality assurance.
   - A confirmation message is sent via Twilio to the user’s provided phone number. Example:
     *"Welcome to LangGang's Charades game! Your first prompt is coming up. Reply 'OptOut' at any time to stop receiving messages. Let's play!"*
   - This backend record-keeping allows us to maintain a complete history of user interactions, ensuring transparency and a secure environment for participants.

3. **Ongoing Consent Management and User Experience**
   - Users retain full control over their participation and can opt out at any time by texting the LangGang phone number with the message 'OptOut' (case-insensitive). Opt-out requests are processed immediately to ensure user preferences are respected without delay.
   - After opting out, users receive a confirmation message stating that they have successfully unsubscribed and will no longer receive Charades game messages unless they opt in again.
   - If a user opts out and later decides to rejoin, they can restart the process by texting 'LangGang' again. This ensures flexibility for participants who may want to return to the game at a later time.

4. **User Support and Compliance**
   - In case users experience any issues with the opt-in or opt-out process, they can contact LangGang support via a provided help number or email. Support agents are trained to handle inquiries related to SMS-based interactions, ensuring a smooth experience for all participants.
   - LangGang complies with all relevant messaging regulations, ensuring that user data is handled securely and responsibly. No marketing or spam messages are sent, and users only receive messages related to the Charades game as per their consent.

---

## **Supporting Evidence**
To demonstrate proof of consent, the following resources are available:

1. **SMS Interaction Logs**
   - Logs of the initial message from the user and their interactions with the system are stored securely in an encrypted database with access restricted to authorized personnel only.
   - Timestamped records of all consent-related interactions are maintained for compliance and operational transparency.

2. **Database Records**
   - We securely store records of user submissions, including:
     - The phone number provided.
     - Timestamp of consent.
     - Confirmation of their opt-in request.

3. **Confirmation Messages and System Security**
   - Sent messages are logged via Twilio, confirming user consent with a timestamp and message content.
   - Our system undergoes regular security audits to ensure the safety and integrity of stored user data.
   - LangGang employs industry-standard encryption and security measures to protect against unauthorized access and ensure compliance with data protection regulations.

---

This process benefits users by ensuring they have full control over their participation, while LangGang maintains compliance and fosters trust through explicit and transparent consent procedures. By providing a clear opt-in mechanism, an engaging user experience, and a secure consent management system, LangGang ensures a safe and enjoyable environment for all participants in the Charades game.

