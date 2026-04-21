import io
import json
import csv
import os
from flask import Flask, request, jsonify, render_template, send_file
from waitress import serve
from dotenv import load_dotenv

load_dotenv()

from ai_client import extract_document_data
from schemas import get_schema, list_schemas
from document_processor import prepare_image, pdf_to_images, pdf_page_count

app = Flask(__name__, template_folder=".")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/schemas")
def schemas():
    return jsonify(list_schemas())


@app.route("/extract", methods=["POST"])
def extract():
    """Single image / first page of PDF extraction."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    schema_name = request.form.get("schema", "invoice")
    schema = get_schema(schema_name)

    # Handle custom schema fields sent as JSON string
    custom_fields_raw = request.form.get("custom_fields")
    if schema_name == "custom" and custom_fields_raw:
        try:
            schema = {"label": "Custom", "fields": json.loads(custom_fields_raw)}
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid custom fields JSON"}), 400

    if not schema.get("fields"):
        return jsonify({"error": "Schema has no fields defined"}), 400

    try:
        file_bytes = file.read()
        image_bytes, mime_type = prepare_image(file_bytes, file.filename)
        result = extract_document_data(image_bytes, schema, mime_type)
        return jsonify({"success": True, "data": result, "schema": schema_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/extract/batch", methods=["POST"])
def extract_batch():
    """Multi-page PDF — extract all pages, return list of results."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    schema_name = request.form.get("schema", "invoice")
    schema = get_schema(schema_name)

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Batch mode only supports PDF files"}), 400

    try:
        pdf_bytes = file.read()
        pages = pdf_to_images(pdf_bytes)
        results = []

        for page_num, image_bytes, mime_type in pages:
            try:
                data = extract_document_data(image_bytes, schema, mime_type)
                results.append({"page": page_num, "success": True, "data": data})
            except Exception as e:
                results.append({"page": page_num, "success": False, "error": str(e)})

        return jsonify({"success": True, "pages": len(pages), "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/export/json", methods=["POST"])
def export_json():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    buf = io.BytesIO(json.dumps(data, indent=2).encode())
    buf.seek(0)
    return send_file(buf, mimetype="application/json",
                     as_attachment=True, download_name="extracted_data.json")


@app.route("/export/csv", methods=["POST"])
def export_csv():
    """Flatten extracted data to CSV — works best for single-level fields."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    buf = io.StringIO()
    writer = csv.writer(buf)

    # Flatten: skip nested lists, write key/value pairs
    writer.writerow(["Field", "Value"])
    for k, v in data.items():
        if isinstance(v, list):
            writer.writerow([k, json.dumps(v)])
        else:
            writer.writerow([k, v if v is not None else ""])

    buf.seek(0)
    byte_buf = io.BytesIO(buf.getvalue().encode())
    return send_file(byte_buf, mimetype="text/csv",
                     as_attachment=True, download_name="extracted_data.csv")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    serve(app, host="0.0.0.0", port=port)
