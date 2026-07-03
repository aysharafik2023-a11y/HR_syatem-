"""Tests for API endpoints."""




def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert data["total_candidates"] == 0
    assert data["total_jobs"] == 0


def test_create_job(client):
    """Test creating a job posting."""
    job_data = {
        "title": "Senior Python Developer",
        "department": "Engineering",
        "description": "We are looking for a senior Python developer to join our team.",
        "requirements": "5+ years Python experience, FastAPI, SQLAlchemy, Docker",
        "preferred_skills": "Machine learning, AWS, Kubernetes",
        "min_experience_years": 5.0,
    }
    response = client.post("/jobs/", json=job_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Senior Python Developer"
    assert data["department"] == "Engineering"
    assert data["is_active"] is True


def test_list_jobs(client):
    """Test listing job postings."""
    # Create a job first
    job_data = {
        "title": "Data Scientist",
        "description": "Looking for a data scientist with ML expertise.",
        "requirements": "Python, TensorFlow, statistics, 3 years experience",
    }
    client.post("/jobs/", json=job_data)

    response = client.get("/jobs/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Data Scientist"


def test_get_job(client):
    """Test getting a specific job."""
    job_data = {
        "title": "Frontend Developer",
        "description": "React developer needed for our web applications.",
        "requirements": "React, TypeScript, 2+ years experience",
    }
    create_response = client.post("/jobs/", json=job_data)
    job_id = create_response.json()["id"]

    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Frontend Developer"


def test_get_job_not_found(client):
    """Test getting a non-existent job."""
    response = client.get("/jobs/999")
    assert response.status_code == 404


def test_update_job(client):
    """Test updating a job posting."""
    job_data = {
        "title": "DevOps Engineer",
        "description": "DevOps engineer to manage our infrastructure.",
        "requirements": "AWS, Terraform, Docker, CI/CD pipelines",
    }
    create_response = client.post("/jobs/", json=job_data)
    job_id = create_response.json()["id"]

    update_data = {"title": "Senior DevOps Engineer", "min_experience_years": 4.0}
    response = client.patch(f"/jobs/{job_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Senior DevOps Engineer"
    assert response.json()["min_experience_years"] == 4.0


def test_delete_job(client):
    """Test deleting a job posting."""
    job_data = {
        "title": "QA Engineer",
        "description": "Quality assurance engineer for our testing team.",
        "requirements": "Selenium, pytest, 2 years experience",
    }
    create_response = client.post("/jobs/", json=job_data)
    job_id = create_response.json()["id"]

    response = client.delete(f"/jobs/{job_id}")
    assert response.status_code == 204

    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 404


def test_upload_resume_txt(client, tmp_path):
    """Test uploading a text resume."""
    resume_content = """John Smith
john.smith@example.com
+1-555-123-4567

Skills
Python, FastAPI, SQLAlchemy, Docker, AWS, Machine Learning

Experience
Senior Software Engineer at Tech Corp (2019-2024)
- Built REST APIs serving 1M+ requests/day
- Led team of 5 engineers

Education
B.S. Computer Science, MIT, 2015
"""
    resume_file = tmp_path / "john_smith_resume.txt"
    resume_file.write_text(resume_content)

    with resume_file.open("rb") as f:
        response = client.post(
            "/resumes/upload",
            files={"file": ("john_smith_resume.txt", f, "text/plain")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["email"] == "john.smith@example.com"
    assert data["phone"] is not None


def test_upload_resume_no_email(client, tmp_path):
    """Test uploading a resume with no email fails gracefully."""
    resume_content = "Just some text without an email address"
    resume_file = tmp_path / "bad_resume.txt"
    resume_file.write_text(resume_content)

    with resume_file.open("rb") as f:
        response = client.post(
            "/resumes/upload",
            files={"file": ("bad_resume.txt", f, "text/plain")},
        )

    assert response.status_code == 422


def test_upload_unsupported_format(client, tmp_path):
    """Test uploading an unsupported file format."""
    bad_file = tmp_path / "resume.xyz"
    bad_file.write_text("content")

    with bad_file.open("rb") as f:
        response = client.post(
            "/resumes/upload",
            files={"file": ("resume.xyz", f, "application/octet-stream")},
        )

    assert response.status_code == 400


def test_list_candidates(client, tmp_path):
    """Test listing candidates."""
    # Upload a resume first
    resume_content = """Jane Doe
jane.doe@example.com

Skills: JavaScript, React, Node.js

Experience: 3 years at Startup Inc (2021-2024)

Education: B.S. CS from Stanford
"""
    resume_file = tmp_path / "jane_resume.txt"
    resume_file.write_text(resume_content)

    with resume_file.open("rb") as f:
        client.post(
            "/resumes/upload",
            files={"file": ("jane_resume.txt", f, "text/plain")},
        )

    response = client.get("/resumes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "jane.doe@example.com"


def test_screening_no_candidates(client):
    """Test screening with no candidates."""
    job_data = {
        "title": "Backend Developer",
        "description": "Backend developer for Python services.",
        "requirements": "Python, FastAPI, databases",
    }
    create_response = client.post("/jobs/", json=job_data)
    job_id = create_response.json()["id"]

    response = client.post("/screening/run", json={"job_id": job_id})
    assert response.status_code == 404


def test_screening_job_not_found(client):
    """Test screening with a non-existent job."""
    response = client.post("/screening/run", json={"job_id": 999})
    assert response.status_code == 404


def test_full_screening_workflow(client, tmp_path):
    """Test the complete screening workflow: upload resumes, create job, run screening."""
    # Upload candidate 1
    resume1 = """Alice Johnson
alice.johnson@techcorp.com
+1-555-100-2000

Skills
Python, FastAPI, Django, PostgreSQL, Docker, AWS, CI/CD, REST APIs

Experience
Senior Backend Engineer at BigTech (2018-2024)
- Designed microservices handling 500K requests/day
- 6 years of Python development experience

Education
M.S. Computer Science, Stanford University, 2018
"""
    f1 = tmp_path / "alice_resume.txt"
    f1.write_text(resume1)
    with f1.open("rb") as f:
        client.post("/resumes/upload", files={"file": ("alice_resume.txt", f, "text/plain")})

    # Upload candidate 2
    resume2 = """Bob Williams
bob.williams@email.com
+1-555-200-3000

Skills
JavaScript, React, HTML, CSS, some Python

Experience
Frontend Developer at WebCo (2022-2024)
- Built responsive UIs
- 2 years experience

Education
B.A. Design, Art Institute, 2022
"""
    f2 = tmp_path / "bob_resume.txt"
    f2.write_text(resume2)
    with f2.open("rb") as f:
        client.post("/resumes/upload", files={"file": ("bob_resume.txt", f, "text/plain")})

    # Create a job
    job_data = {
        "title": "Senior Python Backend Developer",
        "department": "Engineering",
        "description": (
            "We need a senior Python backend developer"
            " to build scalable APIs and microservices."
        ),
        "requirements": (
            "5+ years Python, FastAPI or Django,"
            " PostgreSQL, Docker, AWS experience required."
        ),
        "preferred_skills": "Machine learning, Kubernetes, gRPC",
        "min_experience_years": 5.0,
    }
    job_response = client.post("/jobs/", json=job_data)
    job_id = job_response.json()["id"]

    # Run screening
    screening_response = client.post("/screening/run", json={"job_id": job_id})
    assert screening_response.status_code == 200
    data = screening_response.json()

    assert data["job_id"] == job_id
    assert data["total_candidates_screened"] == 2
    assert len(data["ranked_candidates"]) == 2

    # Alice should rank higher (more relevant experience)
    assert data["ranked_candidates"][0]["candidate"]["email"] == "alice.johnson@techcorp.com"
    assert data["ranked_candidates"][0]["rank"] == 1
    assert data["ranked_candidates"][1]["rank"] == 2

    # Verify scores are in valid range
    for rc in data["ranked_candidates"]:
        assert 0.0 <= rc["overall_score"] <= 1.0
        assert 0.0 <= rc["skills_score"] <= 1.0
        assert 0.0 <= rc["experience_score"] <= 1.0

    # Get ranked candidates via GET endpoint
    ranked_response = client.get(f"/screening/jobs/{job_id}/candidates")
    assert ranked_response.status_code == 200
    assert len(ranked_response.json()) == 2
