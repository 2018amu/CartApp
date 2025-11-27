let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentSub = null;
let profile_id = null;

// ------------------- Load categories -------------------
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
    loadAds();
}

// ------------------- Load subservices/ministries -------------------
async function loadMinistriesInCategory(cat) {
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("sub-title").innerText = cat.name?.[lang] || cat.name?.en || cat.id;

    if (cat.ministry_ids && cat.ministry_ids.length) {
        for (let id of cat.ministry_ids) {
            const r = await fetch(`/api/service/${id}`);
            const s = await r.json();
            if (s && s.subservices) {
                s.subservices.forEach(sub => {
                    let li = document.createElement("li");
                    li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
                    li.onclick = () => loadQuestions(s, sub);
                    document.getElementById("sub-list").appendChild(li);
                });
            }
        }
    } else {
        const svcRes = await fetch("/api/services");
        const all = await svcRes.json();
        all.filter(s => s.category === cat.id).forEach(s => {
            s.subservices.forEach(sub => {
                let li = document.createElement("li");
                li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
                li.onclick = () => loadQuestions(s, sub);
                document.getElementById("sub-list").appendChild(li);
            });
        });
    }
}

// ------------------- Load questions -------------------
async function loadQuestions(service, sub) {
    currentServiceName = service.name?.[lang] || service.name?.en;
    currentSub = sub;
    const qList = document.getElementById("question-list");
    qList.innerHTML = "";
    document.getElementById("q-title").innerText = sub.name?.[lang] || sub.name?.en || sub.id;

    (sub.questions || []).forEach(q => {
        let li = document.createElement("li");
        li.textContent = q.q?.[lang] || q.q?.en;
        li.onclick = () => showAnswer(service, sub, q);
        qList.appendChild(li);
    });
}

// ------------------- Show answer -------------------
function showAnswer(service, sub, q) {
    let html = `<h3>${q.q?.[lang] || q.q?.en}</h3>`;
    html += `<p>${q.answer?.[lang] || q.answer?.en}</p>`;
    if (q.downloads && q.downloads.length) {
        html += `<p><b>Downloads:</b> ${q.downloads.map(d => `<a href="${d}" target="_blank">${d.split("/").pop()}</a>`).join(", ")}</p>`;
    }
    if (q.location) {
        html += `<p><b>Location:</b> <a href="${q.location}" target="_blank">View Map</a></p>`;
    }
    if (q.instructions) {
        html += `<p><b>Instructions:</b> ${q.instructions}</p>`;
    }
    document.getElementById("answer-box").innerHTML = html;

    // Engagement log (non-blocking)
    fetch("/api/engagement", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: profile_id,
            age: null,
            job: null,
            desires: [],
            question_clicked: q.q?.[lang] || q.q?.en,
            service: currentServiceName
        })
    });
}

// ------------------- Chat -------------------
function openChat() { document.getElementById("chat-panel").style.display = "block"; }
function closeChat() { document.getElementById("chat-panel").style.display = "none"; }

async function sendChat() {
    const input = document.getElementById("chat-text");
    const text = input.value.trim();
    if (!text) return;
    appendChat("user", text);
    input.value = "";

    const res = await fetch("/api/ai/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text, top_k: 5 })
    });
    const data = await res.json();
    let reply = data.answer || "No answer found.";
    appendChat("bot", reply);

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

// ------------------- Autosuggest -------------------
let suggestTimer = null;
async function autosuggest(q) {
    clearTimeout(suggestTimer);
    if (!q || q.length < 2) {
        document.getElementById("suggestions").innerHTML = "";
        return;
    }
    suggestTimer = setTimeout(async () => {
        const res = await fetch(`/api/search/autosuggest?q=${encodeURIComponent(q)}`);
        const items = await res.json();
        const el = document.getElementById("suggestions");
        el.innerHTML = items.map(it => `<div class="s-item" onclick='pickSuggestion(${JSON.stringify(it)})'>${it.name?.en || it.name}</div>`).join("");
    }, 250);
}

function pickSuggestion(it) {
    if (it && it.subservices && it.subservices.length) {
        loadQuestions(it, it.subservices[0]);
    }
    document.getElementById("suggestions").innerHTML = "";
}

// ------------------- Profile modal flow -------------------
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

        // Step 1: basic
        let res1 = await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: data2.email, step: "basic", data: data1 })
        });
        let j1 = await res1.json();
        profile_id = j1.profile_id || null;

        // Step 2: contact
        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id: profile_id, step: "contact", data: data2 })
        });

        // Step 3: employment
        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id: profile_id, step: "employment", data: data3 })
        });

        // Force-close modal
        const modal = document.getElementById("profile-modal");
        if (modal) {
            modal.style.display = "none";
        }

        // Reset all steps
        document.querySelectorAll(".profile-step").forEach((el, idx) => {
            el.style.display = idx === 0 ? "block" : "none";
        });

        alert("Profile saved successfully!");
    } catch (err) {
        console.error("Error submitting profile:", err);
        alert("Error saving profile. Please try again.");
    }
}


// ------------------- Load ads -------------------
async function loadAds() {
    const res = await fetch("/api/ads");
    const ads = await res.json();
    const el = document.getElementById("ads-area");
    el.innerHTML = ads.map(a => `<div class="ad-card"><a href="${a.link || '#'}"><h4>${a.title}</h4><p>${a.body || ''}</p></a></div>`).join("");
}

// ------------------- Language switch -------------------
function setLang(l) {
    lang = l;
    loadCategories();
    if (currentSub) loadQuestions({ name: { [lang]: currentServiceName } }, currentSub);
}

// ------------------- Initial load -------------------
window.onload = async () => {
    await loadCategories();
    const svcRes = await fetch("/api/services");
    services = await svcRes.json();
};
