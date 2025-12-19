from fastapi import FastAPI, UploadFile, Form, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import traceback
import os
from dotenv import load_dotenv
load_dotenv()

from utils import model_utils, file_utils, youtube_utils

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memuat model dengan penanganan error
try:
    model, tokenizer, thresholds, label_names = model_utils.load_model_and_tokenizer()
    model_loaded = True
except Exception as e:
    model_loaded = False
    startup_error = str(e)
    print(f"FATAL: Gagal memuat model saat startup: {startup_error}")
    traceback.print_exc()


def build_results_with_interpretation(texts):
    """
    Fungsi ini mengambil teks mentah, melakukan prediksi, dan membangun hasil
    interpretasi yang kaya dengan logika fallback dan prioritas.
    """
    preds = model_utils.predict_texts(texts, model, tokenizer, thresholds, label_names)

    kategori_map = {
        "Religion": "Agama", "Race": "Ras", "Physical": "Fisik",
        "Gender": "Gender", "Other": "Lainnya"
    }

    results_final = []
    for p in preds:
        result_item = {"text": p.get("text")}

        # Jika bukan Hate Speech, langsung beri nilai default dan lanjutkan
        if p.get('HS', 0) == 0:
            result_item['Target'] = '-'
            result_item['Kategori'] = '-'
            result_item['Level'] = '-'
            result_item['HS'] = "Tidak"
            results_final.append(result_item)
            continue

        # Jika terdeteksi sebagai Hate Speech, proses lebih lanjut
        result_item['HS'] = "Ya"

        # --- Interpretasi Target ---
        target = []
        if p.get("HS_Individual"): target.append("Individu")
        if p.get("HS_Group"): target.append("Kelompok")
        if not target:
            target_scores = {
                "Individu": p.get("HS_Individual_score", 0),
                "Kelompok": p.get("HS_Group_score", 0)
            }
            if any(s > 0 for s in target_scores.values()):
                highest_target = max(target_scores, key=target_scores.get)
                target.append(highest_target)
        result_item["Target"] = ", ".join(target) if target else "Umum"

        # --- Interpretasi Kategori ---
        kategori = []
        kategori_scores = {}
        for cat_en, cat_id in kategori_map.items():
             if p.get(f"HS_{cat_en}"):
                 kategori.append(cat_id)
             kategori_scores[cat_id] = p.get(f"HS_{cat_en}_score", 0) # Kumpulkan skor untuk fallback

        if not kategori:
            if any(s > 0 for s in kategori_scores.values()):
                highest_kategori = max(kategori_scores, key=kategori_scores.get)
                kategori.append(highest_kategori)
        result_item["Kategori"] = ", ".join(kategori) if kategori else "Lainnya"

        # --- Interpretasi Level  ---
        tingkat = []
        level_label = "-" 
        if p.get("HS_Strong"):
            level_label = "Kuat"
        elif p.get("HS_Moderate"):
            level_label = "Sedang"
        elif p.get("HS_Weak"):
            level_label = "Lemah"
        else: # Fallback jika HS=Ya tapi tidak ada level aktif
             level_scores = {
                 "Kuat": p.get("HS_Strong_score", 0),
                 "Sedang": p.get("HS_Moderate_score", 0),
                 "Lemah": p.get("HS_Weak_score", 0)
             }
             if any(s > 0 for s in level_scores.values()):
                  level_label = max(level_scores, key=level_scores.get)
             else:
                  level_label = "Lemah" # Default akhir
        result_item["Level"] = level_label

        results_final.append(result_item)

    return results_final


# --- Route Halaman Statis ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/deteksi", response_class=HTMLResponse)
def deteksi_page(request: Request):
    return templates.TemplateResponse("deteksi.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/help", response_class=HTMLResponse)
def help_page(request: Request):
    return templates.TemplateResponse("help.html", {"request": request})


# --- Route Prediksi dengan Penanganan Error ---
async def handle_prediction(prediction_func, *args):
    """Fungsi pembungkus untuk menangani error prediksi."""
    if not model_loaded:
        return JSONResponse(
            status_code=500,
            content={"error": f"Model gagal dimuat saat aplikasi dimulai: {startup_error}"}
        )
    try:
        results = prediction_func(*args)
        return JSONResponse(content={"results": results})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Error internal server: {str(e)}"}
        )

@app.post("/predict/text")
async def predict_text_endpoint(text: str = Form(...)):
    return await handle_prediction(build_results_with_interpretation, [text])

@app.post("/predict/file")
async def predict_file_endpoint(file: UploadFile = File(...)):
    try:
        texts = file_utils.process_file(file) 
        return await handle_prediction(build_results_with_interpretation, texts)
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Gagal memproses file: {str(e)}"}
        )

@app.post("/predict/youtube")
async def predict_youtube_endpoint(url: str = Form(...)):
    try:
        comments = youtube_utils.get_comments_from_video(url) 
        if not comments:
            return JSONResponse(content={"error": "Tidak ada komentar atau video tidak valid."}, status_code=400)
        return await handle_prediction(build_results_with_interpretation, comments)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Gagal mengambil komentar YouTube: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=True)
