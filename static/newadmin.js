// Helper: Clear a list of input IDs
function clearInputs(ids) {
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });
}

// Helper: Show result messages
function showResult(id, message, status = "success") {
  const box = document.getElementById(id);
  box.style.display = "block";
  box.className = `result-box ${status}`;
  box.innerText = message;
}

// -------------------------
// CATEGORY CREATE
// -------------------------
async function createCategory() {
  const payload = {
    id: document.getElementById("cat-id").value.trim(),
    name: {
      en: document.getElementById("cat-name-en").value.trim(),
      si: document.getElementById("cat-name-si").value.trim(),
      ta: document.getElementById("cat-name-ta").value.trim(),
    },
    ministry_ids: document.getElementById("cat-ministry").value
      .split(",")
      .map((x) => x.trim()),
  };

  try {
    const res = await fetch("/api/categories", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) throw data;

    showResult("cat-result", "Category added successfully!");

    // RESET ALL FORMS except category
    clearInputs(["off-id", "off-name", "off-role", "off-ministry", "off-email", "off-phone"]);
    clearInputs(["ad-id", "ad-title", "ad-body", "ad-link", "ad-image"]);

  } catch (err) {
    showResult("cat-result", err.error || "Category creation failed", "error");
  }
}

// -------------------------
// OFFICER CREATE
// -------------------------
async function createOfficer() {
  const payload = {
    id: document.getElementById("off-id").value.trim(),
    name: document.getElementById("off-name").value.trim(),
    role: document.getElementById("off-role").value.trim(),
    ministry_id: document.getElementById("off-ministry").value.trim(),
    email: document.getElementById("off-email").value.trim(),
    phone: document.getElementById("off-phone").value.trim(),
  };

  try {
    const res = await fetch("/api/officers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) throw data;

    showResult("off-result", "Officer added successfully!");

    // RESET other forms
    clearInputs(["cat-id", "cat-name-en", "cat-name-si", "cat-name-ta", "cat-ministry"]);
    clearInputs(["ad-id", "ad-title", "ad-body", "ad-link", "ad-image"]);

  } catch (err) {
    showResult("off-result", err.error || "Officer creation failed", "error");
  }
}

// -------------------------
// AD CREATE
// -------------------------
async function createAd() {
  const payload = {
    id: document.getElementById("ad-id").value.trim(),
    title: document.getElementById("ad-title").value.trim(),
    body: document.getElementById("ad-body").value.trim(),
    link: document.getElementById("ad-link").value.trim(),
    image: document.getElementById("ad-image").value.trim(),
  };

  try {
    const res = await fetch("/api/ads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) throw data;

    showResult("ad-result", "Ad added successfully!");

    // RESET other forms
    clearInputs(["cat-id", "cat-name-en", "cat-name-si", "cat-name-ta", "cat-ministry"]);
    clearInputs(["off-id", "off-name", "off-role", "off-ministry", "off-email", "off-phone"]);

  } catch (err) {
    showResult("ad-result", err.error || "Ad creation failed", "error");
  }
}

// -------------------------
// AI INDEX REBUILD
// -------------------------
async function rebuildIndex() {
  try {
    const res = await fetch("/api/ai/rebuild", {
      method: "POST",
    });
    const data = await res.json();

    if (!res.ok) throw data;

    showResult("index-result", "AI index rebuilt successfully!");

  } catch (err) {
    showResult("index-result", err.error || "Index rebuild failed", "error");
  }
}
