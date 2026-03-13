from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import cleaning_data

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.post("/api/process")
async def process_banking_file(
	file: UploadFile = File(...),
	period_type: str = Form(...),
	value: str = Form(...),
	request_type: str = Form(...)
):
	if not file.filename.endswith('.csv'):
		raise HTTPException(status_code=400, detail="Fisierul trebuie sa fie .csv")

	try:
		contents = await file.read()
		raw_df = pd.read_csv(io.BytesIO(contents))
		
		if request_type == "spendings":
			result = cleaning_data.get_spendings_report(raw_df, period_type, value)
			return {
				"status": "success",
				"type": "spendings",
				"period": value,
				"data": result
			}
			
		elif request_type == "transfers":
			result = cleaning_data.get_transfers_report(raw_df, period_type, value)
			return {
				"status": "success",
				"type": "transfers",
				"period": value,
				"data": result
			}
			
		else:
			raise HTTPException(status_code=400, detail="request_type invalid")

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health_check():
	return {"status": "online"}