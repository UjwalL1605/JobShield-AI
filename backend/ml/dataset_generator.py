"""
JobShield AI — Synthetic Dataset Generator

Generates a labeled dataset of ~2000 samples for training the scam detection model.
Each sample is a job/internship message labeled as 0 (legitimate) or 1 (scam).
"""

import pandas as pd
import random
import os

# ─── Scam Templates ─────────────────────────────────────────────────────────────

SCAM_TEMPLATES = [
    # Fee-based scams
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

    # Urgency + vague role scams
    "LAST CHANCE! {company} hiring freshers NOW. ₹{salary}/month. No skills required. Apply immediately before all positions are filled. Contact: {email}",
    "⚠️ FINAL CALL: Only 5 seats left for {company} internship program. Register now by paying ₹{fee}. Don't miss this golden opportunity!",
    "Dear candidate, you've been referred for an exclusive position at {company}. Salary: ₹{salary}/month. This offer expires in 2 hours. Reply YES to confirm.",
    "Hi! {company} is looking for data entry operators. Work from home. Earn ₹{salary}/day. No experience needed. Pay ₹{fee} to start. WhatsApp: {phone}",
    "You won a lottery selection for {company} internship! Pay ₹{fee} to claim your position. Certificate + stipend provided. Act fast!",

    # Fake offer letter scams
    "Dear {name}, Please find attached your offer letter from {company}. To activate your employment, transfer ₹{fee} to the following UPI: {upi}. HR Team",
    "Your application to {company} has been approved! Download your appointment letter after paying ₹{fee} verification fee. Contact HR: {email}",
    "Welcome to {company}! Your joining date is next Monday. Please complete onboarding by paying ₹{fee} for background verification. UPI: {upi}",

    # Social media scams
    "🌟 {company} is hiring! DM us on Instagram @{handle} for details. Earn ₹{salary}/month. Quick hiring process. No resume needed!",
    "Telegram job alert! {company} needs 500 workers for data entry. ₹{salary}/day guaranteed. Join our channel and pay ₹{fee} to register.",

    # Impersonation scams
    "This is from {company} HR department. We found your resume on Naukri. You are shortlisted. Pay ₹{fee} for aptitude test. Call: {phone}",
    "Google/Microsoft/Amazon is hiring freshers! Salary ₹{salary}/month. Send your resume to {email} and pay ₹{fee} application fee.",
    "TCS/Infosys/Wipro walk-in drive! No experience needed. ₹{salary}/month CTC. Registration fee ₹{fee}. Venue details after payment.",

    # Multi-level / referral scams
    "Earn ₹{salary}/month by referring friends to {company}! Pay ₹{fee} membership fee. Each referral earns you ₹500. Unlimited income potential!",
    "Join {company} affiliate program. Invest ₹{fee} and earn ₹{salary}/month passive income. 100% guaranteed returns. WhatsApp: {phone}",

    # SMS-style scams
    "Congrats! U r selected 4 {company} job. Sal: {salary}/m. Pay {fee} 2 confirm. Call {phone} NOW!",
    "Selected! {company}. ₹{salary}/m. Pay ₹{fee}. Limited offer. {phone}",
    "FREE LAPTOP + ₹{salary}/month job at {company}. Just pay ₹{fee} shipping. WhatsApp {phone}",

    # Vague description scams
    "Are you looking for a job? {company} is hiring. Good salary. Flexible hours. Work from anywhere. Pay ₹{fee} to apply. Contact: {email}",
    "Part time / Full time job available at {company}. Earn ₹{salary}/month minimum. Investment: ₹{fee} only. Returns guaranteed. {phone}",
]

# ─── Legitimate Job Templates ──────────────────────────────────────────────────

