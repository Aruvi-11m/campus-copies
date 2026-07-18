const axios = require('axios');

async function test() {
  try {
    const pricingPayload = {
      "id": 1,
      "single_side_price": "1",
      "double_side_price": "1.55",
      "multi_page_price": "2",
      "color_price": "10",
      "spiral_binding_price": "35",
      "soft_binding_price": "40",
      "gst_percent": "0",
      "upi_id": "6381056942",
      "qr_code_path": null,
      "updated_at": "2026-07-18T10:00:00Z"
    };

    // We can't hit the API without logging in, but we want to know what Pydantic does.
    // Instead of hitting the API, let's write a python script to test pydantic validation directly.
  } catch (err) {
    console.error(err.response ? err.response.data : err.message);
  }
}
test();
