"""
JobShield AI — Synthetic Dataset Generator (v3)

Generates a labeled dataset for training the scam detection model.
Each sample is tagged with a template_id so train/test can be split
by template (prevents the model from just memorizing template shape).

v3 adds legitimate freelance/gig-payment templates (client pays freelancer)
to counterbalance false positives on real freelance payment language, which
was surfaced by a blind holdout evaluation.
"""

import pandas as pd
import random
import os

# ─── Scam Templates ─────────────────────────────────────────────────────────────

SCAM_TEMPLATES = [
    "Congratulations! You have been selected for {company} internship. Pay ₹{fee} registration fee to confirm your seat. Limited seats available. Contact {email} immediately.",
    "Dear Candidate, {company} is offering guaranteed placement with ₹{salary}/month salary. To proceed, pay ₹{fee} as security deposit. Offer expires today!",
    "URGENT: You are shortlisted for {company} work from home job. Salary ₹{salary}/month. Pay ₹{fee} processing fee to get your offer letter. WhatsApp: {phone}",
    "Hi, I am HR from {company}. We have a vacancy for fresher. No experience needed. Salary ₹{salary}/month. Pay ₹{fee} training fee. Join immediately.",
    "Exciting opportunity at {company}! Earn ₹{salary}/month working from home. Only requirement: pay ₹{fee} one-time registration charge. Limited time offer!",
    "Dear Student, You have been selected for summer internship at {company}. Stipend: ₹{salary}/month. Please pay ₹{fee} admission fee within 24 hours.",
    "🎉 Congratulations! {company} internship offer! Pay ₹{fee} to reserve your spot. High stipend guaranteed. Contact us on WhatsApp: {phone}",
    "Selected for {company} placement drive! Pay ₹{fee} exam fee. 100% placement guarantee. Offer valid till today only. Hurry! Email: {email}",
    "Job Opening at {company}. No interview required. Just pay ₹{fee} and start earning ₹{salary}/month from day 1. Work from home. Contact: {phone}",
    "ATTENTION: {company} is hiring! Part-time job, earn ₹{salary}/day! Simple typing work. Registration fee ₹{fee}. DM now for details.",
    "LAST CHANCE! {company} hiring freshers NOW. ₹{salary}/month. No skills required. Apply immediately before all positions are filled. Contact: {email}",
    "⚠️ FINAL CALL: Only 5 seats left for {company} internship program. Register now by paying ₹{fee}. Don't miss this golden opportunity!",
    "Dear candidate, you've been referred for an exclusive position at {company}. Salary: ₹{salary}/month. This offer expires in 2 hours. Reply YES to confirm.",
    "Hi! {company} is looking for data entry operators. Work from home. Earn ₹{salary}/day. No experience needed. Pay ₹{fee} to start. WhatsApp: {phone}",
    "You won a lottery selection for {company} internship! Pay ₹{fee} to claim your position. Certificate + stipend provided. Act fast!",
    "Dear {name}, Please find attached your offer letter from {company}. To activate your employment, transfer ₹{fee} to the following UPI: {upi}. HR Team",
    "Your application to {company} has been approved! Download your appointment letter after paying ₹{fee} verification fee. Contact HR: {email}",
    "Welcome to {company}! Your joining date is next Monday. Please complete onboarding by paying ₹{fee} for background verification. UPI: {upi}",
    "🌟 {company} is hiring! DM us on Instagram @{handle} for details. Earn ₹{salary}/month. Quick hiring process. No resume needed!",
    "Telegram job alert! {company} needs 500 workers for data entry. ₹{salary}/day guaranteed. Join our channel and pay ₹{fee} to register.",
    "This is from {company} HR department. We found your resume on Naukri. You are shortlisted. Pay ₹{fee} for aptitude test. Call: {phone}",
    "Google/Microsoft/Amazon is hiring freshers! Salary ₹{salary}/month. Send your resume to {email} and pay ₹{fee} application fee.",
    "TCS/Infosys/Wipro walk-in drive! No experience needed. ₹{salary}/month CTC. Registration fee ₹{fee}. Venue details after payment.",
    "Earn ₹{salary}/month by referring friends to {company}! Pay ₹{fee} membership fee. Each referral earns you ₹500. Unlimited income potential!",
    "Join {company} affiliate program. Invest ₹{fee} and earn ₹{salary}/month passive income. 100% guaranteed returns. WhatsApp: {phone}",
    "Congrats! U r selected 4 {company} job. Sal: {salary}/m. Pay {fee} 2 confirm. Call {phone} NOW!",
    "Selected! {company}. ₹{salary}/m. Pay ₹{fee}. Limited offer. {phone}",
    "FREE LAPTOP + ₹{salary}/month job at {company}. Just pay ₹{fee} shipping. WhatsApp {phone}",
    "Are you looking for a job? {company} is hiring. Good salary. Flexible hours. Work from anywhere. Pay ₹{fee} to apply. Contact: {email}",
    "Part time / Full time job available at {company}. Earn ₹{salary}/month minimum. Investment: ₹{fee} only. Returns guaranteed. {phone}",
    # ── Hard cases: no fee mentioned, data-harvesting or professional-sounding scams ──
    "Hello, this is {name} from {company} recruitment team. We reviewed your profile and would like to proceed with onboarding. Kindly share your bank account number and Aadhaar details to process your first month's salary in advance.",
    "{company} is pleased to offer you the position of Business Development Executive. To complete verification, please send a scanned copy of your ID proof and PAN card to {email}.",
    "Thank you for your interest in {company}. Your final round is a formality. Please share your banking details for salary account setup before we release your appointment letter.",
    "We are excited to have you join {company} as a remote data associate. Please confirm by sharing your UPI PIN for verification purposes. Regards, HR",
    "{company} recruitment update: your interview has been waived based on a strong profile match. Kindly complete KYC by sharing your Aadhaar and bank passbook photo to {email}.",
    "Dear Candidate, We are delighted to extend an offer for the {role} position at {company}. Kindly revert with your bank account details for payroll setup within 24 hours to avoid delay in onboarding.",
    "Hi, HR at {company} here. Great news, you're through to the final stage! Just need your date of birth, address and bank IFSC code to prepare your employment contract.",
    "{company} Talent Team: Your resume matched our open role perfectly, no interview needed. Reply with your Aadhaar number so we can generate your employee ID before joining.",
    # ── Soft-fee freelance scams: candidate pays company for freelance "access" ──
    "Hi, to finalize your freelance project with us, please pay a ₹{fee} onboarding fee to access the client dashboard and start receiving tasks.",
    "Freelance opportunity confirmed! Just deposit ₹{fee} as a refundable trust fee before we release your first project brief.",
]

