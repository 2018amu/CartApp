// -----------------------------
// Load cart from localStorage
// -----------------------------
let cart = JSON.parse(localStorage.getItem("cart")) || [];

// -----------------------------
// Render Cart
// -----------------------------
function renderCart() {
  const container = document.getElementById("cart-items");
  const totalEl = document.getElementById("cart-total");

  if (!container || !totalEl) return;

  if (!cart.length) {
    container.innerHTML = `
      <div class="empty">
        <h3>Your cart is empty 😕</h3>
        <p>Start shopping and add items to your cart.</p>
      </div>
    `;
    totalEl.textContent = "0";
    return;
  }

  let total = 0;

  container.innerHTML = cart
    .map((item, index) => {
      total += item.price * item.quantity;

      return `
        <div class="cart-item">
          <img src="${item.image}" alt="${item.name}">
          <div class="cart-info">
            <h4>${item.name}</h4>
            <p>LKR ${item.price.toLocaleString()}</p>
          </div>
          <div class="qty-box">
            <button onclick="changeQty(${index}, -1)">−</button>
            <div class="qty">${item.quantity}</div>
            <button onclick="changeQty(${index}, 1)">+</button>
            <button class="remove" onclick="removeItem(${index})">✕</button>
          </div>
        </div>
      `;
    })
    .join("");

  totalEl.textContent = total.toLocaleString();
}

// -----------------------------
// Cart operations
// -----------------------------
function changeQty(index, change) {
  if (!cart[index]) return;

  cart[index].quantity += change;
  if (cart[index].quantity <= 0) {
    cart.splice(index, 1);
  }
  saveCart();
}

function removeItem(index) {
  if (!cart[index]) return;

  cart.splice(index, 1);
  saveCart();
}

function clearCart() {
  cart = [];
  saveCart(); // handles localStorage & re-render
}

function saveCart() {
  localStorage.setItem("cart", JSON.stringify(cart));
  renderCart();
}

function goBack() {
  window.location.href = "/store";
}

// -----------------------------
// Checkout
// -----------------------------
async function checkout() {
  if (!cart.length) {
    alert("Your cart is empty");
    return;
  }

  const orderData = {
    user_id: localStorage.getItem("userId") || "guest",
    items: cart.map(item => ({
      product_id: item._id || item.id,
      name: item.name,
      price: item.price,
      quantity: item.quantity
    })),
    total_amount: cart.reduce((sum, i) => sum + i.price * i.quantity, 0),
    payment_method: "cod"
  };

  try {
    const btn = document.getElementById("checkoutBtn");
    if (btn) btn.disabled = true;

    const response = await fetch("/api/store/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(orderData)
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      alert(data.error || "Order failed. Please try again.");
      if (btn) btn.disabled = false;
      return;
    }

    // Save for payment-success page
    sessionStorage.setItem("orderId", data.order_id);
    sessionStorage.setItem("totalAmount", String(data.total_amount));
    sessionStorage.setItem("paymentStatus", "completed");

    // Clear cart
    clearCart();

    // Redirect to payment-success page
    window.location.href = "/store/cart/payment-success";

  } catch (err) {
    console.error("Checkout error:", err);
    alert("Server error. Please try again later.");
    if (btn) btn.disabled = false;
  }
}


// -----------------------------
// Initialize cart page
// -----------------------------
document.addEventListener("DOMContentLoaded", () => {
  renderCart();

  const checkoutBtn = document.getElementById("checkoutBtn");
  if (checkoutBtn) {
    checkoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      checkout();
    });
  }
});
