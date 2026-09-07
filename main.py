from fastapi import FastAPI, Request
import json

app = FastAPI()

# كلمات مفتاحية بالدارجة - 3 أسئلة فقط
KEYWORDS_CONFIRM = ["موعد", "امتى", "وقتاش", "فين", "موعدي", "rendez-vous", "rdv"]
KEYWORDS_RESCHEDULE = ["أجل", "اجل", "مقدرش", "ما نجيش", "روطار", "نأجل", "نبدل"]
KEYWORDS_DELAY = ["تعطلت", "تعطل", "جاي", "طريق", "زحام", "روطار", "غادي نتعطل"]

# أجوبة بالدارجة - خفيفة
ANSWERS = {
    "confirm": "السلام - موعدك الإثنين مع 10h مؤكد - اجي قبل 15 دقيقة - العيادة فمراكش - إلا بغيتي تأجل قول ليا 'نأجل'",
    "reschedule": "واخا - كتب أجل للأربعاء - قول ليا النهار اللي يناسبك - الإثنين ولا الأربعاء - وغادي نأكد لك",
    "delay": "واخا - كنستناوك - عيط لينا فالعيادة إلا تعطلتي بزاف - 05XXXXXXXX",
    "default": "السلام - معك عيادة الدكتور - إلا بغيتي الموعد قول 'موعدي' - إلا بغيتي تأجل قول 'نأجل' - إلا تعطلتي قول 'تعطلت'"
}

# تسجيل كلشي - باش ما يضيع والو
LOGS = []

def detect_intent(text: str):
    text = text.lower()
    if any(k in text for k in KEYWORDS_CONFIRM):
        return "confirm"
    if any(k in text for k in KEYWORDS_RESCHEDULE):
        return "reschedule"
    if any(k in text for k in KEYWORDS_DELAY):
        return "delay"
    return "default"

@app.get("/")
def home():
    return {"status": "البوت خدام - 3 أسئلة - خير للبلاد والعباد", "logs_count": len(LOGS)}

# Webhook Verification ديال ميتا
@app.get("/webhook")
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    # غادي نبدلو VERIFY_TOKEN من بعد
    if mode == "subscribe" and token == "BOT_MARRAKECH_500":
        return int(challenge)
    return {"error": "verification failed"}

# استقبال الرسائل
@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    try:
        # استخراج الرسالة
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        
        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            text = message["text"]["body"] if "text" in message else ""
            
            # تسجيل - ديما خدام
            LOGS.append({
                "from": from_number,
                "text": text,
                "time": value.get("metadata", {}).get("phone_number_id", "")
            })
            
            # تحديد النية
            intent = detect_intent(text)
            answer = ANSWERS[intent]
            
            # هنا كنصيفطو الجواب - فاللول كنطبعو فقط
            # منين ناخدو ACCESS_TOKEN غادي نفعّلو الإرسال الحقيقي
            print(f"من: {from_number} - كتب: {text} - النية: {intent} - الجواب: {answer}")
            
            # TODO: إرسال عبر WhatsApp Cloud API
            # requests.post(f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages", ...)
            
            return {"status": "received", "intent": intent, "answer": answer}
            
    except Exception as e:
        print(f"خطأ: {e}")
    
    return {"status": "ok"}

# تقرير يومي - للطبيب
@app.get("/report")
def daily_report():
    return {
        "اليوم": f"{len(LOGS)} مريض صيفط",
        "التفاصيل": LOGS[-20:],  # آخر 20
        "الخلاصة": "8 تأكدو - 2 أجلو - مثال"
    }


import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
