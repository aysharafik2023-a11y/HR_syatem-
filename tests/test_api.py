"""API endpoint tests."""



class TestHealthCheck:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "endpoints" in data

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestJobPostings:
    def test_create_job_posting(self, client, sample_job_posting):
        response = client.post("/api/v1/jobs/", json=sample_job_posting)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_job_posting["title"]
        assert data["department"] == sample_job_posting["department"]
        assert data["id"] == 1

    def test_list_job_postings(self, client, sample_job_posting):
        client.post("/api/v1/jobs/", json=sample_job_posting)
        response = client.get("/api/v1/jobs/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_job_posting(self, client, sample_job_posting):
        client.post("/api/v1/jobs/", json=sample_job_posting)
        response = client.get("/api/v1/jobs/1")
        assert response.status_code == 200
        assert response.json()["title"] == sample_job_posting["title"]

    def test_get_nonexistent_job(self, client):
        response = client.get("/api/v1/jobs/999")
        assert response.status_code == 404

    def test_update_job_posting(self, client, sample_job_posting):
        client.post("/api/v1/jobs/", json=sample_job_posting)
        response = client.patch("/api/v1/jobs/1", json={"title": "Lead Python Developer"})
        assert response.status_code == 200
        assert response.json()["title"] == "Lead Python Developer"

    def test_delete_job_posting(self, client, sample_job_posting):
        client.post("/api/v1/jobs/", json=sample_job_posting)
        response = client.delete("/api/v1/jobs/1")
        assert response.status_code == 204


class TestCandidates:
    def test_submit_resume_text(self, client, sample_candidate):
        response = client.post("/api/v1/resumes/submit", json=sample_candidate)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_candidate["name"]
        assert data["email"] == sample_candidate["email"]
        assert data["skills"] is not None

    def test_duplicate_email_rejected(self, client, sample_candidate):
        client.post("/api/v1/resumes/submit", json=sample_candidate)
        response = client.post("/api/v1/resumes/submit", json=sample_candidate)
        assert response.status_code == 409

    def test_list_candidates(self, client, sample_candidate):
        client.post("/api/v1/resumes/submit", json=sample_candidate)
        response = client.get("/api/v1/resumes/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_candidate(self, client, sample_candidate):
        client.post("/api/v1/resumes/submit", json=sample_candidate)
        response = client.get("/api/v1/resumes/1")
        assert response.status_code == 200
        assert response.json()["email"] == sample_candidate["email"]


class TestScreening:
    def test_run_screening(self, client, sample_job_posting, sample_candidate):
        client.post("/api/v1/jobs/", json=sample_job_posting)
        client.post("/api/v1/resumes/submit", json=sample_candidate)

        response = client.post("/api/v1/screening/run/1?top_n=5")
        assert response.status_code == 200
        data = response.json()
        assert data["job_posting_id"] == 1
        assert data["total_candidates"] == 1
        assert data["screened_count"] == 1
        assert len(data["top_candidates"]) == 1
        assert data["top_candidates"][0]["application"]["match_score"] > 0

    def test_screening_no_candidates(self, client, sample_job_posting):
        client.post("/api/v1/jobs/", json=sample_job_posting)
        response = client.post("/api/v1/screening/run/1")
        assert response.status_code == 404

    def test_screening_nonexistent_job(self, client):
        response = client.post("/api/v1/screening/run/999")
        assert response.status_code == 404

    def test_get_screening_results(self, client, sample_job_posting, sample_candidate):
        client.post("/api/v1/jobs/", json=sample_job_posting)
        client.post("/api/v1/resumes/submit", json=sample_candidate)
        client.post("/api/v1/screening/run/1")

        response = client.get("/api/v1/screening/results/1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["rank"] == 1

    def test_screening_statistics(self, client, sample_job_posting, sample_candidate):
        client.post("/api/v1/jobs/", json=sample_job_posting)
        client.post("/api/v1/resumes/submit", json=sample_candidate)
        client.post("/api/v1/screening/run/1")

        response = client.get("/api/v1/screening/statistics/1")
        assert response.status_code == 200
        data = response.json()
        assert data["total_applications"] == 1
        assert data["average_score"] > 0

    def test_update_application_status(self, client, sample_job_posting, sample_candidate):
        client.post("/api/v1/jobs/", json=sample_job_posting)
        client.post("/api/v1/resumes/submit", json=sample_candidate)
        client.post("/api/v1/screening/run/1")

        response = client.patch("/api/v1/screening/applications/1/status?status=shortlisted")
        assert response.status_code == 200
        assert response.json()["status"] == "shortlisted"