# ─── Legitimate Job Templates ──────────────────────────────────────────────────

LEGIT_TEMPLATES = [
    "We are looking for a {role} to join our team at {company}. Requirements: {years}+ years of experience in {skill}. Competitive salary and benefits. Apply at {website}.",
    "{company} is hiring a {role}. Location: {city}. Experience: {years}+ years. Skills required: {skill}, {skill2}. Send your resume to {corporate_email}.",
    "Job Opening: {role} at {company}, {city}. We offer a collaborative work environment, health insurance, and competitive compensation. Apply through our careers page: {website}.",
    "Position: {role}\nCompany: {company}\nLocation: {city}\nExperience: {years}-{years2} years\nSkills: {skill}, {skill2}, {skill3}\nApply: {website}\n\nEqual opportunity employer.",
    "{company} invites applications for {role}. CTC: {ctc} LPA. Location: {city}. Qualifications: B.Tech/M.Tech in {field}. Apply by {date}.",
    "{company} Summer Internship Program {year}. Duration: {months} months. Stipend: ₹{stipend}/month. Eligibility: Students in {field}. Apply at {website} by {date}.",
    "Internship Opportunity at {company}. Role: {role} Intern. Duration: {months} months. Location: {city} (Hybrid). Stipend: ₹{stipend}/month. No registration fee.",
    "We're offering a {months}-month internship for {field} students at {company}, {city}. You'll work on real projects with our {role} team. Stipend provided. Apply: {website}",
    "{company} will be visiting {college} for campus placements on {date}. Eligible branches: CSE, IT, ECE. CTC: {ctc} LPA. No registration charges. Prepare well!",
    "Campus Drive Alert: {company} | Date: {date} | Package: {ctc} LPA | Eligibility: 60% throughout, no backlogs | Register on the placement portal by {date}.",
    "Dear Applicant, Thank you for applying to the {role} position at {company}. We have reviewed your application and would like to invite you for a technical interview on {date} at {time}. Please confirm your availability. Regards, HR Team, {company}",
    "We are pleased to inform you that you have been shortlisted for the {role} position at {company}. The next round is a coding test scheduled on {date}. No fees required at any stage of recruitment.",
    "Thank you for your interest in {company}. We are currently reviewing applications for the {role} position. Our recruitment process includes: 1) Resume screening, 2) Technical interview, 3) HR discussion. We do not charge any fees.",
    "Exciting opportunity! {company} is expanding and we're looking for talented {role}s. If you have {years}+ years of experience in {skill} and {skill2}, apply through the link in bio. #hiring #{skill}",
    "🚀 We're hiring! {company} needs a {role} in {city}. Great culture, competitive pay, learning opportunities. Check out the JD on our careers page. #openposition",
    "About {company}: We are a leading {industry} company based in {city}.\n\nRole: {role}\nResponsibilities:\n- Design and develop {skill} solutions\n- Collaborate with cross-functional teams\n- Write clean, maintainable code\n\nRequirements:\n- {years}+ years in {skill}\n- Strong problem-solving skills\n- Excellent communication\n\nBenefits: Health insurance, flexible hours, learning budget\n\nApply: {website}",
    "{company} Recruitment {year}. Post: {role}. Vacancies: {vacancies}. Qualification: {qualification}. Age limit: 18-{age} years. Apply online at {website}. Last date: {date}. No application fee for SC/ST candidates.",
    "Remote {role} position at {company}. We're a distributed team working across {city} and {city2}. Stack: {skill}, {skill2}, {skill3}. Salary: {ctc} LPA. Apply: {corporate_email}",
    "Join our early-stage startup {company}! We're building {product} and need a {role}. Equity + competitive salary. If you're passionate about {field}, send your resume to {corporate_email}.",
    "Hey, my team at {company} is hiring a {role}. Great work culture and benefits. If interested, apply through {website} and I can refer you internally. Happy to chat!",
    "Subject: Application for {role} - {company}\n\nDear Hiring Manager,\n\nI am writing to express my interest in the {role} position at {company}. With {years} years of experience in {skill}, I believe I would be a strong fit.\n\nBest regards",
    "Dear Applicant, After careful consideration, we regret to inform you that we will not be moving forward with your application for the {role} position at {company}. We encourage you to apply for future openings. Regards, HR Team",
    # ── Hard cases: urgency and legitimate refundable fees (still legit) ──
    "{company} certification exam registration is now open. A nominal exam fee of ₹{cert_fee} applies, fully refundable upon course completion. Register at {website} before {date}.",
    "Limited seats available for {company}'s {months}-month internship cohort! Apply within 48 hours to secure your spot. Stipend: ₹{stipend}/month. No hidden charges. Apply: {website}",
    "Hurry! {company} campus placement registration closes {date}. Eligible students must register on the official portal. Selection is based purely on merit, no fees at any stage.",
    "As part of our onboarding process, {company} requires a refundable security deposit of ₹{cert_fee} for company laptop issuance, returned upon completion of probation. Full details in your official offer letter.",
    "Reminder: your {company} interview is scheduled for {date} at {time}. Please carry your original documents. This is a formal in-person process, no online payment is required at any stage.",
    "{company} is closing applications for the {role} internship in 2 days. Don't miss out, apply now at {website}. Selection purely on merit, no payment involved.",
    # ── Freelance/gig payment direction: client pays freelancer (legit) ──
    "Hi, thanks for taking up the {project_type} project! Payment will be ₹{gig_amount}, 50% upfront via UPI once we sign off on the brief, remaining on delivery. Let me know your UPI ID to send the advance.",
    "Freelance opportunity: {project_type} for a 2-week sprint. Budget ₹{gig_amount} fixed, paid via bank transfer in two milestones. DM your portfolio if interested.",
    "We need a freelance {role} for a short-term contract, ₹{gig_amount}/month retainer, paid via NEFT on the 1st of every month. Send your rate card.",
    "Hey, loved your portfolio! For the {project_type} gig we discussed, I'll pay ₹{gig_amount} total, half now as advance and half after final delivery. What's your UPI ID?",
    "Looking for a freelance voiceover artist for a one-time project, ₹{gig_amount} flat fee, payment via bank transfer within 24 hours of delivery.",
    "Client here from {platform} - confirming the {project_type} job at ₹{gig_amount}, milestone-based payment through the platform's escrow, first milestone released on approval.",
    "Thanks for the quote! Let's proceed with ₹{gig_amount} for the {project_type} work, I'll send 30% advance via UPI today and rest on completion as agreed.",
    "We're hiring a freelance content writer, ₹{gig_amount} per article, payments processed weekly via bank transfer, no fees or deposits required from your side.",
]

