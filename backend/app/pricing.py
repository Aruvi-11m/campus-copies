import math

def calculate_cost(pages, copies, print_type, color, binding, pricing):
    base_rate = {
        "single_side": pricing.single_side_price,
        "double_side": pricing.double_side_price,
        "multi_page": pricing.multi_page_price,
    }[print_type]

    per_page_rate = base_rate + (pricing.color_price if color == "color" else 0)
    
    if print_type == "multi_page":
        billable_pages = math.ceil(pages / 4.0)
    else:
        billable_pages = pages
        
    printing_cost = round(billable_pages * copies * per_page_rate, 2)

    binding_rate = {"none": 0, "spiral": pricing.spiral_binding_price,
                     "soft": pricing.soft_binding_price}[binding]
    binding_cost = round(binding_rate * copies, 2)

    subtotal = printing_cost + binding_cost
    gst_amount = round(subtotal * pricing.gst_percent / 100, 2)
    grand_total = round(subtotal + gst_amount, 2)
    
    return {
        "printing_cost": printing_cost,
        "binding_cost": binding_cost,
        "gst_amount": gst_amount,
        "grand_total": grand_total
    }
