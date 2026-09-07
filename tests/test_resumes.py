def test_upload_valid_pdf(client, auth_headers, sample_pdf_bytes):
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["file_name"] == "resume.pdf"


def test_upload_rejects_non_pdf_extension(client, auth_headers, sample_pdf_bytes):
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("resume.txt", sample_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 400


def test_upload_rejects_spoofed_content_type(client, auth_headers):
    fake_pdf = b"this is definitely not a pdf"
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
    )
    assert response.status_code == 400  # caught by the magic-bytes check


def test_upload_without_auth_rejected(client, sample_pdf_bytes):
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.pdf", sample_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 401