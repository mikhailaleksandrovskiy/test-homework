from fastapi import FastAPI, File, UploadFile
from starlette.responses import FileResponse
from pathlib import Path
from hashlib import md5

app = FastAPI()

db = []

store_path = Path('store')
try:
    store_path.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    pass


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    name = str(file.filename)
    file_ext_split = name.split(".")
    file_ext = file_ext_split[-1]
    name_encode = md5(name.encode())
    name_encode_str = name_encode.hexdigest()
    path = name_encode_str[:2]
    new_destination = store_path / path
    try:
        new_destination.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        pass
    result_save = f'{new_destination}/{name_encode_str}.{file_ext}'
    with open(result_save, "wb+") as save_dir:
        save_dir.write(file.file.read())
    db.append({"path": new_destination, "file": name_encode_str, "extension": "." + file_ext})
    return db[-1]


@app.get("/download/")
def download_file(hash: str):
    x = dict((i['file'], i['extension']) for i in db)
    if hash in x:
        extension = x[hash]
        full_name = str(hash + extension)
        download_path = f'store/' + hash[:2] + "/" + full_name
        return FileResponse(path=download_path, filename=full_name)
    else:
        return "No such file"


@app.get("/delete/")
def delete_file(hash: str):
    x = dict((i['file'], i['extension']) for i in db)
    if hash in x:
        extension = x[hash]
        full_name = str(hash + extension)
        db[:] = [d for d in db if d.get('file') != hash]
    else:
        return "No such file"