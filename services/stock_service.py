from datetime import datetime
from decimal import Decimal
from extensions import db
from models import Item, PurchaseOrder, StockMovement


def apply_stock_movement(company_id, user_id, item: Item, qty: Decimal,
                        mtype="purchase", reference="", note=""):
    item.stock_qty = Decimal(str(item.stock_qty or 0)) + qty
    db.session.add(StockMovement(
        company_id=company_id, item_id=item.id, movement_type=mtype,
        qty=qty, reference=reference, note=note, created_by=user_id,
    ))
    db.session.commit()
    return item


def receive_purchase_order(po: PurchaseOrder, user_id):
    for line in po.lines:
        item = Item.query.get(line.item_id)
        if item:
            apply_stock_movement(po.company_id, user_id, item,
                                 Decimal(str(line.qty)), "purchase", po.reference)
    po.status = "received"
    po.received_at = datetime.utcnow()
    db.session.commit()
    return po


def low_stock_items(company_id):
    return (Item.query
            .filter(Item.company_id == company_id, Item.active.is_(True))
            .filter(Item.stock_qty <= Item.reorder_level).all())