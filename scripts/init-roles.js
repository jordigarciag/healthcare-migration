db = db.getSiblingDB('healthcare_db');
print("🔐 Création des rôles et utilisateurs...");
// Utilisateur Médecin (lecture + écriture)
db.createUser({
  user: "medecin_user",
  pwd: "medecin123",
  roles: [
    { role: "readWrite", db: "healthcare_db" }
  ]
});
print("✅ Utilisateur \"medecin_user\" créé avec permissions lecture/écriture");
// Utilisateur Infirmière (lecture seule)
db.createUser({
  user: "infirmiere_user",
  pwd: "infirmiere123",
  roles: [
    { role: "read", db: "healthcare_db" }
  ]
});
print("✅ Utilisateur \"infirmiere_user\" créé avec permissions lecture seule");
print("🎉 Initialisation des rôles terminée !");