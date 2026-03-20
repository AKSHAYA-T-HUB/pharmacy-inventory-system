import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.medicine import Medicine
from app.models.stock import Stock
from app.models.sale import Sale

app = create_app()

med_names = [
    "Paracetamol", "Amoxicillin", "Ciprofloxacin", "Metformin", "Amlodipine", 
    "Atorvastatin", "Omeprazole", "Lisinopril", "Azithromycin", "Gabapentin",
    "Losartan", "Albuterol", "Sertraline", "Simvastatin", "Levothyroxine",
    "Hydrochlorothiazide", "Furosemide", "Cetirizine", "Ibuprofen", "Aspirin",
    "Clopidogrel", "Pantoprazole", "Montelukast", "Rosuvastatin", "Escitalopram",
    "Duloxetine", "Venlafaxine", "Bupropion", "Tamsulosin", "Finasteride"
]

suffixes = ["500mg", "250mg", "100mg", "10mg", "5mg", "XL", "DS", "Forte", "Plus", "Retard"]
categories = ["Analgesic", "Antibiotic", "Antidiabetic", "Cardiovascular", "Gastrointestinal", "Respiratory", "Neurological"]

def seed_data():
    with app.app_context():
        print("Cleaning existing data (optional)...")
        # Keep admin user, but we can clear medicines to have exactly 1000 new ones
        # Sale.query.delete()
        # Stock.query.delete()
        # Medicine.query.delete()
        
        print("Generating 1000 medicines...")
        for i in range(1000):
            base_name = random.choice(med_names)
            suffix = random.choice(suffixes)
            name = f"{base_name} {suffix} #{i+1}"
            category = random.choice(categories)
            
            # Random expiry date between 1 month and 2 years from now
            days_to_expiry = random.randint(30, 730)
            expiry_date = datetime.utcnow().date() + timedelta(days=days_to_expiry)
            
            price = round(random.uniform(5.0, 150.0), 2)
            
            med = Medicine(
                name=name,
                category=category,
                expiry_date=expiry_date,
                price=price
            )
            db.session.add(med)
            
            # Commit every 100 to avoid memory issues and see progress
            if i % 100 == 0:
                db.session.commit()
                print(f"Added {i} medicines...")

        db.session.commit()
        print("1000 Medicines added. Now adding stock and sales...")
        
        all_meds = Medicine.query.order_by(Medicine.id.desc()).limit(1000).all()
        
        for med in all_meds:
            # Random stock level
            quantity = random.randint(5, 200)
            stock = Stock(
                medicine_id=med.id,
                quantity=quantity,
                last_updated=datetime.utcnow().date()
            )
            db.session.add(stock)
            
            # Random sales for some medicines
            if random.random() > 0.3: # 70% chance to have sales
                num_sales = random.randint(1, 5)
                for _ in range(num_sales):
                    sale_qty = random.randint(1, 10)
                    sale = Sale(
                        medicine_id=med.id,
                        quantity=sale_qty,
                        sale_date=datetime.utcnow().date() - timedelta(days=random.randint(0, 30))
                    )
                    db.session.add(sale)
        
        db.session.commit()
        print("Data Seeding Completed Successfully!")

if __name__ == "__main__":
    seed_data()