# ─── Fill Values ─────────────────────────────────────────────────────────────────

SCAM_COMPANIES = [
    "TechVision Solutions", "GlobalHire Pvt Ltd", "SmartWork India",
    "MegaCorp International", "QuickHire Solutions", "EasyMoney Corp",
    "FastTrack Placements", "DreamJob India", "TopNotch Hiring",
    "PrimeWork Solutions", "EliteJobs Global", "InstantHire Pvt Ltd",
    "GoldenGate Careers", "SureShot Placements", "RapidGrowth Inc",
    "Google", "Microsoft", "Amazon", "TCS", "Infosys", "Wipro",
    "Flipkart", "Paytm", "Reliance", "Zomato", "Swiggy",
]

LEGIT_COMPANIES = [
    "Accenture", "Deloitte", "KPMG", "Ernst & Young", "PwC",
    "Tata Consultancy Services", "Infosys", "Wipro", "HCL Technologies",
    "Tech Mahindra", "Cognizant", "Capgemini", "IBM India", "Oracle",
    "Adobe", "Salesforce", "SAP Labs", "ThoughtWorks", "Freshworks",
    "Zoho Corporation", "Razorpay", "PhonePe", "CRED", "Atlassian",
    "Goldman Sachs", "Morgan Stanley", "JP Morgan", "Deutsche Bank",
]

