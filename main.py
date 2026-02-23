from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import resend
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Set Resend API key from environment variable
resend.api_key = os.getenv("RESEND_API_KEY")

class ContactForm(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    message: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "active_page": "home"})

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "active_page": "home"})

@app.get("/book-session", response_class=HTMLResponse)
async def book_session(request: Request):
    return templates.TemplateResponse("book.html", {"request": request, "active_page": "book"})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "active_page": "about"})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request, "active_page": "contact"})

@app.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request, "active_page": "pricing"})

@app.get("/faq", response_class=HTMLResponse)
async def faq(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request, "active_page": "faq"})

@app.get("/cancellation-policy", response_class=HTMLResponse)
async def cancellation_policy(request: Request):
    return templates.TemplateResponse("cancellation.html", {"request": request, "active_page": "cancellation"})

# Therapy Hub and Individual Therapy Pages (SEO-focused pages)
@app.get("/therapy", response_class=HTMLResponse)
async def therapy_hub(request: Request):
    return templates.TemplateResponse("seo/therapy.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/cbt", response_class=HTMLResponse)
async def therapy_cbt(request: Request):
    return templates.TemplateResponse("seo/therapy_cbt.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/trauma-informed", response_class=HTMLResponse)
async def therapy_trauma(request: Request):
    return templates.TemplateResponse("seo/therapy_trauma.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/dbt", response_class=HTMLResponse)
async def therapy_dbt(request: Request):
    return templates.TemplateResponse("seo/therapy_dbt.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/mindfulness", response_class=HTMLResponse)
async def therapy_mindfulness(request: Request):
    return templates.TemplateResponse("seo/therapy_mindfulness.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/act", response_class=HTMLResponse)
async def therapy_act(request: Request):
    return templates.TemplateResponse("seo/therapy_act.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/attachment-therapy", response_class=HTMLResponse)
async def therapy_attachment(request: Request):
    return templates.TemplateResponse("seo/therapy_attachment.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/solution-focused", response_class=HTMLResponse)
async def therapy_sfbt(request: Request):
    return templates.TemplateResponse("seo/therapy_sfbt.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/internal-family-systems", response_class=HTMLResponse)
async def therapy_ifs(request: Request):
    return templates.TemplateResponse("seo/therapy_ifs.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/narrative-therapy", response_class=HTMLResponse)
async def therapy_narrative(request: Request):
    return templates.TemplateResponse("seo/therapy_narrative.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/person-centred", response_class=HTMLResponse)
async def therapy_person_centred(request: Request):
    return templates.TemplateResponse("seo/therapy_person_centred.html", {"request": request, "active_page": "therapy"})

@app.get("/therapy/spiritual-care", response_class=HTMLResponse)
async def therapy_spiritual(request: Request):
    return templates.TemplateResponse("seo/therapy_spiritual.html", {"request": request, "active_page": "therapy"})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/images/logo.svg")

@app.post("/api/contact")
async def send_contact_email(form: ContactForm):
    try:
        params = {
            "from": "Innera Contact Form <onboarding@resend.dev>",
            "to": ["elfgokce@gmail.com"],
            "subject": f"New Contact Form Message from {form.firstName} {form.lastName}",
            "html": f"""
                <h2>New Contact Form Submission</h2>
                <p><strong>From:</strong> {form.firstName} {form.lastName}</p>
                <p><strong>Email:</strong> {form.email}</p>
                <p><strong>Message:</strong></p>
                <p>{form.message.replace(chr(10), '<br>')}</p>
            """
        }

        email = resend.Emails.send(params)
        return JSONResponse(content={"success": True, "id": email["id"]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

