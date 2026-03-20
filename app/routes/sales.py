from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.sales_service import SalesService
from app.services.inventory_service import InventoryService

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        success, message = SalesService.record_sale(
            request.form['medicine_id'],
            request.form['quantity']
        )
        if success:
            flash(message, 'success')
            return redirect(url_for('inventory.view_stock'))
        else:
            flash(message, 'danger')
            
    medicines = InventoryService.get_all_medicines()
    selected_id = request.args.get('medicine_id', type=int)
    return render_template('add_sale.html', medicines=medicines, selected_id=selected_id)
