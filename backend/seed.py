from app.db import get_db

LOCATIONS = [
    "Mahachakri Sirindhorn Building",
    "Maha Vajiravudh Building",
    "Boromratchakumari Building",
    "Chamchuri 5",
    "Chamchuri 9",
    "Chaloem Rajakumari 60 Building",
    "Mahitaladhibesra Building",
    "Office of Academic Resources (Central Library)",
    "Faculty of Commerce & Accountancy",
    "Faculty of Engineering",
    "Faculty of Science",
    "Faculty of Arts",
    "Faculty of Law",
    "Faculty of Medicine",
    "Sala Phra Kiao",
    "MBK Center",
    "Siam Square",
    "CU Sports Complex",
    "Cafeteria (Sasa Patasala)",
    "CU Dorm",
]

ADMINS = [
    {
        "email": "library.admin@chula.ac.th",
        "role": "location_admin",
        "admin_location_name": "Office of Academic Resources (Central Library)",
    },
    {
        "email": "eng.admin@chula.ac.th",
        "role": "location_admin",
        "admin_location_name": "Faculty of Engineering",
    },
    {
        "email": "web.admin@chula.ac.th",
        "role": "web_admin",
        "admin_location_name": None,
    },
]


def seed_locations(db):
    for name in LOCATIONS:
        db.locations.update_one(
            {"name": name},
            {"$setOnInsert": {"name": name, "is_active": True}},
            upsert=True,
        )
    print(f"Seeded {len(LOCATIONS)} locations")


def seed_admins(db):
    for admin in ADMINS:
        db.users.update_one(
            {"email": admin["email"]},
            {"$setOnInsert": admin},
            upsert=True,
        )
    print(f"Seeded {len(ADMINS)} admins")


if __name__ == "__main__":
    db = get_db()
    seed_locations(db)
    seed_admins(db)
    print("Done")