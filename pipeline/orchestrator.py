import time
from pydantic import ValidationError
from database.models import PipelineRun
from ingestion.validation import JobRecord
from pipeline.transform import transform
from pipeline.load import load_one

def run_pipeline(session, rows):
    start=time.perf_counter(); good=bad=dupes=0; errors=[]
    for i,row in enumerate(rows, start=1):
        try:
            d=transform(row); valid=JobRecord(**{k:v for k,v in d.items() if k in JobRecord.model_fields and k != "skills"})
            result=load_one(session,d)
            if result == "duplicate": dupes += 1
            else: good += 1
        except Exception as e: bad += 1; errors.append(f"Row {i}: {str(e)[:240]}")
    duration=time.perf_counter()-start
    run=PipelineRun(status="completed" if not bad else "completed_with_errors", processed=len(rows), successful=good, rejected=bad, duplicates=dupes, duration_seconds=duration, details="\n".join(errors))
    session.add(run); session.commit()
    return {"processed":len(rows),"successful":good,"rejected":bad,"duplicates":dupes,"duration_seconds":duration,"errors":errors,"run_id":run.id}
