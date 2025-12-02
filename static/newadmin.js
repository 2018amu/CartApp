let lang = "en";
let services = [];
let categories = [];
let profile_id = null;

// ------------------- CATEGORY MANAGEMENT -------------------
async function loadCategories() {
  const res = await fetch("/api/categories");
  categories = await res.json();

  const el = document.getElementById("cat-result");
  el.innerHTML = categories
    .map((c) => {
      return `<div class="cat-item">
                <strong>${c.id}</strong> - ${c.name?.en || c.id} 
                [Ministries: ${(c.ministry_ids || []).join(", ")}]
            </div>`;
    })
    .join("");
}
async function createCategory() {
    const id = document.getElementById("cat-id").value.trim();
    const en = document.getElementById("cat-name-en").value.trim();
    const si = document.getElementById("cat-name-si").value.trim();
    const ta = document.getElementById("cat-name-ta").value.trim();
    const ministries = document
        .getElementById("cat-ministry")
        .value.trim()
        .split(",")
        .map(x => x.trim())
        .filter(x => x !== "");

    const payload = {
        id,
        name: { en, si, ta },
        ministry_ids: ministries
    };

    try {
        const res = await fetch("/api/categories", {   // <-- NO TRAILING SLASH
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Failed to add category.");
            return;
        }

        alert(data.message || "Category added successfully!");
       // loadCategories();

    } catch (err) {
        console.error("Fetch error:", err);
        alert("Cannot connect to server.");
    }
}




// ------------------- OFFICERS MANAGEMENT -------------------
async function loadOfficers() {
  const res = await fetch("/api/officers");
  const officers = await res.json();
  const el = document.getElementById("off-result");
  el.innerHTML = officers
    .map(
      (o) =>
        `<div>${o.id} - ${o.name} (${o.role}) - Ministry: ${o.ministry_id}</div>`
    )
    .join("");
}

async function createOfficer() {
    const payload = {
      id: document.getElementById("off-id").value.trim(),
      name: document.getElementById("off-name").value.trim(),
      role: document.getElementById("off-role").value.trim(),
      ministry_id: document.getElementById("off-ministry").value.trim(),
      email: document.getElementById("off-email").value.trim(),
      phone: document.getElementById("off-phone").value.trim(),
    };
  
    console.log("Sending payload:", payload);   // DEBUG
  
    const res = await fetch("/api/officers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  
    const data = await res.json();
    alert(data.message);
   // loadOfficers();
  }
  

// ------------------- ADS MANAGEMENT -------------------
async function loadAds() {
  const res = await fetch("/api/ads");
  const ads = await res.json();
  const el = document.getElementById("ad-result");
  el.innerHTML = ads
    .map(
      (a) =>
        `<div class="ad-card"><strong>${a.title}</strong> - ${
          a.body || ""
        } [<a href="${a.link}" target="_blank">Link</a>]</div>`
    )
    .join("");
}

async function createAd() {
    const payload = {
      id: document.getElementById("ad-id").value.trim(),
      title: document.getElementById("ad-title").value.trim(),
      body: document.getElementById("ad-body").value.trim(),
      link: document.getElementById("ad-link").value.trim(),
      image: document.getElementById("ad-image").value.trim(),
    };
  
    console.log("Sending Ad payload:", payload); // Debug log
  
    const res = await fetch("/api/ads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  
    const data = await res.json();
  
    if (data.error) {
      alert("❌ ERROR: " + data.error);
      return;
    }
  
    alert("✔ Ad added successfully!");
   // loadAds(); // refresh list
  }
  

// ------------------- AI INDEX MANAGEMENT -------------------
async function rebuildIndex() {
  const res = await fetch("/api/ai/rebuild", { method: "POST" });
  const data = await res.json();
  document.getElementById("index-result").innerText =
    data.message || "AI Index rebuilt!";
}

// ------------------- INITIAL LOAD -------------------
window.onload = async () => {
  //await loadCategories();
  //await loadOfficers();
  //await loadAds();

  // Load services if needed for other functionality
  const svcRes = await fetch("/api/services");
  services = await svcRes.json();
};
