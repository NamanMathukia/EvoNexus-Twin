from fastapi import APIRouter, HTTPException, UploadFile, File
from api.utils.file_extractor import extract_text_from_file
from src.llm_parser import parse_resume_to_features
from src.predict import predict_full
from api.schemas import TextEvaluateRequest

router = APIRouter()

@router.post("/evaluate")
async def evaluate_candidate_text(request: TextEvaluateRequest):
    raw_text = request.resume_text
    
    if not raw_text or len(raw_text) < 20:
        raise HTTPException(status_code=400, detail="Could not extract enough text from input.")
        
    try:
        print("Extracting features from text input...")
        extracted_features = parse_resume_to_features(raw_text)
        
        print("Running ML Pipeline...")
        final_results = predict_full(extracted_features)
        
        return {
            "status": "success",
            "filename": "text_input",
            "extracted_data": extracted_features,
            "analysis": final_results
        }
    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate_file")
async def evaluate_candidate_file(file: UploadFile = File(...)):
    # 1. Extract raw text from the uploaded PDF/DOCX
    raw_text = await extract_text_from_file(file)
    
    if not raw_text or len(raw_text) < 20:
        raise HTTPException(status_code=400, detail="Could not extract enough text from file.")
        
    try:
        # 2. Same pipeline as before
        print(f"Extracting features for {file.filename}...")
        extracted_features = parse_resume_to_features(raw_text)
        
        print("Running ML Pipeline...")
        final_results = predict_full(extracted_features)
        
        return {
            "status": "success",
            "filename": file.filename,
            "extracted_data": extracted_features,
            "analysis": final_results
        }
    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))