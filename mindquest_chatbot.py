"""
╔══════════════════════════════════════════════════════════╗
║         MINDQUEST AI ASSISTANT — Mini RAG Demo           ║
║     "Level Up Your Mind, One Quest at a Time"            ║
╚══════════════════════════════════════════════════════════╝

Sistem chatbot kesehatan mental berbasis RAG (Retrieval-Augmented Generation)
dengan fitur gamifikasi: EXP, Level, Daily Quest, dan Achievement Badge.

Requirements:
    pip install anthropic chromadb sentence-transformers colorama

Cara Penggunaan:
    python mindquest_chatbot.py
"""

import os
import json
import random
import hashlib
from datetime import date, datetime
from typing import Optional

# ─── Dependencies dengan fallback graceful ───────────────────────────────────
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    C = {
        "title":   Fore.CYAN + Style.BRIGHT,
        "user":    Fore.GREEN,
        "bot":     Fore.YELLOW,
        "source":  Fore.BLUE,
        "quest":   Fore.MAGENTA,
        "level":   Fore.CYAN,
        "warn":    Fore.RED,
        "reset":   Style.RESET_ALL,
    }
except ImportError:
    C = {k: "" for k in ["title","user","bot","source","quest","level","warn","reset"]}


# ═══════════════════════════════════════════════════════════════════════════════
# 1. KNOWLEDGE BASE — dokumen kesehatan mental
# ═══════════════════════════════════════════════════════════════════════════════