ROLES = [
    "Software Engineer", "Data Analyst", "Frontend Developer",
    "Backend Developer", "Full Stack Developer", "DevOps Engineer",
    "Machine Learning Engineer", "Product Manager", "Business Analyst",
    "QA Engineer", "UI/UX Designer", "Cloud Architect",
    "Data Scientist", "Mobile Developer", "Systems Administrator",
]

SKILLS = [
    "Python", "Java", "JavaScript", "React", "Node.js", "SQL",
    "AWS", "Docker", "Kubernetes", "TensorFlow", "PyTorch",
    "MongoDB", "PostgreSQL", "TypeScript", "Go", "Rust",
    "Machine Learning", "Data Analysis", "Cloud Computing",
]

CITIES = [
    "Bangalore", "Hyderabad", "Pune", "Mumbai", "Delhi NCR",
    "Chennai", "Kolkata", "Noida", "Gurgaon", "Ahmedabad",
]

FIELDS = [
    "Computer Science", "Information Technology", "Electronics",
    "Electrical Engineering", "Mechanical Engineering", "Data Science",
    "Artificial Intelligence", "Cybersecurity",
]

COLLEGES = [
    "IIT Bombay", "IIT Delhi", "NIT Trichy", "BITS Pilani",
    "VIT Vellore", "SRM University", "Manipal Institute of Technology",
]

INDUSTRIES = [
    "technology", "fintech", "e-commerce", "healthcare", "edtech",
    "SaaS", "cybersecurity", "AI/ML", "cloud computing",
]

SCAM_EMAILS = [
    "hr.google@gmail.com", "microsoft.careers@yahoo.com",
    "amazon.hiring@gmail.com", "tcs.hr2024@gmail.com",
    "placement.infosys@outlook.com", "jobs.wipro@yahoo.in",
    "recruit.flipkart@gmail.com", "hiring.paytm@gmail.com",
    "techvision.hr@gmail.com", "quickhire@yahoo.com",
]

SCAM_PHONES = [
    "+91 98765 43210", "+91 87654 32109", "+91 76543 21098",
    "+91 9999988888", "+91 8888877777", "9876543210",
]

SCAM_UPIS = [
    "hr.company@paytm", "recruiter2024@gpay",
    "placement.fee@upi", "registration@phonepe",
]

HANDLES = [
    "techvision_careers", "quickhire_india", "dreamjob_official",
    "megacorp_hiring", "fasttrack_jobs",
]

PROJECT_TYPES = [
    "logo design", "WordPress website", "explainer video edit",
    "Instagram reel editing", "content writing", "voiceover recording",
    "data entry for a research project", "UI mockup design",
    "resume writing", "translation work",
]

FREELANCE_PLATFORMS = ["Upwork", "Fiverr", "Freelancer.com", "Truelancer", "our agency"]


def _random_fee() -> int:
    """Generate a realistic random scam fee amount."""
    return random.choice([499, 599, 799, 999, 1499, 1999, 2499, 2999, 4999, 5999, 9999])


def _random_cert_fee() -> int:
    """Generate a realistic certificate or exam fee."""
    return random.choice([300, 500, 750, 1000, 1500])


def _random_gig_amount() -> int:
    """Generate a realistic freelance gig payment amount."""
    return random.choice([1500, 2500, 3500, 5000, 8000, 10000, 12000, 15000, 20000])


def _random_scam_salary() -> str:
    """Generate an unrealistic or high scam salary string."""
    return random.choice([
        "50,000", "75,000", "1,00,000", "1,20,000", "1,50,000",
        "2,00,000", "80,000", "60,000", "40,000", "25,000",
        "3,000", "5,000", "8,000", "10,000",
    ])


