const express = require("express");
const cors = require("cors");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const app = express();
const PORT = 5000;

// =============== MIDDLEWARE ===============
app.use(cors()); // permite cereri de pe alt port (ex: React)
app.use(express.json()); // parsează JSON în body

// =============== BAZA DE DATE ===============
const dbPath = path.join(__dirname, "Bazadate.db"); // un singur fișier pt toată aplicația
const db = new sqlite3.Database(dbPath);

let dashboardData = {
    totalPeople: 0,
    todayPeople: 0,
    categories: {
        Oferte: 0,
        Facturi: 0,
        Diverse: 0
    }
};


// Creăm tabelele dacă nu există
db.serialize(() => {
    // ---- Tabela utilizatori ----
    db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      type TEXT NOT NULL
    )
  `);

    // ---- Tabela probleme ----
    db.run(`
    CREATE TABLE IF NOT EXISTS problems (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      message TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      resolved INTEGER DEFAULT 0
    )
  `);

    // ---- Seed utilizatori default ----
    const defaultUsers = [
        { username: "Functionar", password: "Parolafunctionar", type: "Functionar" },
        { username: "Dev", password: "Paroladev", type: "Developer" },
    ];

    defaultUsers.forEach((u) => {
        db.get(
            "SELECT id FROM users WHERE username = ?",
            [u.username],
            (err, row) => {
                if (err) {
                    console.error("Eroare la verificarea userului:", err);
                    return;
                }
                if (!row) {
                    db.run(
                        "INSERT INTO users (username, password, type) VALUES (?, ?, ?)",
                        [u.username, u.password, u.type],
                        (err2) => {
                            if (err2) {
                                console.error("Eroare la inserarea userului default:", err2);
                            } else {
                                console.log(`User creat: ${u.username} (${u.type})`);
                            }
                        }
                    );
                }
            }
        );
    });
});

// =============== ENDPOINT LOGIN ===============
app.post("/api/login", (req, res) => {
    const username = req.body.username || req.body.email;
    const password = req.body.password;

    if (!username || !password) {
        return res
            .status(400)
            .json({ error: "Username și parolă sunt obligatorii." });
    }

    db.get(
        "SELECT * FROM users WHERE username = ?",
        [username],
        (err, user) => {
            if (err) {
                console.error("Eroare DB la login:", err);
                return res.status(500).json({ error: "Eroare internă." });
            }

            if (!user) {
                return res.status(401).json({ error: "Credențiale invalide." });
            }

            // comparație simplă (fără hash)
            if (password !== user.password) {
                return res.status(401).json({ error: "Credențiale invalide." });
            }

            // LOGIN OK – trimitem spre frontend username + type
            return res.json({
                username: user.username,
                type: user.type,
            });
        }
    );
});

// =============== ENDPOINTURI PROBLEME ===============

// Adaugă problemă
app.post("/api/problems", (req, res) => {
    const { title, message } = req.body;

    if (!title || !message) {
        return res
            .status(400)
            .json({ error: "Titlu și mesaj sunt obligatorii." });
    }

    const stmt = db.prepare(
        "INSERT INTO problems (title, message) VALUES (?, ?)"
    );
    stmt.run(title, message, function (err) {
        if (err) {
            console.error("DB insert error:", err);
            return res
                .status(500)
                .json({ error: "Eroare la salvarea în baza de date." });
        }

        res.status(201).json({
            id: this.lastID,
            title,
            message,
        });
    });
    stmt.finalize();
});

// Listă probleme
app.get("/api/problems", (req, res) => {
    db.all("SELECT * FROM problems ORDER BY created_at DESC", [], (err, rows) => {
        if (err) {
            console.error("DB select error:", err);
            return res
                .status(500)
                .json({ error: "Eroare la citirea din baza de date." });
        }
        res.json(rows);
    });
});

// Ștergere problemă
app.delete("/api/problems/:id", (req, res) => {
    const id = req.params.id;

    db.run("DELETE FROM problems WHERE id = ?", [id], function (err) {
        if (err) {
            console.error("DB delete error:", err);
            return res.status(500).json({ error: "Eroare la ștergere." });
        }
        res.json({ success: true });
    });
});

// Rezolvare problemă
app.put("/api/problems/:id/resolve", (req, res) => {
    const id = req.params.id;

    db.run(
        "UPDATE problems SET resolved = 1 WHERE id = ?",
        [id],
        function (err) {
            if (err) {
                console.error("DB update error:", err);
                return res.status(500).json({ error: "Eroare la actualizare." });
            }
            res.json({ success: true });
        }
    );
});

// Debug users
app.get("/api/debug-users", (req, res) => {
    db.all("SELECT id, username, password, type FROM users", [], (err, rows) => {
        if (err) {
            console.error("Eroare la citirea userilor:", err);
            return res.status(500).json({ error: "Eroare DB." });
        }
        res.json(rows);
    });
});

// =============== UPDATE DASHBOARD DATA ===============
app.post("/api/dashboard", (req, res) => {
    const { totalPeople, todayPeople, categories } = req.body;

    if (!totalPeople || !todayPeople || !categories) {
        return res.status(400).json({ error: "Date incomplete pentru dashboard." });
    }

    dashboardData = {
        totalPeople,
        todayPeople,
        categories
    };

    console.log("Dashboard data actualizată:", dashboardData);

    res.json({ success: true, message: "Dashboard updated." });
});


// =============== PORNIRE SERVER ===============
app.listen(PORT, () => {
    console.log(`Server pornit pe http://localhost:${PORT}`);
});
