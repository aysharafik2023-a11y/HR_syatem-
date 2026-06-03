/* ── HR System Frontend ── */
const API = "";

// ── Data caches ──
let jobsCache = [];
let candidatesCache = [];
let applicationsCache = [];

// ── Helpers ──
async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json", ...opts.headers },
    ...opts,
  });
  if (res.status === 204) return null;
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

function toast(msg, type = "success") {
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  document.getElementById("toast-container").appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function fmtDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function fmtSalary(min, max) {
  const f = (v) => "$" + Number(v).toLocaleString();
  if (min && max) return `${f(min)} – ${f(max)}`;
  if (min) return `${f(min)}+`;
  if (max) return `Up to ${f(max)}`;
  return "—";
}

function badge(status) {
  return `<span class="badge badge-${status}">${status}</span>`;
}

function esc(str) {
  if (!str) return "";
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

// ── Navigation ──
document.querySelectorAll(".nav-item[data-page]").forEach((el) => {
  el.addEventListener("click", (e) => {
    e.preventDefault();
    navigateTo(el.dataset.page);
  });
});

function navigateTo(page) {
  document.querySelectorAll(".nav-item").forEach((n) => n.classList.remove("active"));
  document.querySelector(`.nav-item[data-page="${page}"]`).classList.add("active");
  document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
  document.getElementById(`page-${page}`).classList.add("active");
  const titles = {
    dashboard: "Dashboard", jobs: "Job Postings", candidates: "Candidates",
    applications: "Applications", pipeline: "Hiring Pipeline",
    policies: "Policy Documents", chatbot: "HR Chatbot",
  };
  document.getElementById("page-title").textContent = titles[page] || page;
  if (page === "dashboard") loadDashboard();
  if (page === "jobs") loadJobs();
  if (page === "candidates") loadCandidates();
  if (page === "applications") loadApplications();
  if (page === "pipeline") loadPipeline();
  if (page === "policies") loadPolicies();
}

// ── Modals ──
function openModal(id) { document.getElementById(id).classList.add("open"); }
function closeModal(id) { document.getElementById(id).classList.remove("open"); }

// Close modal on overlay click
document.querySelectorAll(".modal-overlay").forEach((el) => {
  el.addEventListener("click", (e) => {
    if (e.target === el) el.classList.remove("open");
  });
});

// ══════════════════════════════════════
// Dashboard
// ══════════════════════════════════════
async function loadDashboard() {
  try {
    const [jobs, candidates, apps, policies] = await Promise.all([
      api("/recruitment/jobs"),
      api("/recruitment/candidates"),
      api("/recruitment/applications"),
      api("/policies/documents"),
    ]);
    jobsCache = jobs;
    candidatesCache = candidates;
    applicationsCache = apps;

    const openJobs = jobs.filter((j) => j.status === "open").length;
    const activeApps = apps.filter((a) => !["hired", "rejected"].includes(a.status)).length;

    document.getElementById("stats-grid").innerHTML = `
      <div class="stat-card"><div class="stat-icon blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg></div><div class="stat-label">Open Jobs</div><div class="stat-value">${openJobs}</div></div>
      <div class="stat-card"><div class="stat-icon green"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg></div><div class="stat-label">Candidates</div><div class="stat-value">${candidates.length}</div></div>
      <div class="stat-card"><div class="stat-icon purple"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/></svg></div><div class="stat-label">Active Applications</div><div class="stat-value">${activeApps}</div></div>
      <div class="stat-card"><div class="stat-icon amber"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg></div><div class="stat-label">Policies</div><div class="stat-value">${policies.length}</div></div>
    `;

    const recent = [...apps].sort((a, b) => new Date(b.applied_at) - new Date(a.applied_at)).slice(0, 5);
    document.getElementById("dashboard-apps").innerHTML = recent.length
      ? recent.map((a) => {
          const job = jobs.find((j) => j.id === a.job_posting_id);
          const cand = candidates.find((c) => c.id === a.candidate_id);
          return `<tr><td>${a.id}</td><td>${esc(job?.title || "—")}</td><td>${esc(cand?.name || "—")}</td><td>${badge(a.status)}</td><td>${fmtDate(a.applied_at)}</td></tr>`;
        }).join("")
      : '<tr><td colspan="5" class="empty-state"><p>No applications yet</p></td></tr>';
  } catch (e) {
    toast(e.message, "error");
  }
}

// ══════════════════════════════════════
// Jobs
// ══════════════════════════════════════
async function loadJobs() {
  try {
    const filter = document.getElementById("jobs-filter").value;
    const url = filter ? `/recruitment/jobs?status=${filter}` : "/recruitment/jobs";
    const jobs = await api(url);
    jobsCache = jobs;
    document.getElementById("jobs-table").innerHTML = jobs.length
      ? jobs.map((j) => `<tr>
          <td>${j.id}</td><td>${esc(j.title)}</td><td>${esc(j.department)}</td>
          <td>${esc(j.location)}</td><td>${fmtSalary(j.salary_min, j.salary_max)}</td>
          <td>${badge(j.status)}</td>
          <td><button class="btn btn-danger btn-sm" onclick="deleteJob(${j.id})">Delete</button></td>
        </tr>`).join("")
      : '<tr><td colspan="7" class="empty-state"><p>No job postings found</p></td></tr>';
  } catch (e) {
    toast(e.message, "error");
  }
}

document.getElementById("jobs-filter").addEventListener("change", loadJobs);

async function createJob() {
  try {
    const body = {
      title: document.getElementById("job-title").value,
      description: document.getElementById("job-desc").value,
      department: document.getElementById("job-dept").value,
      location: document.getElementById("job-loc").value,
      status: document.getElementById("job-status").value,
    };
    const salMin = document.getElementById("job-sal-min").value;
    const salMax = document.getElementById("job-sal-max").value;
    if (salMin) body.salary_min = parseInt(salMin);
    if (salMax) body.salary_max = parseInt(salMax);
    await api("/recruitment/jobs", { method: "POST", body: JSON.stringify(body) });
    closeModal("job-modal");
    toast("Job posting created");
    loadJobs();
    // Clear form
    ["job-title","job-desc","job-dept","job-loc","job-sal-min","job-sal-max"].forEach(id => document.getElementById(id).value = "");
    document.getElementById("job-status").value = "draft";
  } catch (e) {
    toast(e.message, "error");
  }
}

async function deleteJob(id) {
  if (!confirm("Delete this job posting?")) return;
  try {
    await api(`/recruitment/jobs/${id}`, { method: "DELETE" });
    toast("Job deleted");
    loadJobs();
  } catch (e) {
    toast(e.message, "error");
  }
}

// ══════════════════════════════════════
// Candidates
// ══════════════════════════════════════
async function loadCandidates() {
  try {
    const candidates = await api("/recruitment/candidates");
    candidatesCache = candidates;
    document.getElementById("candidates-table").innerHTML = candidates.length
      ? candidates.map((c) => `<tr>
          <td>${c.id}</td><td>${esc(c.name)}</td><td>${esc(c.email)}</td>
          <td>${esc(c.phone || "—")}</td><td>${esc(c.skills || "—")}</td><td>${fmtDate(c.created_at)}</td>
        </tr>`).join("")
      : '<tr><td colspan="6" class="empty-state"><p>No candidates found</p></td></tr>';
  } catch (e) {
    toast(e.message, "error");
  }
}

async function createCandidate() {
  try {
    const body = {
      name: document.getElementById("cand-name").value,
      email: document.getElementById("cand-email").value,
    };
    const phone = document.getElementById("cand-phone").value;
    const skills = document.getElementById("cand-skills").value;
    const resume = document.getElementById("cand-resume").value;
    if (phone) body.phone = phone;
    if (skills) body.skills = skills;
    if (resume) body.resume_text = resume;
    await api("/recruitment/candidates", { method: "POST", body: JSON.stringify(body) });
    closeModal("candidate-modal");
    toast("Candidate added");
    loadCandidates();
    ["cand-name","cand-email","cand-phone","cand-skills","cand-resume"].forEach(id => document.getElementById(id).value = "");
  } catch (e) {
    toast(e.message, "error");
  }
}

// ══════════════════════════════════════
// Applications
// ══════════════════════════════════════
async function loadApplications() {
  try {
    const [apps, jobs, candidates] = await Promise.all([
      api("/recruitment/applications"),
      api("/recruitment/jobs"),
      api("/recruitment/candidates"),
    ]);
    applicationsCache = apps;
    jobsCache = jobs;
    candidatesCache = candidates;
    document.getElementById("applications-table").innerHTML = apps.length
      ? apps.map((a) => {
          const job = jobs.find((j) => j.id === a.job_posting_id);
          const cand = candidates.find((c) => c.id === a.candidate_id);
          return `<tr>
            <td>${a.id}</td><td>${esc(job?.title || "—")}</td><td>${esc(cand?.name || "—")}</td>
            <td>${badge(a.status)}</td><td>${fmtDate(a.applied_at)}</td>
            <td><button class="btn btn-secondary btn-sm" onclick="openStatusModal(${a.id},'${a.status}')">Update</button></td>
          </tr>`;
        }).join("")
      : '<tr><td colspan="6" class="empty-state"><p>No applications found</p></td></tr>';
  } catch (e) {
    toast(e.message, "error");
  }
}

async function openNewApplicationModal() {
  try {
    const [jobs, candidates] = await Promise.all([
      api("/recruitment/jobs"),
      api("/recruitment/candidates"),
    ]);
    const jobSel = document.getElementById("app-job");
    const candSel = document.getElementById("app-candidate");
    jobSel.innerHTML = jobs.map((j) => `<option value="${j.id}">${esc(j.title)} (${j.department})</option>`).join("");
    candSel.innerHTML = candidates.map((c) => `<option value="${c.id}">${esc(c.name)} (${esc(c.email)})</option>`).join("");
    openModal("application-modal");
  } catch (e) {
    toast(e.message, "error");
  }
}

async function createApplication() {
  try {
    const body = {
      job_posting_id: parseInt(document.getElementById("app-job").value),
      candidate_id: parseInt(document.getElementById("app-candidate").value),
    };
    const cover = document.getElementById("app-cover").value;
    if (cover) body.cover_letter = cover;
    await api("/recruitment/applications", { method: "POST", body: JSON.stringify(body) });
    closeModal("application-modal");
    toast("Application created");
    loadApplications();
    document.getElementById("app-cover").value = "";
  } catch (e) {
    toast(e.message, "error");
  }
}

function openStatusModal(appId, currentStatus) {
  document.getElementById("status-app-id").value = appId;
  document.getElementById("status-select").value = currentStatus;
  openModal("status-modal");
}

async function updateApplicationStatus() {
  const appId = document.getElementById("status-app-id").value;
  const status = document.getElementById("status-select").value;
  try {
    await api(`/recruitment/applications/${appId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    closeModal("status-modal");
    toast("Status updated");
    loadApplications();
  } catch (e) {
    toast(e.message, "error");
  }
}

// ══════════════════════════════════════
// Pipeline
// ══════════════════════════════════════
async function loadPipeline() {
  try {
    const [apps, jobs, candidates] = await Promise.all([
      api("/recruitment/applications"),
      api("/recruitment/jobs"),
      api("/recruitment/candidates"),
    ]);
    const stages = ["applied", "screening", "interview", "offer", "hired", "rejected"];
    const board = document.getElementById("pipeline-board");
    board.innerHTML = stages.map((stage) => {
      const items = apps.filter((a) => a.status === stage);
      return `<div class="pipeline-col">
        <h4>${stage} (${items.length})</h4>
        ${items.map((a) => {
          const job = jobs.find((j) => j.id === a.job_posting_id);
          const cand = candidates.find((c) => c.id === a.candidate_id);
          return `<div class="pipeline-card">
            <div class="name">${esc(cand?.name || "Unknown")}</div>
            <div class="meta">${esc(job?.title || "—")} &bull; ${fmtDate(a.applied_at)}</div>
          </div>`;
        }).join("") || '<div style="text-align:center;color:var(--gray-400);font-size:.8rem;padding:.5rem;">Empty</div>'}
      </div>`;
    }).join("");
  } catch (e) {
    toast(e.message, "error");
  }
}

// ══════════════════════════════════════
// Policies
// ══════════════════════════════════════
async function loadPolicies() {
  try {
    const docs = await api("/policies/documents");
    document.getElementById("policies-table").innerHTML = docs.length
      ? docs.map((d) => `<tr>
          <td>${d.id}</td><td><a href="#" onclick="viewPolicy(${d.id});return false;">${esc(d.title)}</a></td>
          <td>${esc(d.category)}</td><td>${esc(d.version)}</td><td>${fmtDate(d.uploaded_at)}</td>
          <td><button class="btn btn-danger btn-sm" onclick="deletePolicy(${d.id})">Delete</button></td>
        </tr>`).join("")
      : '<tr><td colspan="6" class="empty-state"><p>No policies uploaded yet</p></td></tr>';
  } catch (e) {
    toast(e.message, "error");
  }
}

async function uploadPolicy() {
  try {
    const body = {
      title: document.getElementById("policy-title").value,
      content: document.getElementById("policy-content").value,
      category: document.getElementById("policy-category").value,
      version: document.getElementById("policy-version").value || "1.0",
    };
    await api("/policies/documents", { method: "POST", body: JSON.stringify(body) });
    closeModal("policy-modal");
    toast("Policy uploaded");
    loadPolicies();
    ["policy-title","policy-content","policy-category"].forEach(id => document.getElementById(id).value = "");
    document.getElementById("policy-version").value = "1.0";
  } catch (e) {
    toast(e.message, "error");
  }
}

async function deletePolicy(id) {
  if (!confirm("Delete this policy?")) return;
  try {
    await api(`/policies/documents/${id}`, { method: "DELETE" });
    toast("Policy deleted");
    loadPolicies();
  } catch (e) {
    toast(e.message, "error");
  }
}

async function viewPolicy(id) {
  try {
    const doc = await api(`/policies/documents/${id}`);
    document.getElementById("view-policy-title").textContent = doc.title;
    document.getElementById("view-policy-cat").textContent = doc.category;
    document.getElementById("view-policy-ver").textContent = `v${doc.version}`;
    document.getElementById("view-policy-content").textContent = doc.content;
    openModal("view-policy-modal");
  } catch (e) {
    toast(e.message, "error");
  }
}

async function searchPolicies() {
  const query = document.getElementById("policy-search").value.trim();
  if (!query) {
    document.getElementById("policy-search-results").innerHTML = "";
    return;
  }
  try {
    const data = await api("/policies/query", {
      method: "POST",
      body: JSON.stringify({ query, top_k: 5 }),
    });
    const container = document.getElementById("policy-search-results");
    if (!data.results.length) {
      container.innerHTML = '<div class="card"><div class="card-body empty-state"><p>No results found</p></div></div>';
      return;
    }
    container.innerHTML = `<div class="card"><div class="card-header"><h2>Search Results for "${esc(query)}"</h2></div><div class="card-body">
      ${data.results.map((r) => `<div style="margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid var(--gray-100);">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <strong>${esc(r.title)}</strong>
          <span style="font-size:.75rem;color:var(--gray-500);">Score: ${r.relevance_score.toFixed(4)}</span>
        </div>
        <p style="font-size:.85rem;color:var(--gray-600);margin-top:.25rem;">${esc(r.content.substring(0, 200))}${r.content.length > 200 ? "..." : ""}</p>
      </div>`).join("")}
    </div></div>`;
  } catch (e) {
    toast(e.message, "error");
  }
}

// ══════════════════════════════════════
// Chatbot
// ══════════════════════════════════════
let conversationId = null;

async function sendChat() {
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();
  if (!msg) return;
  input.value = "";

  const messagesEl = document.getElementById("chat-messages");
  messagesEl.innerHTML += `<div class="chat-msg user">${esc(msg)}</div>`;
  messagesEl.scrollTop = messagesEl.scrollHeight;

  try {
    const body = { message: msg };
    if (conversationId) body.conversation_id = conversationId;
    const data = await api("/chat/", { method: "POST", body: JSON.stringify(body) });
    conversationId = data.conversation_id;

    let html = esc(data.message);
    if (data.sources && data.sources.length) {
      html += `<div class="sources">Sources: ${data.sources.map(s => esc(s)).join(", ")}</div>`;
    }
    messagesEl.innerHTML += `<div class="chat-msg bot">${html}</div>`;
    messagesEl.scrollTop = messagesEl.scrollHeight;
  } catch (e) {
    messagesEl.innerHTML += `<div class="chat-msg bot" style="background:#fee2e2;">Error: ${esc(e.message)}</div>`;
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }
}

// ── Init ──
loadDashboard();
