from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from forms import ItemForm
from models import Item, PurchaseOrder
from services.stock_service import receive_purchase_order
from blueprints.stock import stock_bp
from utils.decorators import company_required, role_required


@stock_bp.route("/")
@login_required
@company_required
def index():
    items = (Item.query.filter_by(company_id=current_user.company_id)
             .order_by(Item.name).all())
    return render_template("stock/items.html", items=items)


@stock_bp.route("/items/new", methods=["GET", "POST"])
@login_required
@company_required
@role_required("admin", "finance", "manager")
def new_item():
    form = ItemForm()
    if form.validate_on_submit():
        db.session.add(Item(
            company_id=current_user.company_id, name=form.name.data,
            sku=form.sku.data, unit=form.unit.data or "pcs",
            cost_price=form.cost_price.data or 0,
            selling_price=form.selling_price.data or 0,
            stock_qty=form.stock_qty.data or 0,
            reorder_level=form.reorder_level.data or 0,
        ))
        db.session.commit()
        flash("Item saved.", "success")
        return redirect(url_for("stock.index"))
    return render_template("stock/item_form.html", form=form)


@stock_bp.route("/purchase-orders")
@login_required
@company_required
def purchase_orders():
    rows = (PurchaseOrder.query.filter_by(company_id=current_user.company_id)
            .order_by(PurchaseOrder.created_at.desc()).all())
    return render_template("stock/purchase_orders.html", orders=rows)


@stock_bp.route("/purchase-orders/<int:pid>/receive", methods=["POST"])
@login_required
@company_required
@role_required("admin", "finance", "manager")
def receive_po(pid):
    po = PurchaseOrder.query.get_or_404(pid)
    receive_purchase_order(po, current_user.id)
    flash("Purchase order received; stock updated.", "success")
    return redirect(url_for("stock.purchase_orders"))