KNOWLEDGE_BASE = [
    # ── Burnout ────────────────────────────────────────────────────────────────
    {
        "id": "kb_001",
        "text": (
            "Burnout adalah sindrom yang dihasilkan dari stres kronis di tempat kerja "
            "atau aktivitas yang tidak berhasil dikelola dengan baik. Gejalanya meliputi: "
            "kelelahan emosional, kehilangan motivasi, penurunan produktivitas, dan sulit "
            "berkonsentrasi. Burnout berbeda dari stres biasa karena bersifat jangka panjang "
            "dan memengaruhi seluruh aspek kehidupan seseorang."
        ),
        "source": "WHO Mental Health Resources",
        "topic": "burnout",
        "category": "Edukasi",
    },
    {
        "id": "kb_002",
        "text": (
            "Cara mengatasi burnout: (1) Istirahat yang cukup dan tidur 7–9 jam per malam. "
            "(2) Tetapkan batasan antara pekerjaan dan waktu pribadi. (3) Lakukan aktivitas "
            "menyenangkan di luar rutinitas. (4) Bicarakan perasaan dengan orang terpercaya. "
            "(5) Pertimbangkan konsultasi dengan profesional kesehatan mental bila diperlukan."
        ),
        "source": "WHO Mental Health Action Plan",
        "topic": "burnout",
        "category": "Self-Care",
    },
    # ── Stres & Kecemasan ──────────────────────────────────────────────────────
    {
        "id": "kb_003",
        "text": (
            "Stres adalah respons tubuh terhadap tekanan atau tuntutan tertentu, dan "
            "umumnya bersifat sementara. Depresi adalah gangguan suasana hati (mood disorder) "
            "yang berlangsung lebih dari 2 minggu, ditandai rasa sedih mendalam, kehilangan "
            "minat, dan energi rendah. Stres dapat memicu depresi jika tidak ditangani, tetapi "
            "keduanya memerlukan penanganan yang berbeda."
        ),
        "source": "Modul Psikologi Dasar",
        "topic": "stres, depresi",
        "category": "Edukasi",
    },
    {
        "id": "kb_004",
        "text": (
            "Kecemasan sebelum presentasi adalah hal yang normal. Strategi mengatasinya: "
            "(1) Persiapkan materi dengan matang. (2) Latihan pernapasan dalam (tarik napas "
            "4 detik, tahan 4 detik, buang 4 detik). (3) Visualisasikan keberhasilan. "
            "(4) Ingat bahwa audiens ingin kamu berhasil, bukan menghakimi."
        ),
        "source": "Mental Health Foundation Resources",
        "topic": "kecemasan, presentasi",
        "category": "Self-Care",
    },
    # ── Overthinking ──────────────────────────────────────────────────────────
    {
        "id": "kb_005",
        "text": (
            "Overthinking atau berpikir berlebihan dapat diatasi dengan: (1) Tuliskan "
            "pikiranmu di jurnal untuk 'mengeluarkan' beban mental. (2) Tetapkan waktu "
            "khusus untuk memikirkan masalah, bukan sepanjang hari. (3) Fokus pada hal "
            "yang bisa dikontrol. (4) Praktikkan mindfulness — sadari pikiran tanpa menghakimi. "
            "(5) Alihkan perhatian dengan aktivitas fisik atau hobi."
        ),
        "source": "Buku Self Improvement",
        "topic": "overthinking",
        "category": "Self-Care",
    },
    # ── Produktivitas ─────────────────────────────────────────────────────────
    {
        "id": "kb_006",
        "text": (
            "Tips meningkatkan fokus belajar: (1) Gunakan teknik Pomodoro (25 menit fokus, "
            "5 menit istirahat). (2) Singkirkan distraksi — matikan notifikasi HP. "
            "(3) Buat daftar prioritas tugas harian. (4) Belajar di lingkungan bersih dan "
            "tenang. (5) Cukup tidur karena kurang tidur drastis menurunkan konsentrasi."
        ),
        "source": "Buku Self Improvement",
        "topic": "fokus, produktivitas",
        "category": "Produktivitas",
    },
    {
        "id": "kb_007",
        "text": (
            "Manajemen waktu antara kuliah dan organisasi: (1) Buat jadwal mingguan yang "
            "realistis. (2) Prioritaskan tugas dengan matriks Eisenhower (penting vs mendesak). "
            "(3) Belajar mengatakan 'tidak' pada komitmen berlebihan. (4) Manfaatkan waktu "
            "tunggu (perjalanan, antrian) untuk hal produktif kecil."
        ),
        "source": "Buku Self Improvement",
        "topic": "manajemen waktu, kuliah",
        "category": "Produktivitas",
    },
    # ── Self-Care & Mindfulness ───────────────────────────────────────────────
    {
        "id": "kb_008",
        "text": (
            "Mindfulness adalah praktik memusatkan perhatian pada momen saat ini secara "
            "sadar dan tanpa menghakimi. Manfaatnya: mengurangi stres dan kecemasan, "
            "meningkatkan konsentrasi, membantu regulasi emosi, serta meningkatkan kualitas "
            "tidur. Cukup 5–10 menit per hari sudah memberikan manfaat yang terukur."
        ),
        "source": "Mental Health Foundation Resources",
        "topic": "mindfulness",
        "category": "Self-Care",
    },
    {
        "id": "kb_009",
        "text": (
            "Kebiasaan kecil untuk kesehatan mental: (1) Tidur dan bangun di jam yang sama "
            "setiap hari. (2) Olahraga ringan 30 menit (jalan kaki sudah cukup). "
            "(3) Kurangi scrolling media sosial sebelum tidur. (4) Luangkan waktu untuk "
            "bersyukur — tulis 3 hal positif setiap pagi. (5) Jaga koneksi sosial dengan "
            "keluarga atau sahabat."
        ),
        "source": "Mental Health Foundation Resources",
        "topic": "self-care, kebiasaan sehat",
        "category": "Self-Care",
    },
    {
        "id": "kb_010",
        "text": (
            "Aktivitas yang dapat memperbaiki mood: olahraga (melepas endorfin), "
            "mendengarkan musik favorit, menghabiskan waktu di alam, melukis atau menulis "
            "kreatif, memasak makanan baru, menghubungi teman lama, dan tertawa bersama "
            "orang-orang terkasih. Pilihlah aktivitas yang benar-benar kamu nikmati."
        ),
        "source": "Buku Self Improvement",
        "topic": "mood, aktivitas positif",
        "category": "Self-Care",
    },
    # ── Stress Akademik ───────────────────────────────────────────────────────
    {
        "id": "kb_011",
        "text": (
            "Saat tugas kuliah menumpuk, langkah yang dapat dilakukan: (1) Buat daftar "
            "semua tugas dan urutkan berdasarkan deadline. (2) Kerjakan satu tugas per "
            "sesi, jangan multitasking. (3) Pecah tugas besar menjadi langkah-langkah kecil. "
            "(4) Minta bantuan teman atau dosen jika mengalami kesulitan. "
            "(5) Ingat untuk istirahat — otak yang lelah tidak produktif."
        ),
        "source": "Modul Psikologi Dasar",
        "topic": "stres akademik, tugas kuliah",
        "category": "Produktivitas",
    },
    # ── Coping Mechanism ─────────────────────────────────────────────────────
    {
        "id": "kb_012",
        "text": (
            "Coping mechanism yang sehat meliputi: problem-focused coping (menyelesaikan "
            "masalah secara langsung) dan emotion-focused coping (mengelola emosi terkait "
            "masalah). Hindari maladaptive coping seperti penyalahgunaan zat, isolasi diri "
            "berlebihan, atau menghindari masalah. Berbicara dengan orang terpercaya adalah "
            "salah satu coping mechanism paling efektif."
        ),
        "source": "Modul Psikologi Dasar",
        "topic": "coping mechanism",
        "category": "Edukasi",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# 2. SISTEM GAMIFIKASI
# ═══════════════════════════════════════════════════════════════════════════════

LEVEL_SYSTEM = [
    {"level": 1, "name": "Beginner",   "min_exp": 0,   "icon": "🌱"},
    {"level": 2, "name": "Explorer",   "min_exp": 50,  "icon": "🔍"},
    {"level": 3, "name": "Achiever",   "min_exp": 150, "icon": "⭐"},
    {"level": 4, "name": "Guardian",   "min_exp": 300, "icon": "🛡️"},
    {"level": 5, "name": "Mind Master","min_exp": 500, "icon": "👑"},
]

DAILY_QUESTS = [
    {"id": "q1", "name": "Meditasi 5 Menit",         "exp": 10, "icon": "🧘"},
    {"id": "q2", "name": "Tulis Jurnal Syukur",       "exp": 10, "icon": "📓"},
    {"id": "q3", "name": "Jalan Kaki 15 Menit",       "exp": 15, "icon": "🚶"},
    {"id": "q4", "name": "Minum Air 8 Gelas",         "exp": 10, "icon": "💧"},
    {"id": "q5", "name": "Tidur Sebelum Jam 11 Malam","exp": 20, "icon": "😴"},
    {"id": "q6", "name": "Baca Buku 15 Menit",        "exp": 15, "icon": "📚"},
    {"id": "q7", "name": "Hubungi Satu Teman Lama",   "exp": 20, "icon": "📱"},
]

ACHIEVEMENTS = {
    "first_chat":     {"name": "First Step",      "icon": "🎯", "desc": "Pertama kali chat dengan MindQuest"},
    "streak_3":       {"name": "3-Day Streak",    "icon": "🔥", "desc": "Chat 3 hari berturut-turut"},
    "streak_7":       {"name": "7-Day Streak",    "icon": "💎", "desc": "Chat 7 hari berturut-turut"},
    "quest_5":        {"name": "Quest Hunter",    "icon": "🏹", "desc": "Selesaikan 5 daily quest"},
    "focus":          {"name": "Focus Champion",  "icon": "🎯", "desc": "Tanya tentang fokus & produktivitas"},
    "gratitude":      {"name": "Gratitude Hero",  "icon": "🙏", "desc": "Lakukan quest jurnal syukur"},
    "stress_slayer":  {"name": "Stress Slayer",   "icon": "⚡", "desc": "Tanya tentang cara mengatasi stres"},
    "mind_master":    {"name": "Mind Master",     "icon": "👑", "desc": "Capai Level 5"},
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PROFIL PENGGUNA
# ═══════════════════════════════════════════════════════════════════════════════

class UserProfile:
    SAVE_FILE = "mindquest_profile.json"

    def __init__(self, name: str = "Pengguna"):
        self.name = name
        self.exp = 0
        self.completed_quests: list[str] = []
        self.badges: list[str] = []
        self.chat_dates: list[str] = []
        self.total_chats = 0
        self._load()

    # ── persistence ──────────────────────────────────────────────────────────

    def _load(self):
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE) as f:
                    data = json.load(f)
                self.__dict__.update(data)
            except Exception:
                pass  # file rusak → mulai dari awal

    def save(self):
        with open(self.SAVE_FILE, "w") as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=2)

    # ── level & exp ──────────────────────────────────────────────────────────

    def get_level(self) -> dict:
        current = LEVEL_SYSTEM[0]
        for lvl in LEVEL_SYSTEM:
            if self.exp >= lvl["min_exp"]:
                current = lvl
        return current

    def get_next_level(self) -> Optional[dict]:
        lvl = self.get_level()
        idx = LEVEL_SYSTEM.index(lvl)
        return LEVEL_SYSTEM[idx + 1] if idx + 1 < len(LEVEL_SYSTEM) else None

    def add_exp(self, amount: int) -> tuple[int, bool]:
        """Tambah EXP; kembalikan (jumlah_ditambah, level_naik)."""
        old_level = self.get_level()["level"]
        self.exp += amount
        new_level = self.get_level()["level"]
        leveled_up = new_level > old_level
        if leveled_up and new_level == 5:
            self.unlock_badge("mind_master")
        return amount, leveled_up

    # ── badge ─────────────────────────────────────────────────────────────────

    def unlock_badge(self, badge_id: str) -> bool:
        if badge_id in ACHIEVEMENTS and badge_id not in self.badges:
            self.badges.append(badge_id)
            return True
        return False

    # ── quest ─────────────────────────────────────────────────────────────────

    def complete_quest(self, quest_id: str) -> tuple[int, list[str]]:
        """Selesaikan quest; kembalikan (exp_gained, new_badges)."""
        quest = next((q for q in DAILY_QUESTS if q["id"] == quest_id), None)
        if not quest or quest_id in self.completed_quests:
            return 0, []

        self.completed_quests.append(quest_id)
        gained, _ = self.add_exp(quest["exp"])
        new_badges = []

        if quest_id == "q2":  # jurnal syukur
            if self.unlock_badge("gratitude"):
                new_badges.append("gratitude")

        total_done = len(self.completed_quests)
        if total_done >= 5 and self.unlock_badge("quest_5"):
            new_badges.append("quest_5")

        return gained, new_badges

    # ── streak ───────────────────────────────────────────────────────────────

    def record_chat(self) -> int:
        today = date.today().isoformat()
        if today not in self.chat_dates:
            self.chat_dates.append(today)
        self.total_chats += 1

        # hitung streak hari berturut-turut
        streak = 1
        for i in range(len(self.chat_dates) - 1, 0, -1):
            d1 = date.fromisoformat(self.chat_dates[i])
            d0 = date.fromisoformat(self.chat_dates[i - 1])
            if (d1 - d0).days == 1:
                streak += 1
            else:
                break

        if streak >= 3:
            self.unlock_badge("streak_3")
        if streak >= 7:
            self.unlock_badge("streak_7")
        return streak

    # ── tampilan status ───────────────────────────────────────────────────────

    def status_string(self) -> str:
        lvl = self.get_level()
        nxt = self.get_next_level()
        bar_fill = min(int((self.exp - lvl["min_exp"]) / max((nxt["min_exp"] - lvl["min_exp"]) if nxt else 1, 1) * 10), 10)
        bar = "█" * bar_fill + "░" * (10 - bar_fill)
        exp_info = f"{self.exp} EXP" + (f" / {nxt['min_exp']} untuk {nxt['name']}" if nxt else " (MAX)")
        badges_str = " ".join(ACHIEVEMENTS[b]["icon"] for b in self.badges) or "—"
        return (
            f"👤 {self.name}  |  {lvl['icon']} Lv.{lvl['level']} {lvl['name']}\n"
            f"[{bar}] {exp_info}\n"
            f"🏅 Badge: {badges_str}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. RETRIEVAL ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class RetrievalEngine:
    """
    Retrieval sederhana menggunakan keyword overlap (TF-like scoring).
    Jika ChromaDB + sentence-transformers tersedia, akan digunakan embedding.
    """

    def __init__(self):
        self.use_chroma = CHROMA_AVAILABLE
        if self.use_chroma:
            try:
                self._init_chroma()
            except Exception as e:
                print(f"[Chroma init gagal, pakai keyword search: {e}]")
                self.use_chroma = False

    def _init_chroma(self):
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        client = chromadb.Client()
        self.collection = client.get_or_create_collection(
            name="mindquest_kb", embedding_function=ef
        )
        if self.collection.count() == 0:
            self.collection.add(
                ids=[doc["id"] for doc in KNOWLEDGE_BASE],
                documents=[doc["text"] for doc in KNOWLEDGE_BASE],
                metadatas=[
                    {"source": d["source"], "topic": d["topic"], "category": d["category"]}
                    for d in KNOWLEDGE_BASE
                ],
            )

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        if self.use_chroma:
            results = self.collection.query(query_texts=[query], n_results=top_k)
            docs = []
            for i, doc_text in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                docs.append({"text": doc_text, "source": meta["source"],
                              "topic": meta["topic"], "score": 1.0 - results["distances"][0][i]})
            return docs
        return self._keyword_retrieve(query, top_k)

    def _keyword_retrieve(self, query: str, top_k: int) -> list[dict]:
        query_words = set(query.lower().split())
        scored = []
        for doc in KNOWLEDGE_BASE:
            doc_words = set((doc["text"] + " " + doc["topic"]).lower().split())
            overlap = len(query_words & doc_words)
            # bonus jika kata kunci utama cocok
            key_terms = {"burnout", "stres", "cemas", "overthinking", "fokus",
                         "mindfulness", "depresi", "produktivitas", "self-care",
                         "tidur", "mood", "motivasi"}
            bonus = sum(2 for w in query_words if w in key_terms and w in doc_words)
            scored.append((overlap + bonus, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scored[:top_k]:
            if score > 0:
                results.append({"text": doc["text"], "source": doc["source"],
                                 "topic": doc["topic"], "score": score})
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CHATBOT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Kamu adalah MindQuest AI Assistant — asisten kesehatan mental yang ramah, empatik, dan berpengetahuan.

PERANMU:
- Memberikan edukasi kesehatan mental yang akurat dan mudah dipahami
- Merekomendasikan strategi self-care dan coping yang praktis
- Memberikan motivasi dan dukungan emosional
- Memandu pengguna menuju kebiasaan positif

GUARDRAILS (WAJIB DIIKUTI):
1. JANGAN memberikan diagnosis psikologis atau medis
2. SELALU sertakan disclaimer bahwa kamu bukan psikolog/dokter
3. Jika masalah serius (bunuh diri, krisis berat), ARAHKAN ke profesional / hotline kesehatan mental
4. Gunakan HANYA informasi dari context yang diberikan
5. Jika tidak ada context relevan, katakan dengan jujur

GAYA BAHASA:
- Hangat, suportif, tidak menghakimi
- Bahasa Indonesia yang natural dan mudah dipahami
- Gunakan sapaan "kamu" (bukan "Anda") agar terasa lebih akrab
- Boleh gunakan emoji secukupnya untuk keramahan

FORMAT JAWABAN:
- Mulai dengan empati jika pertanyaan bersifat personal
- Jawaban terstruktur dengan poin-poin jika memungkinkan
- Akhiri dengan satu kalimat penyemangat

DISCLAIMER: Selalu tutup jawaban dengan: "💡 *Catatan: Saya adalah AI, bukan psikolog. Untuk masalah serius, konsultasikan dengan profesional kesehatan mental.*"
"""

class MindQuestChatbot:
    def __init__(self, user: UserProfile):
        self.user = user
        self.retrieval = RetrievalEngine()
        self.history: list[dict] = []
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "")) if ANTHROPIC_AVAILABLE else None

    def _build_context(self, retrieved_docs: list[dict]) -> str:
        if not retrieved_docs:
            return "Tidak ada dokumen relevan ditemukan untuk pertanyaan ini."
        parts = ["=== RETRIEVED CONTEXT ==="]
        for i, doc in enumerate(retrieved_docs, 1):
            parts.append(f"[Dokumen {i}] Sumber: {doc['source']}\n{doc['text']}")
        parts.append("=========================")
        return "\n\n".join(parts)

    def _check_topic_badges(self, query: str):
        q = query.lower()
        if any(w in q for w in ["fokus", "produktif", "konsentrasi", "belajar"]):
            if self.user.unlock_badge("focus"):
                print(f"\n{C['quest']}🏅 Achievement Unlocked: Focus Champion! 🎯{C['reset']}")
        if any(w in q for w in ["stres", "stress", "cemas", "burnout", "overthinking"]):
            if self.user.unlock_badge("stress_slayer"):
                print(f"\n{C['quest']}🏅 Achievement Unlocked: Stress Slayer! ⚡{C['reset']}")

    def chat(self, user_message: str) -> str:
        # Rekam aktivitas & badge first_chat
        self.user.record_chat()
        if self.user.unlock_badge("first_chat"):
            print(f"\n{C['quest']}🏅 Achievement Unlocked: First Step! 🎯{C['reset']}")

        self._check_topic_badges(user_message)

        # Ambil context dari knowledge base
        retrieved = self.retrieval.retrieve(user_message, top_k=3)
        context = self._build_context(retrieved)

        # Tambah EXP untuk setiap chat
        exp_gained, leveled_up = self.user.add_exp(5)

        # Bangun pesan untuk LLM
        full_user_msg = f"{context}\n\nPertanyaan pengguna: {user_message}"
        self.history.append({"role": "user", "content": full_user_msg})

        # Generate respons
        if self.client and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                resp = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    messages=self.history,
                )
                answer = resp.content[0].text
            except Exception as e:
                answer = self._fallback_response(user_message, retrieved)
        else:
            answer = self._fallback_response(user_message, retrieved)

        self.history.append({"role": "assistant", "content": answer})

        # Tampilkan status EXP
        print(f"\n{C['quest']}+{exp_gained} EXP  |  Total: {self.user.exp} EXP{C['reset']}", end="")
        if leveled_up:
            lvl = self.user.get_level()
            print(f"  🎉 LEVEL UP! → Lv.{lvl['level']} {lvl['icon']} {lvl['name']}", end="")
        print()

        # Tampilkan sumber dokumen
        if retrieved:
            sources = list(dict.fromkeys(d["source"] for d in retrieved))
            print(f"{C['source']}📚 Sumber: {' | '.join(sources)}{C['reset']}")

        self.user.save()
        return answer

    def _fallback_response(self, query: str, docs: list[dict]) -> str:
        """Jawaban fallback ketika API tidak tersedia."""
        q = query.lower()
        if not docs:
            return (
                "Maaf, saya tidak menemukan informasi yang relevan untuk pertanyaan itu "
                "di knowledge base saya. Coba tanyakan seputar: burnout, stres, kecemasan, "
                "overthinking, fokus belajar, mindfulness, atau self-care.\n\n"
                "💡 *Catatan: Saya adalah AI, bukan psikolog. Untuk masalah serius, "
                "konsultasikan dengan profesional kesehatan mental.*"
            )

        best = docs[0]
        response = f"Berdasarkan sumber terpercaya, berikut informasi untuk kamu:\n\n{best['text']}"

        if len(docs) > 1:
            response += f"\n\n{docs[1]['text']}"

        response += (
            "\n\nSemangat terus, ya! Kamu sudah melakukan langkah yang tepat dengan mencari informasi. 💪\n\n"
            "💡 *Catatan: Saya adalah AI, bukan psikolog. Untuk masalah serius, "
            "konsultasikan dengan profesional kesehatan mental.*"
        )
        return response


# ═══════════════════════════════════════════════════════════════════════════════
# 6. INTERFACE CLI
# ═══════════════════════════════════════════════════════════════════════════════

def print_banner():
    print(f"""{C['title']}
╔══════════════════════════════════════════════════════════════╗
║          MINDQUEST AI ASSISTANT  🧠✨                        ║
║      "Level Up Your Mind, One Quest at a Time"               ║
╠══════════════════════════════════════════════════════════════╣
║  /status    — lihat profil & level kamu                      ║
║  /quest     — tampilkan & selesaikan daily quest             ║
║  /badges    — lihat achievement badge                        ║
║  /help      — contoh pertanyaan                              ║
║  /exit      — keluar                                         ║
╚══════════════════════════════════════════════════════════════╝{C['reset']}""")

def show_quests(user: UserProfile):
    print(f"\n{C['quest']}📋 DAILY QUESTS{C['reset']}")
    available = [q for q in DAILY_QUESTS if q["id"] not in user.completed_quests]
    if not available:
        print("  ✅ Semua quest hari ini sudah selesai! Luar biasa!")
        return

    for i, q in enumerate(available, 1):
        print(f"  {i}. {q['icon']} {q['name']}  (+{q['exp']} EXP)  [{q['id']}]")

    choice = input("\nMasukkan ID quest yang ingin diselesaikan (atau Enter untuk skip): ").strip()
    if choice:
        exp_gained, new_badges = user.complete_quest(choice)
        if exp_gained:
            q_name = next((q["name"] for q in DAILY_QUESTS if q["id"] == choice), choice)
            print(f"{C['quest']}✅ Quest selesai: {q_name} | +{exp_gained} EXP{C['reset']}")
            for badge_id in new_badges:
                b = ACHIEVEMENTS[badge_id]
                print(f"{C['quest']}🏅 Achievement Unlocked: {b['name']} {b['icon']}{C['reset']}")
        else:
            print("Quest tidak ditemukan atau sudah diselesaikan.")
        user.save()

def show_badges(user: UserProfile):
    print(f"\n{C['level']}🏅 ACHIEVEMENT BADGES{C['reset']}")
    for bid, badge in ACHIEVEMENTS.items():
        status = badge["icon"] if bid in user.badges else "🔒"
        locked  = "" if bid in user.badges else " (Belum)"
        print(f"  {status} {badge['name']}{locked} — {badge['desc']}")

def show_help():
    print(f"""
{C['title']}💡 CONTOH PERTANYAAN:{C['reset']}
  • Apa itu burnout dan bagaimana tandanya?
  • Apa perbedaan stres dan depresi?
  • Bagaimana cara mengatasi overthinking?
  • Saya cemas menghadapi presentasi besok
  • Saya stres karena tugas kuliah menumpuk
  • Bagaimana cara meningkatkan fokus belajar?
  • Apa manfaat mindfulness?
  • Aktivitas apa yang bisa memperbaiki mood?
  • Kebiasaan kecil apa yang baik untuk kesehatan mental?
""")

def run():
    print_banner()

    # Setup awal
    save_exists = os.path.exists(UserProfile.SAVE_FILE)
    if save_exists:
        user = UserProfile()
        print(f"\nSelamat datang kembali, {C['user']}{user.name}{C['reset']}! 👋")
    else:
        name = input("\nHai! Siapa namamu? ").strip() or "Pengguna"
        user = UserProfile(name)
        user.save()
        print(f"\nSenang bertemu denganmu, {C['user']}{name}{C['reset']}! 🌟")

    print(f"\n{user.status_string()}\n")

    # Cek API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{C['warn']}⚠  ANTHROPIC_API_KEY tidak ditemukan — berjalan dalam mode fallback (keyword-based){C['reset']}")
        print(f"   Set API key: export ANTHROPIC_API_KEY='sk-ant-...'\n")

    bot = MindQuestChatbot(user)

    while True:
        try:
            user_input = input(f"\n{C['user']}Kamu:{C['reset']} ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSampai jumpa! Jaga kesehatan mentalmu ya 💙")
            user.save()
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("/exit", "/quit", "keluar"):
            print("Sampai jumpa! Jaga kesehatan mentalmu ya 💙")
            user.save()
            break
        elif cmd == "/status":
            print(f"\n{user.status_string()}")
            nxt = user.get_next_level()
            if nxt:
                needed = nxt["min_exp"] - user.exp
                print(f"   → Butuh {needed} EXP lagi untuk level berikutnya!")
        elif cmd == "/quest":
            show_quests(user)
        elif cmd == "/badges":
            show_badges(user)
        elif cmd == "/help":
            show_help()
        else:
            # Chat normal
            print(f"\n{C['bot']}MindQuest:{C['reset']} ", end="", flush=True)
            response = bot.chat(user_input)
            print(response)


if __name__ == "__main__":
    run()
