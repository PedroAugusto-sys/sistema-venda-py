from collections import defaultdict

def build_day_report(clients_data, date_str):
    sales_rows = []
    product_totals = defaultdict(lambda: {"qty": 0, "total": 0.0})

    total_sales = 0.0
    total_paid = 0.0

    for client_name, client in clients_data.items():
        for sale in client.get("sales", []):
            if sale.get("date") != date_str:
                continue
            if sale.get("cancelled", False):
                continue

            total = float(sale.get("total", 0.0))
            paid_amount = float(sale.get("paid_amount", 0.0))
            if sale.get("paid", False) and paid_amount == 0.0:
                paid_amount = total

            remaining = max(total - paid_amount, 0.0)

            sales_rows.append({
                "client": client_name,
                "sale_id": sale.get("id"),
                "date": sale.get("date"),
                "total": total,
                "paid": sale.get("paid", False),
                "paid_amount": paid_amount,
                "remaining": remaining,
                "payment_method": sale.get("payment_method_display", sale.get("payment_method", "N/A")),
                "installments": sale.get("installments", 1)
            })

            total_sales += total
            total_paid += paid_amount

            for item in sale.get("items", []):
                name = item.get("name")
                qty = int(item.get("quantity", 1))
                line_total = float(item.get("line_total", item.get("price", 0.0) * qty))
                if name:
                    product_totals[name]["qty"] += qty
                    product_totals[name]["total"] += line_total

    total_pending = max(total_sales - total_paid, 0.0)

    products_rows = [
        {"name": name, "qty": data["qty"], "total": data["total"]}
        for name, data in product_totals.items()
    ]

    return {
        "sales_rows": sales_rows,
        "products_rows": products_rows,
        "summary": {
            "total_sales": total_sales,
            "total_paid": total_paid,
            "total_pending": total_pending
        }
    }