def _random_legit_stipend() -> str:
    """Generate a realistic legitimate internship stipend string."""
    return random.choice([
        "10,000", "15,000", "20,000", "25,000", "30,000", "35,000", "40,000",
    ])


def _random_ctc() -> str:
    """Generate a realistic LPA package string."""
    return random.choice([
        "3.5", "4.0", "4.5", "5.0", "6.0", "7.0", "8.0",
        "10.0", "12.0", "15.0", "18.0", "20.0",
    ])


def _random_years() -> str:
    """Generate a random years of experience requirement."""
    return str(random.randint(1, 8))


def _random_months() -> str:
    """Generate a random internship duration in months."""
    return str(random.choice([2, 3, 4, 6]))


def _random_date() -> str:
    """Generate a random date string for deadlines/schedules."""
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    return f"{random.randint(1, 28)} {random.choice(months)} 2025"


def _fill_scam_template(template: str) -> str:
    """Populate placeholders in a scam template with randomized entities."""
    return template.format(
        company=random.choice(SCAM_COMPANIES),
        fee=_random_fee(),
        salary=_random_scam_salary(),
        email=random.choice(SCAM_EMAILS),
        phone=random.choice(SCAM_PHONES),
        upi=random.choice(SCAM_UPIS),
        name=random.choice(["Rahul", "Priya", "Amit", "Sneha", "Ravi", "Anjali"]),
        handle=random.choice(HANDLES),
        role=random.choice(ROLES),
    )


def _fill_legit_template(template: str) -> str:
    """Populate placeholders in a legitimate template with randomized entities."""
    skills = random.sample(SKILLS, min(3, len(SKILLS)))
    years_val = _random_years()
    years2_val = str(int(years_val) + random.randint(1, 3))
    company = random.choice(LEGIT_COMPANIES)
    corp_domain = company.lower().replace(" ", "").replace("&", "")[:12]

    return template.format(
        company=company,
        role=random.choice(ROLES),
        city=random.choice(CITIES),
        city2=random.choice(CITIES),
        years=years_val,
        years2=years2_val,
        skill=skills[0],
        skill2=skills[1] if len(skills) > 1 else "SQL",
        skill3=skills[2] if len(skills) > 2 else "Git",
        website=f"https://careers.{corp_domain}.com",
        corporate_email=f"careers@{corp_domain}.com",
        ctc=_random_ctc(),
        cert_fee=_random_cert_fee(),
        field=random.choice(FIELDS),
        date=_random_date(),
        time=f"{random.randint(9,17)}:00 IST",
        year="2025",
        months=_random_months(),
        stipend=_random_legit_stipend(),
        college=random.choice(COLLEGES),
        industry=random.choice(INDUSTRIES),
        product=random.choice(["next-gen payments", "AI-powered analytics", "cloud infrastructure", "health tech"]),
        vacancies=str(random.randint(5, 200)),
        qualification=random.choice(["B.Tech", "M.Tech", "BCA", "MCA", "B.Sc IT"]),
        age=str(random.randint(28, 35)),
        project_type=random.choice(PROJECT_TYPES),
        gig_amount=_random_gig_amount(),
        platform=random.choice(FREELANCE_PLATFORMS),
    )


def generate_dataset(num_scam: int = 1400, num_legit: int = 1400, output_path: str = None) -> pd.DataFrame:
    """Generate a balanced synthetic dataset, tagged with template_id for grouped splitting."""

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "data", "training_data.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = []

    for _ in range(num_scam):
        idx = random.randrange(len(SCAM_TEMPLATES))
        text = _fill_scam_template(SCAM_TEMPLATES[idx])
        data.append({"text": text, "label": 1, "template_id": f"scam_{idx}"})

    generated_legit = 0
    attempts = 0
    max_attempts = num_legit * 3
    while generated_legit < num_legit and attempts < max_attempts:
        attempts += 1
        idx = random.randrange(len(LEGIT_TEMPLATES))
        try:
            text = _fill_legit_template(LEGIT_TEMPLATES[idx])
            data.append({"text": text, "label": 0, "template_id": f"legit_{idx}"})
            generated_legit += 1
        except (KeyError, IndexError):
            continue

    random.shuffle(data)
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"✅ Generated {len(df)} samples ({num_scam} scam, {generated_legit} legit)")
    print(f"   {len(SCAM_TEMPLATES)} scam templates, {len(LEGIT_TEMPLATES)} legit templates")
    print(f"   Saved to: {output_path}")
    return df


if __name__ == "__main__":
    generate_dataset()