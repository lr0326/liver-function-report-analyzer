"""
Integration tests for the Flask API endpoints.
"""

import io
import json
import pytest


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_json_body(self, client):
        response = client.get("/api/health")
        data = response.get_json()
        assert data["status"] == "healthy"


class TestUploadEndpoint:
    def test_no_file_returns_400(self, client):
        response = client.post("/api/reports/upload")
        assert response.status_code == 400

    def test_unsupported_extension_returns_400(self, client):
        data = {"file": (io.BytesIO(b"content"), "report.docx")}
        response = client.post(
            "/api/reports/upload",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_empty_file_returns_400(self, client):
        data = {"file": (io.BytesIO(b""), "report.pdf")}
        response = client.post(
            "/api/reports/upload",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 400


class TestTextAnalysisEndpoint:
    def test_no_body_returns_400(self, client):
        response = client.post(
            "/api/reports/text",
            content_type="application/json",
            data=json.dumps({}),
        )
        assert response.status_code == 400

    def test_empty_text_returns_400(self, client):
        response = client.post(
            "/api/reports/text",
            content_type="application/json",
            data=json.dumps({"text": "   "}),
        )
        assert response.status_code == 400

    def test_valid_text_returns_200(self, client):
        response = client.post(
            "/api/reports/text",
            content_type="application/json",
            data=json.dumps({"text": "ALT 30 U/L 7-56\nAST 25 U/L 10-40"}),
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "report_id" in data

    def test_valid_text_with_abnormal_returns_risk_score(self, client):
        response = client.post(
            "/api/reports/text",
            content_type="application/json",
            data=json.dumps({"text": "ALT 200 U/L 7-56"}),
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["risk_score"] > 0
        assert data["abnormal_count"] > 0


class TestGetAnalysisEndpoint:
    def test_nonexistent_report_returns_404(self, client):
        response = client.get("/api/reports/analysis/nonexistent-id")
        assert response.status_code == 404

    def test_existing_report_is_retrievable(self, client):
        # First, create a report via the text endpoint
        create_response = client.post(
            "/api/reports/text",
            content_type="application/json",
            data=json.dumps({"text": "ALT 30 U/L 7-56"}),
        )
        assert create_response.status_code == 200
        report_id = create_response.get_json()["report_id"]

        # Then retrieve it
        get_response = client.get(f"/api/reports/analysis/{report_id}")
        assert get_response.status_code == 200
        data = get_response.get_json()
        assert data["report_id"] == report_id
