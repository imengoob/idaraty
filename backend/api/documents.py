from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal
from sqlalchemy import text
import os, re

router = APIRouter(prefix="/documents", tags=["Documents"])
PDF_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "pdfs")


class DocumentSearchRequest(BaseModel):
    query: str
    language: str = "fr"


@router.post("/search")
def search_documents(data: DocumentSearchRequest):
    db = SessionLocal()
    try:
        q        = data.query.lower().strip()
        keywords = [w for w in re.findall(r'\w+', q) if len(w) >= 3]
        if not keywords:
            return {"success": False, "results": [], "count": 0}

        conds  = " OR ".join([
            f"LOWER(nom_procedure) LIKE :kw{i} OR LOWER(tags_fr) LIKE :kw{i} "
            f"OR LOWER(tags_ar) LIKE :kw{i} OR LOWER(description_fr) LIKE :kw{i} "
            f"OR LOWER(description_ar) LIKE :kw{i}"
            for i, _ in enumerate(keywords)
        ])
        params = {f"kw{i}": f"%{kw}%" for i, kw in enumerate(keywords)}

        rows = db.execute(text(f"""
            SELECT id, nom_procedure, nom_fichier, chemin_fichier, type,
                   description_fr, description_ar
            FROM documents WHERE {conds} ORDER BY id LIMIT 5
        """), params).fetchall()

        results = [
            {"id": r[0], "nom_procedure": r[1], "nom_fichier": r[2],
             "chemin_fichier": r[3], "type": r[4],
             "description_fr": r[5], "description_ar": r[6]}
            for r in rows
        ]
        return {"success": bool(results), "results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/list")
def list_documents():
    db = SessionLocal()
    try:
        rows = db.execute(text(
            "SELECT id, nom_procedure, nom_fichier, chemin_fichier, type, "
            "description_fr, description_ar FROM documents ORDER BY nom_procedure"
        )).fetchall()
        return {
            "success": True, "count": len(rows),
            "documents": [
                {"id": r[0], "nom_procedure": r[1], "nom_fichier": r[2],
                 "chemin_fichier": r[3], "type": r[4],
                 "description_fr": r[5], "description_ar": r[6]}
                for r in rows
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/download/{filename}")
def download_document(filename: str):
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")
    file_path = os.path.join(PDF_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Fichier '{filename}' introuvable")
    return FileResponse(path=file_path, media_type="application/pdf", filename=filename)