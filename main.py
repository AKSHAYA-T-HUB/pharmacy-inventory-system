from app import create_app, db
from app.models.user import User

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database and create an admin user."""
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Database initialized and admin user created (admin/admin123)")
    else:
        print("Database already initialized")

if __name__ == "__main__":
    app.run(debug=True)
