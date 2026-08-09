"""
JobShield AI — BLIND Holdout Evaluation

CRITICAL: This test set is separate from evaluate_real.py's TEST_SET on
purpose. That original 27-example set has effectively become a *tuning*
set over the course of development — we've looked at its misses
repeatedly and made rule_engine/weight/model decisions based on them.
That's normal and fine, but it means it can no longer give an unbiased
read on real-world performance.

This file's BLIND_TEST_SET is written fresh, targeting the known weak
spots (soft-phrased fees, negation edge cases, casual/DM style, campus
placement style, freelance/gig work, overseas/BPO scams, credential
harvesting) but with NEW wording never looked at during tuning.

RULES FOR USING THIS FILE HONESTLY:
  1. Run it to get a final read AFTER you're done making changes for
     a given round of work — not as a running scoreboard you optimize
     against turn by turn.
  2. If you look at the misclassified examples here and then tweak
     rule_engine.py / weights / templates specifically to fix them,
     this set has become a tuning set too — at that point, treat its
     score with the same skepticism as evaluate_real.py's, and write
     yet another fresh blind set before trusting a future number.
  3. It's fine to run this occasionally just to check progress — the
     contamination risk is in reacting to specific misses, not in
     looking at the top-line accuracy number itself.
"""

import os
import sys
import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix
)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ── Fresh hand-written test set (label: 1 = scam, 0 = legit) ───────────────
# Independently written — NOT from dataset_generator.py templates, NOT
# overlapping with evaluate_real.py's TEST_SET.

