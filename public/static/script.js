let lang = "en";
let services = [];
let currentServiceName = "";
let userId = null; // guest

// Load all services
async function loadServices() {
  try {
    const res = await fetch("/api/services");
    services = await res.json();

    const list = document.getElementById("service-list");
    list.innerHTML = "";

    services.forEach((s) => {
      const li = document.createElement("li");
      li.textContent = s.name[lang] || s.name.en;
      li.onclick = () => loadSubservices(s);
      list.appendChild(li);
    });

    list.style.display = "block";
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("question-list").innerHTML = "";
    document.getElementById("answer-box").innerHTML = "";

  } catch (err) {
    console.error("Error loading services:", err);
  }
}

// Language switch
function setLang(l) {
  lang = l;
  loadServices();
}

// Search ministries
document.getElementById("service-search").addEventListener("input", (e) => {
  const val = e.target.value.toLowerCase();
  const list = document.getElementById("service-list");

  Array.from(list.children).forEach((li) => {
    const text = li.textContent.toLowerCase();
    li.style.display = text.includes(val) ? "list-item" : "none";
  });
});

// Load subservices
function loadSubservices(service) {
  currentServiceName = service.name[lang] || service.name.en;

  const subList = document.getElementById("sub-list");
  subList.innerHTML = "";
  document.getElementById("sub-title").innerText = currentServiceName;

  (service.subservices || []).forEach((sub) => {
    const li = document.createElement("li");
    li.textContent = sub.name[lang] || sub.name.en;
    li.onclick = () => loadQuestions(sub);
    subList.appendChild(li);
  });

  document.getElementById("question-list").innerHTML = "";
  document.getElementById("answer-box").innerHTML = "";
}

// Load questions
function loadQuestions(sub) {
  const qList = document.getElementById("question-list");
  qList.innerHTML = "";
  document.getElementById("q-title").innerText = sub.name[lang] || sub.name.en;

  (sub.questions || []).forEach((q) => {
    const li = document.createElement("li");
    li.textContent = q.q[lang] || q.q.en;
    li.onclick = () => showAnswer(q);
    qList.appendChild(li);
  });

  document.getElementById("answer-box").innerHTML = "";
}

// Show answer + ask user age/job/desire and save it
function showAnswer(q) {
  let html = `<h3>${q.q[lang] || q.q.en}</h3>
              <p>${q.answer[lang] || q.answer.en}</p>`;

  if (q.downloads?.length) {
    html += `<p><b>Downloads:</b> ${q.downloads
      .map(d => `<a href="${d}" target="_blank">${d.split("/").pop()}</a>`).join(", ")}</p>`;
  }

  if (q.location) html += `<p><b>Location:</b> <a href="${q.location}" target="_blank">View Map</a></p>`;
  if (q.instructions) html += `<p><b>Instructions:</b> ${q.instructions}</p>`;

  document.getElementById("answer-box").innerHTML = html;

  // --------------------------
  // YOUR REQUESTED BLOCK ADDED
  // --------------------------
  setTimeout(async () => {
    let age = prompt("Enter your age (optional):");
    let job = prompt("Enter your job (optional):");
    let desire = prompt("What is your main interest here (optional)?");

    await fetch("/api/engagement", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: null,
        age: age,
        job: job,
        desires: desire ? [desire] : [],
        question_clicked: q.q[lang] || q.q.en,
        service: currentServiceName
      })
    });

  }, 200);
}

// Initialize
window.onload = loadServices;
