#!/usr/bin/env python3
"""
Add a job posting to the Natera database
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Job details from Greenhouse
job_data = {
    'job_id': '5635534004',
    'position': 'PRN Phlebotomist (1099)',
    'company': 'Natera',
    'department': 'Phlebotomy',
    'location_type': 'On-site',
    'location_city': 'Denver',
    'location_country': 'United States',
    'employment_type': 'PRN (1099 Contractor)',
    'compensation_currency': None,  # Not specified
    'compensation_min': None,
    'compensation_max': None,
    'about_role': 'A phlebotomist identifies optimal blood collection methods, prepares specimens for laboratory analysis, and manages shipping procedures. This is a PRN (as-needed) independent contractor position working in a mobile/remote setting.',
    'requirements': json.dumps({
        'must_have': [
            'High school diploma or equivalent',
            'Minimum 2 years phlebotomy experience',
            'National phlebotomy certification (may be required depending on state)',
            'Ability to adhere to professional standards, federal/state/local regulations, and JCAHO requirements'
        ],
        'nice_to_have': [
            'RN/BS/BA degree'
        ]
    }),
    'responsibilities': json.dumps([
        'Verifies test orders and patient information for accuracy',
        'Performs venipunctures to obtain blood specimens',
        'Maintains specimen integrity using aseptic technique',
        'Documents collection details including initials, dates, and times',
        'Ensures compliance with quality procedures and safety standards',
        'Resolves unusual test orders by coordinating with the mobile phlebotomy team',
        'Handles Protected Health Information (PHI) in paper and electronic formats',
        'Updates job statuses and tracking data in Skedulo software',
        'Completes requisition paperwork and manages patient report logistics',
        'Answers billing inquiries and schedules courier pickups'
    ]),
    'raw_job_data': json.dumps({
        'source': 'greenhouse',
        'original_url': 'https://job-boards.greenhouse.io/natera/jobs/5635534004',
        'benefits': [
            'Comprehensive medical, dental, vision, life, and disability insurance',
            'Free genetic testing for employees and immediate families',
            'Fertility care benefits',
            'Pregnancy and baby bonding leave',
            '401(k) benefits',
            'Commuter benefits',
            'Employee referral program'
        ],
        'physical_requirements': [
            'Mobile/remote setting work',
            'Scrubs and closed-toe shoes required',
            'Appropriate PPE (facemasks, gloves, hand hygiene)'
        ],
        'training': 'Training on Standard Operating Procedures must be completed within 30 days of hire'
    }),
    'application_link': 'https://job-boards.greenhouse.io/natera/jobs/5635534004',
    'posting_code': 'GH-5635534004',
    'status': 'active',
    'posted_date': datetime.now().isoformat()
}

print("Adding job to database...")
print(f"Position: {job_data['position']}")
print(f"Location: {job_data['location_city']}, {job_data['location_country']}")
print(f"Job ID: {job_data['job_id']}")

try:
    # Insert job posting
    result = supabase.table('job_postings').insert(job_data).execute()

    print("\n✅ Job successfully added to database!")
    print(f"Database ID: {result.data[0]['id']}")
    print(f"Position: {result.data[0]['position']}")
    print(f"Status: {result.data[0]['status']}")

except Exception as e:
    print(f"\n❌ Error adding job: {str(e)}")

    # Check if job already exists
    existing = supabase.table('job_postings').select('*').eq('job_id', job_data['job_id']).execute()
    if existing.data:
        print(f"\nJob already exists in database:")
        print(f"  - ID: {existing.data[0]['id']}")
        print(f"  - Position: {existing.data[0]['position']}")
        print(f"  - Status: {existing.data[0]['status']}")