BLIND_TEST_SET = [
    # ── Legit: casual / DM / conversational ──
    ("hey saw ur profile on cutshort, we're hiring a react dev at our series A startup, 12-18 lpa based on exp, want to hop on a quick call this week?", 0),
    ("yo my manager asked me to find a freelance video editor for our youtube channel, pay is 8k per video, 2 videos a week, no upfront cost obviously, dm if interested", 0),
    ("hi! loved your portfolio. we're a 6 person agency, need a part time graphic designer, 15k/month retainer, invoice us monthly, first payment after first deliverable", 0),
    ("congrats on clearing round 2! round 3 is a system design discussion with our staff engineer, 45 mins, calendar invite coming from careers@ourcompany.com", 0),

    # ── Legit: campus / placement / formal process ──
    ("Placement Notice: Cognizant pre-placement talk in Auditorium at 3pm Thursday. Eligible: all branches, min 60% aggregate. Online test link will be shared post-talk via official college email.", 0),
    ("TPO Update: Wipro Elite drive results are out. Shortlisted students must report to the placement office by 5pm today with original mark sheets for document verification. No fees at any stage.", 0),
    ("Reminder: your pre-placement offer (PPO) confirmation call with HDFC Bank is scheduled for 11am tomorrow. Please join via the Teams link sent to your registered email.", 0),
    ("Dear Candidate, your GATE score qualifies you for the PSU recruitment drive. Application fee for General category is ₹800, payable only via the official recruitment portal linked on the PSU's website.", 0),

    # ── Legit: freelance / gig / contract ──
    ("Looking for a freelance WordPress dev for a 1-week landing page build, ₹8000 fixed, 50% via UPI on contract signing, 50% on final delivery. Milestone-based, standard freelance terms.", 0),
    ("We need a voiceover artist for a 3-min explainer video, one-time gig, ₹3500, payment via bank transfer after you send the final audio file, no advance needed from your side.", 0),
    ("Hiring a content writer on a per-article basis, ₹1500/article, topics assigned weekly, invoice at month end, standard NET-15 payment terms via our accounts team.", 0),

    # ── Legit: referral / networking / rejection ──
    ("Hey, remember me from the meetup last month? We have an opening for a PM role at my company, thought of you. No fees obviously, just send your resume and I'll pass it along internally.", 0),
    ("Thank you for interviewing with us for the Data Analyst role. After much deliberation, we've decided to move forward with another candidate. We'll keep your profile on file for future openings.", 0),
    ("Following up on your application - unfortunately this role has been put on hold internally due to budget freezes. We'll reach out if it reopens. No action needed from you at this time.", 0),

    # ── Legit: tricky "urgent"/"verification" language done right ──
    ("Reminder: complete your pre-employment verification form by Friday, this is standard for all new joiners and does not involve any payment, just document uploads on our internal portal.", 0),
    ("Quick heads up - your background check with our third-party partner (SpringVerify) may reach out this week to confirm past employment dates. This is routine, no cost to you.", 0),
    ("We're moving fast on this hire since the team needs someone by month-end. If you're keen, let's do a call tomorrow. No fees, no forms to fill beyond the usual application.", 0),
    ("Time-sensitive: our current intern batch wraps up Friday and we want to fill the seat immediately. If interested, reply today - stipend 10k/month, official offer letter to follow.", 0),

    # ── Legit: government / PSU / formal exam-style ──
    ("SSC CGL 2025 Notification: Online applications open till the 15th. Application fee ₹100 for General/OBC, exempted for SC/ST/PWD/Female candidates. Pay only via the official SSC portal.", 0),
    ("Railway Recruitment Board Notice: RRB NTPC exam admit cards released. Download only via rrbcdg.gov.in using your registration number. No other website or app is authorized.", 0),

    # ── Scam: soft-phrased / low-pressure fee disclosure ──
    ("Hi, thanks for your interest in the Marketing Associate role. Before we proceed, there's a small onboarding facilitation charge of Rs 799 to activate your candidate profile on our internal system.", 1),
    ("We're happy to move forward with your application. As a formality, a nominal processing charge of Rs 350 applies to generate your employee code in our HR system, standard for all new hires.", 1),
    ("Your profile has been forwarded to our client for the Analyst role. To proceed, kindly complete registration on our portal, which involves a one-time listing fee of Rs 599.", 1),

    # ── Scam: negation combined with other strong signals ──
    ("No registration fee, no hidden charges! Just work 1 hour daily from home and earn up to Rs 40,000/month. Limited slots, DM now to grab yours before they're gone.", 1),
    ("Zero investment work from home job, guaranteed daily payout, no fee ever. Just join our WhatsApp group and start immediately, first task pays instantly to build trust.", 1),

    # ── Scam: crypto / investment ──
    ("Join our exclusive trading community, we teach you to earn 5-10% daily returns on crypto, minimum deposit $50 to open your wallet with our recommended partner exchange.", 1),
    ("Hi, I run a small forex signals group, members are making consistent profits, just need Rs 2000 to add you to the premium channel where we share live guaranteed trade calls.", 1),

    # ── Scam: task-based / telegram / app install ──
    ("Complete easy tasks like following pages and rating apps, earn Rs 50-200 per task. Free to start, but to withdraw earnings above Rs 500 you must upgrade your account for Rs 999.", 1),
    ("Download this app and complete 3 daily tasks to earn Rs 300/day. Referral bonus available. To unlock premium high-paying tasks, a one-time activation of Rs 499 is required.", 1),

    # ── Scam: credential harvesting, softer framing ──
    ("Great news, you're through to the final step! Our payroll team just needs your bank account number, IFSC, and a copy of your PAN card to set up your salary account before joining.", 1),
    ("To speed up your offer letter generation, please reply with your Aadhaar number and a selfie for identity verification, this is handled directly by our HR automation system.", 1),
    ("Congratulations on clearing the interview! Last step - share your net banking user ID so our finance team can verify your account is active before crediting your joining bonus.", 1),

    # ── Scam: fake MNC impersonation / overseas ──
    ("This is regarding your application to Infosys through our overseas placement partner. Selected candidates for the Dubai branch must pay a visa processing fee of AED 500 to proceed.", 1),
    ("We are hiring Electricians and Welders for a construction project in Qatar. Salary QAR 2500/month + accommodation. Processing and visa fee of ₹15,000 required before departure.", 1),
    ("On behalf of TCS overseas recruitment cell, you've been shortlisted for our Singapore office. Kindly remit the relocation processing fee of $200 to confirm your slot.", 1),

    # ── Scam: BPO bulk hiring / urgency ──
    ("URGENT bulk hiring for International BPO, 50+ openings, freshers welcome, salary 18-25k, walk-in interview tomorrow, carry Rs 500 registration fee and 2 photographs.", 1),
    ("Voice process job opening, immediate joining, no experience needed, salary credited weekly. Registration and ID card fee of Rs 650 payable at the time of joining.", 1),

    # ── Scam: casual / broken English / WhatsApp forward ──
    ("gud morning sir madam, we hv job for u, wrk from home, salary 25k gurantee, only pay 500 for id card n starting kit, reply fast slots limited", 1),
    ("*Forwarded many times* Big company hiring urgent basis, no intervew, salary credit daily, contact this no and pay small registration to start work today itself", 1),
    ("Hii I saw ur resume online, we have vacancy, salary very good, just need small amount for uniform and training materials before joining, reply for details", 1),

    # ── Scam: fake interview then payment pivot ──
    ("Thanks for the great interview today! One last step before we finalize - please transfer Rs 2500 as a refundable interview booking fee, it'll be returned in your first payslip.", 1),
    ("You did well in the technical round. HR will now process your offer, but first needs a Rs 1000 background verification charge to be paid via the link we just sent.", 1),

    # ── Scam: lottery / selection framing ──
    ("🎊 SELECTED! Your number has been picked for our exclusive hiring lottery among 10,000 applicants. Claim your Rs 45,000/month job by paying a small confirmation fee of Rs 299.", 1),
    ("You have been randomly selected from our database for a premium remote job opportunity. To claim your slot, complete verification by paying Rs 450 within the next 2 hours.", 1),

    # ── Scam: placement consultancy fee framing ──
    ("Our placement consultancy has 100% tie-ups with top MNCs. Registration fee Rs 3000 covers resume building, mock interviews, and guaranteed placement within 30 days or full refund.", 1),
    ("Get guaranteed government job placement through our consultancy. One-time service charge of Rs 8000 covers all exam guidance and interview preparation until you're selected.", 1),
]


