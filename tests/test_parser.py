"""Tests for resume parser service."""


import pytest

from hr_system.services.resume_parser import (
    extract_education,
    extract_email,
    extract_experience_years,
    extract_name,
    extract_phone,
    extract_skills,
    extract_text,
    parse_resume,
)

SAMPLE_RESUME = """John Doe
john.doe@example.com
+1-555-123-4567

Objective
Experienced software engineer seeking a challenging role.

Skills
Python, JavaScript, React, Docker, AWS, PostgreSQL, Redis, CI/CD

Experience
Senior Software Engineer at TechCorp (2019-2024)
- Led development of microservices architecture
- Managed team of 4 engineers

Software Engineer at StartupXYZ (2016-2019)
- Built REST APIs in Python/Flask
- Implemented CI/CD pipelines

Education
M.S. Computer Science, MIT, 2016
B.S. Mathematics, UCLA, 2014
"""


def test_extract_email():
    assert extract_email(SAMPLE_RESUME) == "john.doe@example.com"
    assert extract_email("no email here") is None


def test_extract_phone():
    assert extract_phone(SAMPLE_RESUME) is not None
    phone = extract_phone(SAMPLE_RESUME)
    assert "555" in phone


def test_extract_name():
    name = extract_name(SAMPLE_RESUME)
    assert name == "John Doe"


def test_extract_skills():
    skills = extract_skills(SAMPLE_RESUME)
    assert skills is not None
    assert "Python" in skills


def test_extract_experience_years():
    years = extract_experience_years(SAMPLE_RESUME)
    assert years is not None
    assert years >= 5  # 2019-2024 + 2016-2019 = 8 years


def test_extract_education():
    education = extract_education(SAMPLE_RESUME)
    assert education is not None
    assert "MIT" in education


def test_extract_text_txt(tmp_path):
    """Test extracting text from a .txt file."""
    txt_file = tmp_path / "resume.txt"
    txt_file.write_text("Hello World\njohn@test.com")
    text = extract_text(txt_file)
    assert "Hello World" in text
    assert "john@test.com" in text


def test_extract_text_unsupported(tmp_path):
    """Test that unsupported formats raise an error."""
    bad_file = tmp_path / "resume.xyz"
    bad_file.write_text("content")
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text(bad_file)


def test_parse_resume(tmp_path):
    """Test full resume parsing pipeline."""
    resume_file = tmp_path / "test_resume.txt"
    resume_file.write_text(SAMPLE_RESUME)

    result = parse_resume(resume_file)
    assert result["name"] == "John Doe"
    assert result["email"] == "john.doe@example.com"
    assert result["phone"] is not None
    assert result["skills"] is not None
    assert result["experience_years"] is not None
    assert result["education"] is not None
    assert "Python" in result["text"]
