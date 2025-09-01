import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os
from typing import List

from api import main as run_pipeline
from utils.db import save_result, get_all_results, db
from utils.validation import validate_analysis
from utils.helper import serialize_mongo
from utils.email_utils import send_email
from bson import ObjectId

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run-pipeline")
async def trigger_pipeline_from_uploads(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    jd: UploadFile = File(...),
    resumes: List[UploadFile] = File(...),
):
    try:
        temp_dir = tempfile.mkdtemp()
        resume_folder = os.path.join(temp_dir, "resumes")
        jd_folder = os.path.join(temp_dir, "jd")

        os.makedirs(resume_folder, exist_ok=True)
        os.makedirs(jd_folder, exist_ok=True)

        jd_path = os.path.join(jd_folder, jd.filename)
        with open(jd_path, "wb") as f:
            f.write(await jd.read())

        resume_paths = []
        for resume in resumes:
            resume_path = os.path.join(resume_folder, resume.filename)
            with open(resume_path, "wb") as f:
                f.write(await resume.read())
            resume_paths.append(resume_path)

        results = run_pipeline(resume_folder, jd_folder)

        saved_records = []

        for resume_file, result_dict in zip(resumes, results):
            resume_name = os.path.splitext(resume_file.filename)[0].replace(" ", "_")
            jd_name = os.path.splitext(jd.filename)[0].replace(" ", "_")
            result_key = f"{resume_name}_vs_{jd_name}"

            raw_analysis = result_dict.get(result_key, {})
            analysis = validate_analysis(raw_analysis)

            overall_score = analysis.get("OverallMatchPercentage", 0)
            shortlisted_flag = "yes" if overall_score > 60 else "no"

            record = {
                "name": name,
                "email": email,
                "jd": jd.filename,
                "resume": resume_file.filename,
                "result": {
                    result_key: analysis,
                    "shortlisted": shortlisted_flag
                }
            }

            record_id = save_result(record)
            record["_id"] = record_id

            saved_records.append(record)

        return JSONResponse(
            content=serialize_mongo({
                "status": "success",
                "message": "Processed successfully",
                "records": saved_records
            }),
            status_code=200,
        )

    except Exception as e:
        print("[ERROR] Pipeline failed:", e)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )
        
@app.get("/history")
async def get_history(page: int = Query(1, ge=1), limit: int = Query(8, ge=1)):
    try:
        results = get_all_results()
        total = len(results)

        start = (page - 1) * limit
        end = start + limit
        paginated = results[start:end]

        formatted = [r.get("result", {}) for r in paginated]

        return formatted

    except Exception as e:
        return {"status": "error", "message": str(e)}