LEGIT_TEMPLATES = [
    # Standard job postings
    "We are looking for a {role} to join our team at {company}. Requirements: {years}+ years of experience in {skill}. Competitive salary and benefits. Apply at {website}.",
    "{company} is hiring a {role}. Location: {city}. Experience: {years}+ years. Skills required: {skill}, {skill2}. Send your resume to {corporate_email}.",
    "Job Opening: {role} at {company}, {city}. We offer a collaborative work environment, health insurance, and competitive compensation. Apply through our careers page: {website}.",
    "Position: {role}\nCompany: {company}\nLocation: {city}\nExperience: {years}-{years2} years\nSkills: {skill}, {skill2}, {skill3}\nApply: {website}\n\nEqual opportunity employer.",
    "{company} invites applications for {role}. CTC: {ctc} LPA. Location: {city}. Qualifications: B.Tech/M.Tech in {field}. Apply by {date}.",

    # Internship postings
    "{company} Summer Internship Program {year}. Duration: {months} months. Stipend: ₹{stipend}/month. Eligibility: Students in {field}. Apply at {website} by {date}.",
    "Internship Opportunity at {company}. Role: {role} Intern. Duration: {months} months. Location: {city} (Hybrid). Stipend: ₹{stipend}/month. No registration fee.",
    "We're offering a {months}-month internship for {field} students at {company}, {city}. You'll work on real projects with our {role} team. Stipend provided. Apply: {website}",

    # Campus placement
    "{company} will be visiting {college} for campus placements on {date}. Eligible branches: CSE, IT, ECE. CTC: {ctc} LPA. No registration charges. Prepare well!",
    "Campus Drive Alert: {company} | Date: {date} | Package: {ctc} LPA | Eligibility: 60% throughout, no backlogs | Register on the placement portal by {date}.",

    # Professional tone
    "Dear Applicant, Thank you for applying to the {role} position at {company}. We have reviewed your application and would like to invite you for a technical interview on {date} at {time}. Please confirm your availability. Regards, HR Team, {company}",
    "We are pleased to inform you that you have been shortlisted for the {role} position at {company}. The next round is a coding test scheduled on {date}. No fees required at any stage of recruitment.",
    "Thank you for your interest in {company}. We are currently reviewing applications for the {role} position. Our recruitment process includes: 1) Resume screening, 2) Technical interview, 3) HR discussion. We do not charge any fees.",

    # LinkedIn style
    "Exciting opportunity! {company} is expanding and we're looking for talented {role}s. If you have {years}+ years of experience in {skill} and {skill2}, apply through the link in bio. #hiring #{skill}",
    "🚀 We're hiring! {company} needs a {role} in {city}. Great culture, competitive pay, learning opportunities. Check out the JD on our careers page. #openposition",

    # Detailed JD
    "About {company}: We are a leading {industry} company based in {city}.\n\nRole: {role}\nResponsibilities:\n- Design and develop {skill} solutions\n- Collaborate with cross-functional teams\n- Write clean, maintainable code\n\nRequirements:\n- {years}+ years in {skill}\n- Strong problem-solving skills\n- Excellent communication\n\nBenefits: Health insurance, flexible hours, learning budget\n\nApply: {website}",

    # Government / formal
    "{company} Recruitment {year}. Post: {role}. Vacancies: {vacancies}. Qualification: {qualification}. Age limit: 18-{age} years. Apply online at {website}. Last date: {date}. No application fee for SC/ST candidates.",

    # Remote job
    "Remote {role} position at {company}. We're a distributed team working across {city} and {city2}. Stack: {skill}, {skill2}, {skill3}. Salary: {ctc} LPA. Apply: {corporate_email}",

    # Startup
    "Join our early-stage startup {company}! We're building {product} and need a {role}. Equity + competitive salary. If you're passionate about {field}, send your resume to {corporate_email}.",

    # Referral
    "Hey, my team at {company} is hiring a {role}. Great work culture and benefits. If interested, apply through {website} and I can refer you internally. Happy to chat!",

    # Standard email
    "Subject: Application for {role} - {company}\n\nDear Hiring Manager,\n\nI am writing to express my interest in the {role} position at {company}. With {years} years of experience in {skill}, I believe I would be a strong fit.\n\nBest regards",

    # Rejection (also legitimate)
    "Dear Applicant, After careful consideration, we regret to inform you that we will not be moving forward with your application for the {role} position at {company}. We encourage you to apply for future openings. Regards, HR Team",
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

def _random_fee():
    return random.choice([499, 599, 799, 999, 1499, 1999, 2499, 2999, 4999, 5999, 9999])

def _random_scam_salary():
    return random.choice([
        "50,000", "75,000", "1,00,000", "1,20,000", "1,50,000",
        "2,00,000", "80,000", "60,000", "40,000", "25,000",
        "3,000", "5,000", "8,000", "10,000",  # daily
    ])

def _random_legit_stipend():
    return random.choice([
        "10,000", "15,000", "20,000", "25,000", "30,000", "35,000", "40,000",
    ])

def _random_ctc():
    return random.choice([
        "3.5", "4.0", "4.5", "5.0", "6.0", "7.0", "8.0",
        "10.0", "12.0", "15.0", "18.0", "20.0",
    ])

def _random_years():
    return str(random.randint(1, 8))

def _random_months():
    return str(random.choice([2, 3, 4, 6]))

def _random_date():
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    return f"{random.randint(1, 28)} {random.choice(months)} 2025"

def _fill_scam_template(template):
    years_val = _random_years()
    return template.format(
        company=random.choice(SCAM_COMPANIES),
        fee=_random_fee(),
        salary=_random_scam_salary(),
        email=random.choice(SCAM_EMAILS),
        phone=random.choice(SCAM_PHONES),
        upi=random.choice(SCAM_UPIS),
        name=random.choice(["Rahul", "Priya", "Amit", "Sneha", "Ravi", "Anjali"]),
        handle=random.choice(HANDLES),
    )

def _fill_legit_template(template):
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
    )

def generate_dataset(num_scam=1000, num_legit=1000, output_path=None):
    """Generate a balanced synthetic dataset."""

    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "data", "training_data.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = []

    # Generate scam samples
    for _ in range(num_scam):
        template = random.choice(SCAM_TEMPLATES)
        text = _fill_scam_template(template)
        data.append({"text": text, "label": 1})

    # Generate legit samples
    for _ in range(num_legit):
        template = random.choice(LEGIT_TEMPLATES)
        try:
            text = _fill_legit_template(template)
        except (KeyError, IndexError):
            continue
        data.append({"text": text, "label": 0})

    random.shuffle(data)
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"✅ Generated {len(df)} samples ({num_scam} scam, {len(df) - num_scam} legit)")
    print(f"   Saved to: {output_path}")
    return df


if __name__ == "__main__":
    generate_dataset()
