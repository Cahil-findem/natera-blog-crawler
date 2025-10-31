# Natera Blog Crawler - API Integration Guide

## Quick Reference

**Base URL:** `https://natera-blog-crawler.vercel.app`

**Endpoint:** `POST /api/generate-email`

**Authentication:** Not required (API_KEY is not set)

---

## Generate Email for Candidate

### Overview

This endpoint generates a personalized nurture email for a candidate that includes:
- Matched blog articles from Natera news
- Matched job openings (if available)
- Personalized messaging based on candidate profile

### HTTP Request

```http
POST https://natera-blog-crawler.vercel.app/api/generate-email
Content-Type: application/json
```

### Request Body

```json
{
  "candidate_id": "pub_lnkd_abc123"
}
```

**Parameters:**
- `candidate_id` (string, required): The unique identifier for the candidate (must already exist in database)

---

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "candidate": {
    "id": "pub_lnkd_abc123",
    "name": "Jane Smith",
    "title": "Senior Bioinformatics Scientist",
    "company": "BioTech Corp",
    "location": "Boston, MA"
  },
  "candidate_profile": {
    // Full raw candidate JSON from database
  },
  "professional_summary": "Jane Smith is a Senior Bioinformatics Scientist with 8+ years of experience in genomic analysis and precision medicine...",
  "job_preferences": "Job Titles: Principal Scientist, Staff Scientist\nLocation: Remote\nSeniority: Senior IC",
  "interests": "• Genomics\n• Machine learning in healthcare\n• Clinical research\n• Next-generation sequencing\n• Python development",
  "blog_matches": [
    {
      "title": "Advancing Precision Medicine at Scale",
      "url": "https://www.natera.com/company/news/advancing-precision-medicine",
      "featured_image": "https://www.natera.com/images/article.jpg",
      "relevance": 87.5,
      "author": "Natera Team",
      "excerpt": "Natera's latest breakthrough in genomic sequencing technology enables faster and more accurate analysis..."
    }
  ],
  "job_matches": [
    {
      "position": "Senior Bioinformatics Engineer",
      "company": "Natera",
      "location_type": "Remote",
      "location": "San Carlos, CA",
      "compensation": "USD 150,000 - 200,000",
      "about_role": "Join our bioinformatics team to build scalable pipelines for genomic data analysis...",
      "application_link": "https://careers.natera.com/jobs/12345",
      "match_score": "45%",
      "similarity": 0.45,
      "llm_evaluation": {
        "confidence": "high",
        "match_score": 85,
        "reasoning": "Strong engineering fundamentals and genomics experience align well with this role.",
        "key_alignments": ["Python expertise", "Genomics background", "Data pipeline experience"],
        "concerns": ["Limited cloud infrastructure experience"]
      }
    }
  ],
  "email": {
    "subject": "Been thinking about your next move, Jane",
    "body": "Hi Jane,\n\nI've been thinking about your trajectory from BioTech Corp...\n\n[Full HTML email content with embedded news articles and job links]",
    "candidate_name": "Jane Smith",
    "candidate_title": "Senior Bioinformatics Scientist",
    "news_count": 3
  },
  "timestamp": "2025-10-31T10:30:00.123456"
}
```

### Error Responses

**404 Not Found - Candidate Not Found:**
```json
{
  "error": "Candidate pub_lnkd_abc123 not found in database"
}
```

**404 Not Found - No News Matches:**
```json
{
  "error": "No matching news articles found."
}
```

**400 Bad Request:**
```json
{
  "error": "Invalid request. Provide candidate_id."
}
```

**500 Internal Server Error:**
```json
{
  "error": "Server error: [error details]"
}
```

---

## Code Examples

### cURL

```bash
curl -X POST https://natera-blog-crawler.vercel.app/api/generate-email \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "pub_lnkd_abc123"
  }'
```

### JavaScript / TypeScript

```javascript
async function generateCandidateEmail(candidateId) {
  const response = await fetch('https://natera-blog-crawler.vercel.app/api/generate-email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      candidate_id: candidateId
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to generate email');
  }

  const result = await response.json();
  return result;
}

// Usage
const result = await generateCandidateEmail('pub_lnkd_abc123');

console.log('Subject:', result.email.subject);
console.log('Body:', result.email.body);
console.log('Blog matches:', result.blog_matches.length);
console.log('Job matches:', result.job_matches.length);

