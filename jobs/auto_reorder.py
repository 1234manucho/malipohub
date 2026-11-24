from models import Item
from services.stock_service import low_stock_items


def preflight(job):
    item = Item.query.get(job.ref_id)
    if not item:
        return False, "Item missing"
    if item.stock_qty > item.reorder_level:
        return False, "Stock above reorder level"
    return True, "ok"


def fire(job):
    lows = low_stock_items(job.company_id)
    return f"{len(lows)} items below reorder level"