def evaluate(verbose: bool = True) -> float:
    """
    Run the blind holdout evaluation.

    Args:
        verbose: if True (default), prints the full report.
                 if False, runs silently and just returns the accuracy.

    Returns:
        accuracy as a float in [0, 1]. Returns 0.0 if model files aren't found.
    """
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    tfidf_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
    model_path = os.path.join(model_dir, "scam_classifier.pkl")

    if not os.path.exists(tfidf_path) or not os.path.exists(model_path):
        print("❌ Trained model not found. Run train_model.py first.")
        return 0.0

    tfidf = joblib.load(tfidf_path)
    model = joblib.load(model_path)

    texts = [t.lower().strip() for t, _ in BLIND_TEST_SET]
    y_true = np.array([label for _, label in BLIND_TEST_SET])

    X = tfidf.transform(texts)
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    if verbose:
        print("=" * 55)
        print("🔒 BLIND HOLDOUT EVALUATION (fresh, never tuned against)")
        print("=" * 55)
        print(f"  Samples:   {len(BLIND_TEST_SET)}")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1 Score:  {f1:.4f}")

        print("\n📋 Classification Report:")
        print(classification_report(y_true, y_pred, target_names=["Legitimate", "Scam"]))

        print("🔢 Confusion Matrix:")
        cm = confusion_matrix(y_true, y_pred)
        print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
        print(f"  FN={cm[1][0]}  TP={cm[1][1]}")

        print("\n❌ Misclassified examples:")
        label_name = {0: "Legit", 1: "Scam"}
        for i, (text, true_label) in enumerate(BLIND_TEST_SET):
            if y_pred[i] != true_label:
                print(f"  True={label_name[true_label]:6s} Pred={label_name[y_pred[i]]:6s} "
                      f"(prob_scam={y_prob[i]:.2f}) | {text[:110]}")

        print("\n✅ Evaluation complete!")
        print("\n⚠️  Remember: if you tune rule_engine.py/weights based on the misses")
        print("   above, this set is now contaminated too — write a new blind set")
        print("   before trusting a future number from this file.")

    return accuracy


if __name__ == "__main__":
    evaluate()