// Use the email content
const emailSubject = result.email.subject;
const emailBodyHTML = result.email.body;
```

### Python

```python
import requests

def generate_candidate_email(candidate_id: str):
    url = 'https://natera-blog-crawler.vercel.app/api/generate-email'
    headers = {'Content-Type': 'application/json'}
    data = {'candidate_id': candidate_id}

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()

    return response.json()

# Usage
result = generate_candidate_email('pub_lnkd_abc123')

print(f"Subject: {result['email']['subject']}")
print(f"Blog matches: {len(result['blog_matches'])}")
print(f"Job matches: {len(result['job_matches'])}")

# Use the email content
email_subject = result['email']['subject']
email_body_html = result['email']['body']
```

---

## Response Fields Explained

### email
- **subject**: Personalized email subject line (under 60 characters)
- **body**: Full HTML email content, ready to send via email service
- **candidate_name**: Candidate's full name
- **candidate_title**: Candidate's current job title
- **news_count**: Number of news articles included in the email

### blog_matches (array)
Each blog match contains:
- **title**: Article headline
- **url**: Link to full article on Natera website
- **featured_image**: Article image URL (or placeholder)
- **relevance**: Match score from 0-100 (higher = more relevant)
- **author**: Article author name
- **excerpt**: Brief snippet from most relevant section (200 chars)

### job_matches (array)
Each job match contains:
- **position**: Job title
- **company**: Company name (Natera)
- **location_type**: "Remote", "Hybrid", or "On-site"
- **location**: Geographic location (e.g., "San Carlos, CA")
- **compensation**: Salary range (e.g., "USD 150,000 - 200,000")
- **about_role**: Job description excerpt (250 chars)
- **application_link**: URL to apply for the position
- **match_score**: Percentage match as string (e.g., "45%")
- **similarity**: Raw similarity score as decimal (0-1)
- **llm_evaluation**: AI-powered assessment including:
  - **confidence**: "high", "medium", or "low"
  - **match_score**: 0-100 score
  - **reasoning**: Brief explanation of the match
  - **key_alignments**: List of positive factors
  - **concerns**: List of potential issues

**Note:** `job_matches` may be an empty array `[]` if no suitable jobs are found.

---

## Important Notes

1. **Candidate Must Exist**: The candidate must already be in the database. Use `/api/process-candidate` first if adding a new candidate.

2. **Response Time**: Typical response time is 5-15 seconds due to AI processing (LLM calls for email generation and job matching).

3. **Email Format**: The `email.body` field contains HTML-formatted content that is ready to send through any email service provider.

4. **Job Matching**: The system uses two-stage matching:
   - Stage 1: Semantic similarity (35% threshold)
   - Stage 2: LLM evaluation for genuine fit

   Only jobs that pass both stages are returned (maximum 2 best matches).

5. **No News Matches**: If no relevant news articles are found, the endpoint returns a 404 error. The candidate profile may need updating to better align with available content.

---

## Testing

### Health Check
To verify the API is running:

```bash
curl https://natera-blog-crawler.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "natera-candidate-email-generator",
  "timestamp": "2025-10-31T10:30:00.123456"
}
```

---

## Complete Integration Example

```javascript
class NateraBlogAPI {
  constructor() {
    this.baseURL = 'https://natera-blog-crawler.vercel.app';
  }

  async generateEmail(candidateId) {
    const response = await fetch(`${this.baseURL}/api/generate-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate_id: candidateId })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }

    return await response.json();
  }

  async sendNurtureEmail(candidateId, emailService) {
    try {
      // Generate email
      const result = await this.generateEmail(candidateId);

      // Send via your email service
      await emailService.send({
        to: result.candidate.email,
        subject: result.email.subject,
        html: result.email.body
      });

      return {
        success: true,
        candidate: result.candidate.name,
        blogMatches: result.blog_matches.length,
        jobMatches: result.job_matches.length
      };

    } catch (error) {
      console.error('Failed to send nurture email:', error.message);
      return { success: false, error: error.message };
    }
  }
}

// Usage
const api = new NateraBlogAPI();
const result = await api.sendNurtureEmail('pub_lnkd_abc123', yourEmailService);
console.log(result);
```
