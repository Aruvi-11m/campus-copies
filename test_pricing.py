from backend.app import pricing

class MockPricing:
    single_side_price = 1
    double_side_price = 1.55
    multi_page_price = 2
    color_price = 10
    spiral_binding_price = 10
    soft_binding_price = 40
    gst_percent = 0

cost = pricing.calculate_cost(pages=39, copies=1, print_type="multi_page", color="black_white", binding="none", pricing=MockPricing())
print(cost)
