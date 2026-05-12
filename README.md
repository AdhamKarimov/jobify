# Jobify — Ish Topish Platformasi

Jobify — ish beruvchilar (HR/Company) va ish qidiruvchilar (Candidate) o'rtasida bog'lovchi platforma backend tizimi. Platforma orqali kompaniyalar vakansiyalar joylaydi, foydalanuvchilar resume yaratadi, vakansiyalarga apply qiladi.

---

## Texnologiyalar

- **Python 3.13**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy** (Async)
- **JWT Authentication** (fastapi-jwt-auth2)
- **Redis** (token blacklist)
- **Docker & Docker Compose**
- **Alembic** (migrations)

---

## User Rollari

| Rol | Vazifa |
|-----|--------|
| `USER` | Ish qidiruvchi — resume yaratadi, vakansiyalarga apply qiladi |
| `COMPANY` | HR — vakansiya joylaydi, apply'larni ko'rib chiqadi |
| `ADMIN` | Platformani boshqaradi |

---

## O'rnatish

### Docker orqali (tavsiya)

```bash
git clone https://github.com/username/jobify.git
cd jobify
docker-compose up --build
```

### Qo'lda o'rnatish

```bash
# 1. Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. .env fayl yarating
DATABASE_URL=postgresql+asyncpg://postgres:123@localhost:5432/jobify
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_secret_key

# 4. Migration
alembic upgrade head

# 5. Server
uvicorn main:app --reload
```

---

## Loyiha Strukturasi

```
jobify/
├── main.py
├── db.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic/
│   ├── versions/
│   └── env.py
├── users/
│   ├── models.py
│   ├── schema.py
│   ├── views.py
│   └── utilis.py
├── vakansiya/
│   ├── models.py
│   ├── schema.py
│   └── views.py
├── resume/
│   ├── models.py
│   ├── schema.py
│   └── views.py
├── applies/
│   ├── models.py
│   ├── schema.py
│   └── router.py
├── notification/
│   ├── models.py
│   ├── schema.py
│   ├── utils.py
│   └── views.py
└── favorite/
    ├── models.py
    ├── schema.py
    └── views.py
```

---

## API Endpointlar

### Users
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| `POST` | `/users/signup` | Ro'yxatdan o'tish | Hammaga |
| `POST` | `/users/login` | Tizimga kirish | Hammaga |
| `GET` | `/users/profile` | Profilni ko'rish | Barcha rollar |
| `PUT` | `/users/update` | Profilni yangilash | Barcha rollar |
| `PUT` | `/users/password-reset` | Parolni o'zgartirish | Barcha rollar |
| `POST` | `/users/logout` | Tizimdan chiqish | Barcha rollar |

### Vacancy
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| `POST` | `/vacancy/create` | Vakansiya yaratish | COMPANY, ADMIN |
| `GET` | `/vacancy/list` | Vakansiyalar ro'yxati | Hammaga |
| `GET` | `/vacancy/my` | O'z vakansiyalari | COMPANY, ADMIN |
| `GET` | `/vacancy/detail/{id}` | Vakansiya detail | Hammaga |
| `PATCH` | `/vacancy/update/{id}` | Vakansiyani yangilash | COMPANY, ADMIN |
| `DELETE` | `/vacancy/delete/{id}` | Vakansiyani o'chirish | COMPANY, ADMIN |

### Resume
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| `POST` | `/resume/create` | Resume yaratish | USER |
| `POST` | `/resume/upload-pdf/{id}` | PDF yuklash (max 5MB) | USER |
| `GET` | `/resume/my` | O'z resumelari | USER |
| `GET` | `/resume/detail/{id}` | Resume detail | USER, COMPANY, ADMIN |
| `PATCH` | `/resume/update` | Resume yangilash | USER |
| `DELETE` | `/resume/delete/{id}` | Resume o'chirish | USER |

### Apply
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| `POST` | `/apply/create` | Vakansiyaga apply qilish | USER |
| `GET` | `/apply/my` | O'z apply'lari | USER |
| `GET` | `/apply/vacancy/{id}` | Vakansiya apply'lari | COMPANY, ADMIN |
| `PATCH` | `/apply/status/{id}` | Apply statusini yangilash | COMPANY, ADMIN |
| `DELETE` | `/apply/delete/{id}` | Apply o'chirish | USER |

### Notifications
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| `GET` | `/notifications/my_notification` | O'z notificationlari | Barcha rollar |
| `GET` | `/notifications/unread-count` | O'qilmagan soni | Barcha rollar |
| `PATCH` | `/notifications/read/{id}` | O'qilgan deb belgilash | Barcha rollar |
| `PATCH` | `/notifications/read-all` | Hammasini o'qilgan | Barcha rollar |
| `DELETE` | `/notifications/delete/{id}` | O'chirish | Barcha rollar |

### Favorites
| Method | URL | Tavsif | Ruxsat |
|--------|-----|--------|--------|
| `POST` | `/favorites/add/{id}` | Favoritega qo'shish | Barcha rollar |
| `GET` | `/favorites/my` | O'z favoritelari | Barcha rollar |
| `DELETE` | `/favorites/remove/{id}` | Favoritdan o'chirish | Barcha rollar |
| `GET` | `/favorites/check/{id}` | Favoriteda bormi | Barcha rollar |

---

## Validatsiyalar

- Candidate bir vakansiyaga **1 marta** apply qila oladi
- **Deadline** o'tgan vacancy'ga apply qilib bo'lmaydi
- Faqat **PDF** resume yuklanadi
- Max fayl hajmi: **5MB**
- **ADMIN** roli bilan ro'yxatdan o'tib bo'lmaydi
- Logout qilingan token **blacklistga** qo'shiladi

---

## Notification Tizimi

| Hodisa | Kimga xabar |
|--------|-------------|
| USER vakansiyaga apply qilganda | COMPANY ga |
| COMPANY apply statusini o'zgartganda | USER ga |

---

## Swagger Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Database Modellari

- **User** — foydalanuvchilar
- **Vakansiya** — vakansiyalar
- **Resume** — resumelar
- **Apply** — arizalar
- **Notification** — bildirishnomalar
- **Favorite** — saralangan vakansiyalar
- **CandidateProfile** — candidate profili
- **CompanyProfile** — company profili

---
## postman dokumentaatsiya

- https://documenter.getpostman.com/view/52298169/2sBXqNnyoH
