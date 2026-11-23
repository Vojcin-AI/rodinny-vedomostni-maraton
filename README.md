# 🎬 RODINNÝ VĚDOMOSTNÍ MARATON 🎮

Interaktivní webová aplikace pro rodinný kvíz s QR registrací týmů a průběžným přehledem odpovědí.

## 🚀 Jak to funguje?

### 1. **Admin** spustí aplikaci
```bash
python quiz_backend.py
```
App běží na: `http://localhost:5000`

### 2. **Admin se přihlásí** do panelu
- Jde na: `http://localhost:5000/admin`
- Heslo: `admin123`

### 3. **Admin vygeneruje QR kód**
- Klikne na "Vygeneruj QR Kód"
- Vytiskne jej pro týmy

### 4. **Týmy si naskenují QR kód**
- Jejich mobilní telefony otevřou: `http://localhost:5000/team`
- Zaregistrují se (jméno týmu)

### 5. **Admin spustí kvíz**
- Klikne "Spustit Kvíz"
- Zobrazí se první otázka
- Další otázku lze otevřít až poté, co odpoví všechny registrované týmy

### 6. **Týmy odpovídají**
- Vidí otázku na svých mobilech; časový limit se nepoužívá
- Zadají odpověď a odešlou ji
- Admin vidí, kdo píše odpověď, kdo ji už odeslal a kdo ještě čeká
- Správnost odpovědí se týmům během kola nezobrazuje

### 7. **Leaderboard se aktualizuje live**
- Na velkém displeji: `http://localhost:5000/leaderboard`
- Nebo v Admin panelu

### 8. **Konec kvízu**
- Admin klikne "Ukončit Kvíz"
- Vítěz je určen hned!

---

## 📱 Mobilní přístup - 2 možnosti

### **Varianta A: Lokální síť (WiFi)**
- Všichni na stejné WiFi
- Přijde jim odkaz přes QR kód
- Funguje offline (jen musí být na síti)

### **Varianta B: Data / Online (Fallback)**
- Pokud WiFi nefunguje, můžou používat data
- Admin si zjistí svou IP adresu
- Dá jí týmům (např. `http://192.168.1.100:5000/team`)

### **Varianta C: Papírová forma (Ultimate Fallback)**
- Pokud nefunguje nic
- Týmy odpovídají na papír
- Pro rozhodnutí remízy lze použít samostatnou doplňující otázku

---

## 🎯 Příklady otázek v databázi

Aktuálně jsou v systému sample otázky:
1. **Jak se jmenuje hlavní postava v pohádce "Tři oříšky"?** → `Matěj`
2. **Jaké jméno má postava ze "Zlatovlásky"?** → `Božena`
3. **Kterou pohádkou se rozumí "Popelka"?** → `Popelka`
4. **Kolik měla Popelka sester?** → `2`, `dvě`
5. **Jaké jméno má postava ze "Zvídavého Jiřího"?** → `Jiří`

---

## ⚙️ Přizpůsobení otázek

Chceš jiné otázky? Otevři `quiz_backend.py` a uprav sekci:

```python
def load_quiz(self):
    self.questions = [
        {
            'id': 1,
            'text': 'Tvá otázka?',
            'type': 'text',
            'correct_answers': ['odpověď1', 'odpověď2'],  # Variace
            'points': 1
        },
        # ... další otázky
    ]
```

**Tolerantní odpovědi:**
- `Popelka` = `popelka` = `POPELKA` ✅
- Bez diakritiky: `Matěj` = `Matej` ✅
- Více variant: `2` = `dvě` = `dve` ✅

---

## 🎨 Vzhled a změny

- **CSS:** `static/css/style.css`
- **Barvy:**
  - Primární: Tmavě modrá (`#2c3e50`)
  - Sekundární: Světle modrá (`#3498db`)
  - Accent: Oranžová-červená (`#e74c3c`)
  - Úspěch: Zelená (`#27ae60`)

---

## 🔐 Bezpečnost

- Admin heslo: `admin123`
- SessionID pro týmy: UUID (8 znaků)
- Teams se pamatují v paměti (RAM)
- Reset kvízu = smazání všech dat

**Pro produkci:**
- Změň heslo v `quiz_backend.py`
- Dodej SSL certifikát
- Nasaď na bezpečný server

---

## 📊 API Endpoints

### Admin
- `POST /api/admin/login` - Přihlášení
- `POST /api/admin/start-quiz` - Start kvízu
- `POST /api/admin/next-question` - Další otázka
- `POST /api/admin/end-quiz` - Konec kvízu
- `POST /api/admin/reset` - Reset
- `GET /api/admin/leaderboard` - Leaderboard
- `GET /api/admin/qr-code` - QR kód

### Team
- `POST /api/team/register` - Registrace týmu
- `GET /api/team/status` - Status kvízu
- `POST /api/team/submit-answer` - Odeslání odpovědi
- `GET /api/team/score/<team_id>` - Skóre týmu

---

## 🐛 Troubleshooting

### "Nemohu se připojit z mobilu"
- Zkontroluj, že jsi na stejné WiFi
- Zkus zadát IP adresu ručně (admin: `ipconfig`)
- Zkus port 5000 nebo 8080

### "QR kód nefunguje"
- Zkus zkopírovat odkaz ručně
- Prověř, že admin panel běží

### "Odpovědi se nezadávají"
- Zkus refresh (`F5`)
- Zkontroluj DevTools (`F12`) - Console
- Zkus se odhlásit a přihlásit znovu

---

## 🎁 Bonusy pro budoucnost

Lze snadno přidat:
- Obrázky/oaudio v otázkách
- Pamatování správných odpovědí
- Export výsledků (Excel)
- Více kol v jedné hře
- Týmové soutěže (handicap body)
- Správné odpovědi na konci

---

## 👨‍💻 Technické detaily

- **Framework:** Flask + Flask-CORS
- **Frontend:** HTML5 + CSS3 + Vanilla JS
- **QR Code:** python-qrcode
- **Storage:** In-memory (RAM)
- **Port:** 5000

---

## 📞 Autor

Vytvořeno pro rodinný quiz. ✨

Možnost úprav: Python soubor `quiz_backend.py` + HTML šablony v `templates/`

---

Ať se daří! 🎉
