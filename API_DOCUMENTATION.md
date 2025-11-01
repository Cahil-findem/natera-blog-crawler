# Natera Blog Crawler - API Integration Guide

Complete API documentation for integrating with the Natera Blog Crawler deployed application.

## Base Information

- **Base URL**: `https://natera-blog-crawler.vercel.app`
- **Authentication**: Optional (no API key currently required)
- **Content Type**: `application/json`
- **Response Format**: JSON

---

## Table of Contents

1. [Endpoints Overview](#endpoints-overview)
2. [API Reference](#api-reference)
   - [Process Candidate](#1-process-candidate)
   - [Generate Email](#2-generate-email)
   - [Update Context](#3-update-context)
   - [Health Check](#4-health-check)
3. [Response Objects](#response-objects)
4. [Error Handling](#error-handling)
5. [Code Examples](#code-examples)

---

## Endpoints Overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/process-candidate` | POST | Add new candidate, vectorize, and generate first email |
| `/api/generate-email` | POST | Generate email for existing candidate |
| `/api/update-context` | POST | Append additional context to candidate profile |
| `/api/health` | GET | Check API health status |

---

## API Reference

### 1. Process Candidate

**All-in-one endpoint for new candidates**: Processes candidate profile, creates AI-powered summaries, vectorizes for matching, finds relevant news articles and job openings, and generates personalized email.

**Endpoint**: `POST /api/process-candidate`

#### Request Body

```json
{
  "candidate": {
    "ref": "pub_lnkd_123456",
    "full_name": "John Doe",
    "current_title": "Senior Software Engineer",
    "current_company": "Tech Corp",
    "location": "San Francisco, CA",
    "about_me": "Passionate about cloud architecture and genomics...",
    "skills": ["Python", "AWS", "Machine Learning"],
    "work_experience": [
      {
        "company": {
          "name": "Tech Corp"
        },
        "title": "Senior Software Engineer",
        "duration": "2020-01 - Present"
      }
    ]
  }
}
```

#### Response

```json
{
  "success": true,
  "candidate": {
    "id": "pub_lnkd_123456",
    "name": "John Doe",
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA"
  },
  "candidate_profile": { ... },
  "professional_summary": "John Doe is a Senior Software Engineer...",
  "job_preferences": "Job Titles: Staff Engineer, Principal Engineer...",
  "interests": "• Cloud Architecture\n• Genomics Technology...",
  "blog_matches": [
    {
      "news_id": 1056,
      "news_title": "Natera Named to Fast Company's Next Big Things in Tech",
      "news_url": "https://www.natera.com/company/news/...",
      "news_author": "Natera",
      "news_featured_image": "https://natera-blog-crawler.vercel.app/images/Natera-social.webp",
      "best_matching_chunk": "Natera has been recognized...",
      "max_similarity": 0.78
    }
  ],
  "job_matches": [
    {
      "position": "Senior Bioinformatics Engineer",
      "company": "Natera",
      "location_city": "Austin",
      "location_country": "United States",
      "location_type": "Hybrid",
      "department": "Engineering",
      "employment_type": "Full-time",
      "compensation_min": 150000,
      "compensation_max": 200000,
      "compensation_currency": "USD",
      "about_role": "We are seeking a Senior Bioinformatics Engineer...",
      "requirements": {
        "must_have": ["PhD or MS in Bioinformatics", "5+ years experience"],
        "nice_to_have": ["Experience with genomics pipelines"]
      },
      "responsibilities": [
        "Design and implement bioinformatics pipelines",
        "Collaborate with data science team"
      ],
      "application_link": "https://job-boards.greenhouse.io/natera/jobs/...",
      "similarity": 0.72,
      "llm_evaluation": {
        "confidence": "high",
        "match_score": 85,
        "reasoning": "Strong technical background aligns with role requirements...",
        "key_alignments": ["Python expertise", "Cloud infrastructure experience"],
        "concerns": ["No direct genomics experience mentioned"]
      }
    }
  ],
  "email": {
    "subject": "Thought You'd Find This Interesting, John",
    "body": "Hi John,\n\nI came across your profile and was impressed...",
    "candidate_name": "John Doe",
    "candidate_title": "Senior Software Engineer",
    "news_count": 2
  },
  "timestamp": "2025-11-01T18:30:00.123456"
}
```

---

### 2. Generate Email

**Generate fresh email for existing candidate**: Retrieves candidate from database, matches current news articles and job openings, generates new personalized email.

**Endpoint**: `POST /api/generate-email`

#### Request Body

```json
{
  "candidate_id": "pub_lnkd_123456"
}
```

#### Response

Same structure as `/api/process-candidate` response. Returns the full candidate profile, summaries, current blog matches, job matches, and newly generated email.

#### Use Cases

- Generate follow-up emails with latest news
- Refresh matches after new articles are published
- Re-engage candidates with new job openings

---

### 3. Update Context

**Append additional knowledge to candidate profile**: Updates specific sections of candidate's profile with new context (e.g., from conversation notes, interview feedback). Re-vectorizes the updated section for improved matching.

**Endpoint**: `POST /api/update-context`

#### Request Body

```json
{
  "candidate_id": "pub_lnkd_123456",
  "additional_context": "They mentioned strong interest in platform engineering and learning Kubernetes. Excited about opportunities in healthcare technology.",
  "section": "interests"
}
```

#### Parameters

- `candidate_id` (required): Candidate identifier
- `additional_context` (required): New information to append
- `section` (optional): Which section to update
  - `"interests"` (default) - Personal interests and motivations
  - `"job_preferences"` - Job preferences and career goals
  - Note: `professional_summary` cannot be updated via this endpoint

#### Response

```json
{
  "success": true,
  "candidate_id": "pub_lnkd_123456",
  "section_updated": "interests",
  "updated_content": "• Cloud Architecture\n• Genomics Technology\n• Platform Engineering\n• Kubernetes",
  "context_added": "They mentioned strong interest in platform engineering...",
  "timestamp": "2025-11-01T18:30:00.123456"
}
```

#### Use Cases

- Add notes from recruiter conversations
- Update candidate interests after interviews
- Track evolving job preferences over time

---

### 4. Health Check

**Check API availability**: Simple endpoint to verify the API is running.

**Endpoint**: `GET /api/health`

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2025-11-01T18:30:00.123456"
}
```

---

## Response Objects

### Candidate Object

```json
{
  "id": "pub_lnkd_123456",
  "name": "John Doe",
  "title": "Senior Software Engineer",
  "company": "Tech Corp",
  "location": "San Francisco, CA"
}
```

### Blog Match Object

```json
{
  "news_id": 1056,
  "news_title": "Article Title",
  "news_url": "https://www.natera.com/...",
  "news_author": "Natera",
  "news_featured_image": "https://natera-blog-crawler.vercel.app/images/Natera-social.webp",
  "best_matching_chunk": "Relevant excerpt from article...",
  "max_similarity": 0.78
}
```

### Job Match Object

```json
{
  "position": "Job Title",
  "company": "Natera",
  "location_city": "Austin",
  "location_country": "United States",
  "location_type": "Hybrid",
  "department": "Engineering",
  "employment_type": "Full-time",
  "compensation_min": 150000,
  "compensation_max": 200000,
  "compensation_currency": "USD",
  "about_role": "Role description...",
  "requirements": {
    "must_have": ["Requirement 1", "Requirement 2"],
    "nice_to_have": ["Nice to have 1"]
  },
  "responsibilities": ["Responsibility 1", "Responsibility 2"],
  "application_link": "https://job-boards.greenhouse.io/...",
  "similarity": 0.72,
  "llm_evaluation": {
    "confidence": "high",
    "match_score": 85,
    "reasoning": "Detailed explanation...",
    "key_alignments": ["Alignment 1", "Alignment 2"],
    "concerns": ["Concern 1"]
  }
}
```

### Email Object

```json
{
  "subject": "Email subject line",
  "body": "Full email body with HTML formatting...",
  "candidate_name": "John Doe",
  "candidate_title": "Senior Software Engineer",
  "news_count": 2
}
```

---

## Error Handling

All errors follow this structure:

```json
{
  "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Invalid API key (if authentication enabled) |
| `404` | Not Found - Candidate or resource not found |
| `500` | Server Error - Internal processing error |

### Common Error Scenarios

#### Candidate Not Found
```json
{
  "error": "Candidate pub_lnkd_123456 not found in database"
}
```

#### No Matches Found
```json
{
  "error": "No matching news articles or job openings found."
}
```

#### Invalid Request
```json
{
  "error": "Invalid request. Please provide candidate JSON."
}
```

---

## Code Examples

### JavaScript (Node.js)

#### Process New Candidate

```javascript
const fetch = require('node-fetch');

async function processCandidate(candidateData) {
  const response = await fetch('https://natera-blog-crawler.vercel.app/api/process-candidate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      candidate: candidateData
    })
  });

  const result = await response.json();

  if (result.success) {
    console.log('Email generated:', result.email.subject);
    console.log('Blog matches:', result.blog_matches.length);
    console.log('Job matches:', result.job_matches.length);
    return result;
  } else {
    console.error('Error:', result.error);
  }
}

// Example usage
const candidate = {
  ref: 'pub_lnkd_123456',
  full_name: 'John Doe',
  current_title: 'Senior Software Engineer',
  current_company: 'Tech Corp',
  location: 'San Francisco, CA',
  about_me: 'Passionate about cloud architecture and genomics technology.',
  skills: ['Python', 'AWS', 'Machine Learning'],
  work_experience: [
    {
      company: { name: 'Tech Corp' },
      title: 'Senior Software Engineer',
      duration: '2020-01 - Present'
    }
  ]
};

processCandidate(candidate);
```

#### Generate Email for Existing Candidate

```javascript
async function generateEmail(candidateId) {
  const response = await fetch('https://natera-blog-crawler.vercel.app/api/generate-email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      candidate_id: candidateId
    })
  });

  const result = await response.json();
  return result;
}

// Example usage
generateEmail('pub_lnkd_123456')
  .then(result => {
    console.log('Generated email:', result.email.body);
  });
```

#### Update Candidate Context

```javascript
async function updateContext(candidateId, newContext, section = 'interests') {
  const response = await fetch('https://natera-blog-crawler.vercel.app/api/update-context', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      candidate_id: candidateId,
      additional_context: newContext,
      section: section
    })
  });

  const result = await response.json();
  return result;
}

// Example usage
updateContext(
  'pub_lnkd_123456',
  'Expressed interest in healthcare technology and platform engineering',
  'interests'
).then(result => {
  console.log('Updated:', result.section_updated);
});
```

---

### Python

#### Process New Candidate

```python
import requests
import json

def process_candidate(candidate_data):
    url = 'https://natera-blog-crawler.vercel.app/api/process-candidate'

    response = requests.post(
        url,
        json={'candidate': candidate_data},
        headers={'Content-Type': 'application/json'}
    )

    result = response.json()

    if result.get('success'):
        print(f"Email generated: {result['email']['subject']}")
        print(f"Blog matches: {len(result['blog_matches'])}")
        print(f"Job matches: {len(result['job_matches'])}")
        return result
    else:
        print(f"Error: {result.get('error')}")
        return None

# Example usage
candidate = {
    'ref': 'pub_lnkd_123456',
    'full_name': 'John Doe',
    'current_title': 'Senior Software Engineer',
    'current_company': 'Tech Corp',
    'location': 'San Francisco, CA',
    'about_me': 'Passionate about cloud architecture and genomics technology.',
    'skills': ['Python', 'AWS', 'Machine Learning'],
    'work_experience': [
        {
            'company': {'name': 'Tech Corp'},
            'title': 'Senior Software Engineer',
            'duration': '2020-01 - Present'
        }
    ]
}

result = process_candidate(candidate)
```

#### Generate Email for Existing Candidate

```python
def generate_email(candidate_id):
    url = 'https://natera-blog-crawler.vercel.app/api/generate-email'

    response = requests.post(
        url,
        json={'candidate_id': candidate_id},
        headers={'Content-Type': 'application/json'}
    )

    return response.json()

# Example usage
result = generate_email('pub_lnkd_123456')
print(result['email']['body'])
```

#### Update Candidate Context

```python
def update_context(candidate_id, new_context, section='interests'):
    url = 'https://natera-blog-crawler.vercel.app/api/update-context'

    response = requests.post(
        url,
        json={
            'candidate_id': candidate_id,
            'additional_context': new_context,
            'section': section
        },
        headers={'Content-Type': 'application/json'}
    )

    return response.json()

# Example usage
result = update_context(
    'pub_lnkd_123456',
    'Expressed interest in healthcare technology and platform engineering',
    'interests'
)
print(f"Updated: {result['section_updated']}")
```

---

### cURL

#### Process New Candidate

```bash
curl -X POST https://natera-blog-crawler.vercel.app/api/process-candidate \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "ref": "pub_lnkd_123456",
      "full_name": "John Doe",
      "current_title": "Senior Software Engineer",
      "current_company": "Tech Corp",
      "location": "San Francisco, CA",
      "about_me": "Passionate about cloud architecture and genomics technology.",
      "skills": ["Python", "AWS", "Machine Learning"],
      "work_experience": [
        {
          "company": {"name": "Tech Corp"},
          "title": "Senior Software Engineer",
          "duration": "2020-01 - Present"
        }
      ]
    }
  }'
```

#### Generate Email for Existing Candidate

```bash
curl -X POST https://natera-blog-crawler.vercel.app/api/generate-email \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "pub_lnkd_123456"
  }'
```

#### Update Candidate Context

```bash
curl -X POST https://natera-blog-crawler.vercel.app/api/update-context \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "pub_lnkd_123456",
    "additional_context": "Expressed interest in healthcare technology and platform engineering",
    "section": "interests"
  }'
```

#### Health Check

```bash
curl https://natera-blog-crawler.vercel.app/api/health
```

---

## Integration Best Practices

### 1. Workflow for New Candidates

```
1. Call /api/process-candidate with full profile
   → Stores candidate in database
   → Generates initial email with blog and job matches

2. Use returned candidate_id for future operations

3. Periodically call /api/generate-email to get fresh matches
   → New articles published
   → New jobs posted
```

### 2. Workflow for Candidate Updates

```
1. After recruiter conversations or interviews:
   Call /api/update-context to add new information
   → "section": "interests" for personal notes
   → "section": "job_preferences" for career goals

2. Generate fresh email with updated context:
   Call /api/generate-email
   → Matching improves with accumulated context
```

### 3. Error Handling

```javascript
async function safeApiCall(url, data) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error.message);
    // Handle error appropriately (retry, fallback, notify)
    throw error;
  }
}
```

### 4. Rate Limiting

The API does not currently enforce rate limits, but best practices suggest:
- Batch process candidates when possible
- Avoid generating duplicate emails within short time windows
- Cache candidate data to minimize API calls

---

## Matching Algorithm Details

### Three-Field Embedding System

The system creates three separate AI-powered summaries for each candidate:

1. **Professional Summary**: Technical skills, work history, expertise
2. **Job Preferences**: Desired roles, seniority, location preferences
3. **Interests**: Personal motivations, industry interests, career aspirations

Each summary is vectorized separately, enabling more precise matching across different dimensions.

### Blog Article Matching

- Uses semantic similarity search across all three embeddings
- Combines results using max similarity across fields
- Includes manually prioritized articles (if configured)
- Returns top 3 matches by default

### Job Matching (Two-Stage Process)

**Stage 1: Semantic Similarity**
- Vector search using three-field embeddings
- Threshold: 35% minimum similarity
- Fast filtering of obviously poor matches

**Stage 2: LLM Evaluation**
- GPT-4o evaluates each candidate-job pair
- Returns: match score (0-100), reasoning, key alignments, concerns
- Threshold: 70+ = "strong match", 50-69 = "potential match"

**Job Response Includes:**
- Full job details (requirements, responsibilities, compensation)
- Structured match evaluation with reasoning
- Application link for direct apply

---

## Priority Articles System

Manually assign specific articles to specific candidates that will ALWAYS appear in their emails regardless of semantic matching.

**Database Configuration** (via SQL or scripts):

```sql
INSERT INTO candidate_priority_articles (candidate_id, news_id, priority, notes)
VALUES ('pub_lnkd_123456', 1056, 1, 'Company recognition article');
```

Priority articles appear first in `blog_matches` array with `is_priority: true` flag.

---

## Support

For API issues or questions:
- GitHub: [Natera Blog Crawler Repository](https://github.com/Cahil-findem/natera-blog-crawler)
- Check `/api/health` endpoint to verify service status

---

## Changelog

### v1.0.0 (Current)
- Initial API release
- Three-field embedding system
- Blog article matching
- Job matching with LLM evaluation
- Priority articles support
- Context update functionality
