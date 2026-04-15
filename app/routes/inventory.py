from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.inventory_service import InventoryService

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/medicines')
@login_required
def list_medicines():
    medicines = InventoryService.get_all_medicines()
    return render_template('medicines.html', medicines=medicines)

@inventory_bp.route('/add-medicine', methods=['GET', 'POST'])
@login_required
def add_medicine():
    if request.method == 'POST':
        try:
            InventoryService.add_medicine(
                request.form['name'],
                request.form['category'],
                request.form['expiry_date'],
                request.form['price']
            )
            flash('Medicine added successfully', 'success')
            return redirect(url_for('inventory.list_medicines'))
        except Exception as e:
            flash(f'Error adding medicine: {str(e)}', 'danger')
            
    return render_template('add_medicine.html')

@inventory_bp.route('/stock')
@login_required
def view_stock():
    stock_data = InventoryService.get_stock_data()
    return render_template('stock.html', stock_data=stock_data)

@inventory_bp.route('/add-stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    if request.method == 'POST':
        try:
            InventoryService.update_stock(
                request.form['medicine_id'],
                request.form['quantity']
            )
            flash('Stock updated successfully', 'success')
            return redirect(url_for('inventory.view_stock'))
        except Exception as e:
            flash(f'Error updating stock: {str(e)}', 'danger')
            
    medicines = InventoryService.get_all_medicines()
    return render_template('add_stock.html', medicines=medicines)

@inventory_bp.route('/delete-medicine/<int:medicine_id>')
@login_required
def delete_medicine(medicine_id):
    if InventoryService.delete_medicine(medicine_id):
        flash('Medicine and related records deleted successfully', 'success')
    else:
        flash('Medicine not found', 'danger')
    return redirect(url_for('inventory.list_medicines'))
@inventory_bp.route('/export-csv')
@login_required
def export_csv():
    from flask import Response
    csv_data = InventoryService.export_inventory_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=inventory_export.csv"}
    )
