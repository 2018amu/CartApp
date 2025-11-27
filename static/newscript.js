let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentSub = null;
let profile_id = null;

// -------------------- LANGUAGE --------------------
function setLang(l) {
    lang = l;
    loadCategories();
}

// -------------------- CATEGORIES --------------------
async function loadCategories() {
    const res = await fetch("/api/categories");
    categories = await res.json();
    const el = document.getElementById("category-list");
    el.innerHTML = "";
    categories.forEach(c => {
        const btn = document.createElement("div");
        btn.className = "cat-item";
        btn.textContent = c.name?.[lang] || c.name?.en || c.id;
        btn.onclick = () => loadMinistriesInCategory(c);
        el.appendChild(btn);
    });
}

// -------------------- MINISTRIES / SUBSERVICES --------------------
async function loadMinistriesInCategory(cat) {
    const subList = document.getElementById("sub-list");
    subList.innerHTML = "";
    document.getElementById("sub-title").innerText = cat.name?.[lang] || cat.name?.en || cat.id;

    const svcRes = await fetch("/api/services");
    const all = await svcRes.json();
    all.filter(s => s.category === cat.id).forEach(s => {
        s.subservices?.forEach(sub => {
            const li = document.createElement("li");
            li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
            li.onclick = () => loadQuestions(s, sub);
            subList.appendChild(li);
        });
    });
}

// -------------------- QUESTIONS --------------------
async function loadQuestions(service, sub) {
    currentServiceName = service.name?.[lang] || service.name?.en;
    currentSub = sub;
    const qList = document.getElementById("question-list");
    qList.innerHTML = "";
    document.getElementById("q-title").innerText = sub.name?.[lang] || sub.name?.en || sub.id;

    (sub.questions || []).forEach(q => {
        const li = document.createElement("li");
        li.textContent = q.q?.[lang] || q.q?.en;
        li.onclick = () => showAnswer(service, sub, q);
        qList.appendChild(li);
    });
}

function showAnswer(service, sub, q) {
    let html = `<h3>${q.q?.[lang] || q.q?.en}</h3>`;
    html += `<p>${q.answer?.[lang] || q.answer?.en}</p>`;

    if (q.downloads?.length) {
        html += `<p><b>Downloads:</b> ${q.downloads.map(d => `<a href="${d}" target="_blank">${d.split("/").pop()}</a>`).join(", ")}</p>`;
    }
    if (q.location) html += `<p><b>Location:</b> <a href="${q.location}" target="_blank">View Map</a></p>`;
    if (q.instructions) html += `<p><b>Instructions:</b> ${q.instructions}</p>`;

    html += `<p>
        <button onclick="alert('Download clicked')">Download</button>
        <button onclick="alert('Contact clicked')">Contact</button>
        <button onclick="alert('Apply clicked')">Apply</button>
    </p>`;

    document.getElementById("answer-box").innerHTML = html;

    // Log engagement
    fetch("/api/engagement", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: profile_id,
            question_clicked: q.q?.[lang] || q.q?.en,
            service: currentServiceName
        })
    });
}

// -------------------- ADS --------------------
async function loadAds() {
    try {
        const res = await fetch("/api/ads");
        if (!res.ok) throw new Error("Failed to fetch ads");
        const ads = await res.json();
        const el = document.getElementById("ads-area");
        el.innerHTML = ads.map(a => `<div class="ad-card"><a href="${a.link || '#'}"><h4>${a.title}</h4><p>${a.body || ''}</p></a></div>`).join("");
    } catch (err) {
        console.error("Error loading ads:", err);
        document.getElementById("ads-area").innerHTML = "<p>No ads available.</p>";
    }
}

// -------------------- CHAT --------------------
function openChat() { document.getElementById("chat-panel").style.display = "block"; }
function closeChat() { document.getElementById("chat-panel").style.display = "none"; }

async function sendChat() {
    const input = document.getElementById("chat-text");
    const text = input.value.trim();
    if (!text) return;
    appendChat("user", text);
    input.value = "";

    try {
        const res = await fetch("/api/ai/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: text, top_k: 5 })
        });
        const data = await res.json();
        const reply = data.answer || "No answer found.";
        appendChat("bot", reply);
    } catch {
        appendChat("bot", "AI service not available.");
    }

    // Log engagement
    fetch("/api/engagement", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: profile_id, question_clicked: text, service: null })
    });
}

function appendChat(sender, text) {
    const body = document.getElementById("chat-body");
    const div = document.createElement("div");
    div.className = "chat-msg " + (sender === "user" ? "user-msg" : "bot-msg");
    div.innerText = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
}

// -------------------- PROFILE MODAL --------------------
function showProfileModal() { document.getElementById("profile-modal").style.display = "block"; }
function profileNext(step) {
    document.getElementById(`profile-step-${step}`).style.display = "none";
    document.getElementById(`profile-step-${step + 1}`).style.display = "block";
}
function profileBack(step) {
    document.getElementById(`profile-step-${step}`).style.display = "none";
    document.getElementById(`profile-step-${step - 1}`).style.display = "block";
}

async function profileSubmit() {
    try {
        const data1 = { name: document.getElementById("p_name").value, age: document.getElementById("p_age").value };
        const data2 = { email: document.getElementById("p_email").value, phone: document.getElementById("p_phone").value };
        const data3 = { job: document.getElementById("p_job").value };

        // Step 1: create profile
        let res = await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ step: "basic", data: { ...data1, email: data2.email } })
        });
        let j = await res.json();
        if (!j.profile_id) {
            alert("Error saving profile. Check console.");
            console.error("Profile creation failed", j);
            return;
        }
        profile_id = j.profile_id;

        // Step 2: contact info
        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id, step: "contact", data: data2 })
        });

        // Step 3: employment info
        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id, step: "employment", data: data3 })
        });

        document.getElementById("profile-modal").style.display = "none";
        alert("Profile saved successfully!");

        // Load recommended services after profile saved
        loadRecommendedServices();
    } catch (err) {
        console.error("Profile save error:", err);
        alert("Error saving profile. Check console.");
    }
}

// -------------------- RECOMMENDED SERVICES --------------------
async function loadRecommendedServices() {
    if (!profile_id) return;

    try {
        const res = await fetch(`/api/engagement?user_id=${profile_id}`);
        const engagements = await res.json();

        const serviceCount = {};
        engagements.forEach(e => {
            if (e.service) serviceCount[e.service] = (serviceCount[e.service] || 0) + 1;
        });

        const topServices = Object.entries(serviceCount)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(e => e[0]);

        const el = document.getElementById("sub-list");
        el.innerHTML = "<h3>Recommended for you</h3>";
        topServices.forEach(s => {
            const li = document.createElement("li");
            li.textContent = s;
            li.onclick = async () => {
                const svcRes = await fetch("/api/services");
                const all = await svcRes.json();
                const svc = all.find(x => (x.name?.en || x.name?.[lang]) === s);
                if (svc?.subservices?.length) loadQuestions(svc, svc.subservices[0]);
            };
            el.appendChild(li);
        });
    } catch (err) {
        console.error("Error loading recommended services:", err);
    }
}

// -------------------- INITIAL LOAD --------------------
window.onload = async () => {
    await loadCategories();
    const svcRes = await fetch("/api/services");
    services = await svcRes.json();

    // Show modal for new users
    if (!profile_id) showProfileModal();
};
