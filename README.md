# 🧠 MindQuest AI Assistant

> *"Level Up Your Mind, One Quest at a Time"*

Chatbot kesehatan mental berbasis RAG (Retrieval-Augmented Generation) dengan sistem gamifikasi.

---

## 🚀 Instalasi & Menjalankan

### 1. Install dependencies

```bash
# Minimal (fallback keyword search)
pip install anthropic colorama

# Opsional — untuk embedding RAG sesungguhnya
pip install chromadb sentence-transformers
```

### 2. Set API Key (opsional tapi disarankan)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Tanpa API key, chatbot tetap berjalan dengan **keyword-based fallback**.

### 3. Jalankan

```bash
python mindquest_chatbot.py
```

---

## 💬 Perintah Chat

| Perintah    | Fungsi                              |
|-------------|-------------------------------------|
| `/status`   | Lihat level, EXP, dan badge kamu    |
| `/quest`    | Tampilkan & selesaikan daily quest  |
| `/badges`   | Lihat semua achievement             |
| `/help`     | Contoh pertanyaan                   |
| `/exit`     | Keluar                              |

---

## 🎮 Fitur Gamifikasi

### Level System
| Level | Nama        | EXP Dibutuhkan |
|-------|-------------|----------------|
| 1     | 🌱 Beginner  | 0              |
| 2     | 🔍 Explorer  | 50             |
| 3     | ⭐ Achiever  | 150            |
| 4     | 🛡️ Guardian | 300            |
| 5     | 👑 Mind Master | 500          |

### Daily Quests
- 🧘 Meditasi 5 Menit (+10 EXP)
- 📓 Tulis Jurnal Syukur (+10 EXP)
- 🚶 Jalan Kaki 15 Menit (+15 EXP)
- 💧 Minum Air 8 Gelas (+10 EXP)
- 😴 Tidur Sebelum Jam 11 Malam (+20 EXP)

### Achievement Badges
- 🎯 First Step — Pertama kali chat
- 🔥 3-Day Streak — Chat 3 hari berturut-turut
- 💎 7-Day Streak — Chat 7 hari berturut-turut
- 🏹 Quest Hunter — Selesaikan 5 daily quest
- 🎯 Focus Champion — Tanya tentang fokus & produktivitas
- 🙏 Gratitude Hero — Lakukan quest jurnal syukur
- ⚡ Stress Slayer — Tanya tentang cara mengatasi stres
- 👑 Mind Master — Capai Level 5

---

## 🗂️ Topik Knowledge Base

- Burnout (tanda-tanda, cara mengatasi)
- Stres vs Depresi
- Kecemasan & presentasi
- Overthinking
- Fokus & produktivitas belajar
- Manajemen waktu kuliah + organisasi
- Mindfulness
- Self-care & kebiasaan sehat
- Mood booster
- Stres akademik
- Coping mechanism

---

## 🔧 Arsitektur

```
User Input
    ↓
Retrieval Engine (ChromaDB / Keyword Search)
    ↓
Retrieved Context (top-3 dokumen relevan)
    ↓
LLM (Claude / Fallback)  ← System Prompt + Guardrails
    ↓
Response + Citation + EXP + Badge Check
    ↓
User Profile (disimpan ke mindquest_profile.json)
```

---

## ⚠️ Disclaimer

MindQuest AI Assistant adalah alat edukasi, **bukan pengganti psikolog atau dokter**.
Untuk masalah kesehatan mental yang serius, hubungi profesional.

**Hotline Kesehatan Mental Indonesia:**
- Into The Light: 119 ext 8
- Yayasan Pulih: (021) 788-42580
