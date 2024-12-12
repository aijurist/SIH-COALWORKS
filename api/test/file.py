from fastapi import FastAPI, UploadFile, File
import os
import shutil

app = FastAPI()

@app.post("/upload-file")
async def upload_file_endpoint(file: UploadFile = File(...)):
    dir_fp = os.path.abspath("source_data")
    if not os.path.exists(dir_fp):
        os.makedirs(dir_fp)
    fp = os.path.join(dir_fp, file.filename)
    with open(fp, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": f"File '{file.filename}' uploaded successfully!"}
