import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.simulation import RemediationRecord
from app.schemas.remediation import RemediationGenerateRequest, RemediationOut, PatchValidation
from app.services.remediation_engine import RemediationService

router = APIRouter(prefix="/api/remediation", tags=["remediation"])
svc = RemediationService()


def _out(rec: RemediationRecord) -> RemediationOut:
    return RemediationOut(
        id=rec.id, run_id=rec.run_id, website_test_id=rec.website_test_id, url=rec.url,
        source=rec.source, failure_description=rec.failure_description, root_cause=rec.root_cause,
        affected_components=json.loads(rec.affected_components_json or "[]"),
        recommendation=rec.recommendation, patch_language=rec.patch_language,
        patch_text=rec.patch_text, expected_improvement=rec.expected_improvement,
        validation=PatchValidation(**json.loads(rec.validation_json or '{"status":"pending","checks":[],"logs":[]}')),
        approved=bool(rec.approved),
    )


@router.post("/generate", response_model=RemediationOut)
def generate(req: RemediationGenerateRequest, db: Session = Depends(get_db)):
    try:
        if req.website_test_id:
            rec = svc.generate_for_website_test(db, req.website_test_id, req.language)
        elif req.run_id:
            rec = svc.generate_for_run(db, req.run_id, req.language)
        else:
            raise HTTPException(status_code=400, detail="Provide run_id or website_test_id.")
    except ValueError as e:
        raise HTTPException(404, str(e))
    return _out(rec)


@router.post("/{rec_id}/validate", response_model=RemediationOut)
def validate(rec_id: int, db: Session = Depends(get_db)):
    rec = db.query(RemediationRecord).filter(RemediationRecord.id == rec_id).first()
    if not rec: raise HTTPException(404, "Remediation not found")
    return _out(svc.validate(db, rec))


@router.post("/{rec_id}/approve", response_model=RemediationOut)
def approve(rec_id: int, db: Session = Depends(get_db)):
    rec = db.query(RemediationRecord).filter(RemediationRecord.id == rec_id).first()
    if not rec: raise HTTPException(404, "Remediation not found")
    rec.approved = True
    db.commit(); db.refresh(rec)
    return _out(rec)


@router.get("/run/{run_id}", response_model=list[RemediationOut])
def by_run(run_id: int, db: Session = Depends(get_db)):
    recs = db.query(RemediationRecord).filter(RemediationRecord.run_id == run_id).order_by(RemediationRecord.id.desc()).all()
    return [_out(r) for r in recs]


@router.get("/website-test/{test_id}", response_model=list[RemediationOut])
def by_website_test(test_id: int, db: Session = Depends(get_db)):
    recs = db.query(RemediationRecord).filter(RemediationRecord.website_test_id == test_id).order_by(RemediationRecord.id.desc()).all()
    return [_out(r) for r in recs]
