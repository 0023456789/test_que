/* === CareBridge Health — SPA with Auth Pages === */

const API_BASE = "http://localhost/api";

/* ── State ── */
let accessToken = "";
let currentRole = "";
let currentPatientId = null;
let currentUsername = "";
let patientsCache = [];
let doctorsCache = [];

/* ── Pages ── */
const pageAuth = document.getElementById("pageAuth");
const pageDashboard = document.getElementById("pageDashboard");
const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");

/* ── Auth DOM ── */
const loginForm = document.getElementById("loginForm");
const loginBtn = document.getElementById("loginBtn");
const registerForm = document.getElementById("registerForm");
const registerBtn = document.getElementById("registerBtn");

/* ── Dashboard DOM ── */
const logoutBtn = document.getElementById("logoutBtn");
const topbarAvatar = document.getElementById("topbarAvatar");
const topbarUsername = document.getElementById("topbarUsername");
const topbarRoleBadge = document.getElementById("topbarRoleBadge");
const patientSelect = document.getElementById("patientSelect");
const patientSelectWrap = document.getElementById("patientSelectWrap");
const selfPatientWrap = document.getElementById("selfPatientWrap");
const selfPatient = document.getElementById("selfPatient");
const doctorSelect = document.getElementById("doctorSelect");
const appointmentForm = document.getElementById("appointmentForm");
const bookBtn = document.getElementById("bookBtn");
const appointmentsList = document.getElementById("appointmentsList");
const appointmentsLoading = document.getElementById("appointmentsLoading");
const appointmentsSubtitle = document.getElementById("appointmentsSubtitle");
const noAppointments = document.getElementById("noAppointments");
const hamburgerBtn = document.getElementById("hamburgerBtn");
const navMenu = document.getElementById("navMenu");
const toastContainer = document.getElementById("toastContainer");

/* ── Toast ── */
function showToast(message, type = "info") {
  const t = document.createElement("div");
  t.className = `toast toast-${type}`;
  const icons = { success: "✅", error: "❌", info: "ℹ️" };
  t.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${message}</span>`;
  toastContainer.appendChild(t);
  setTimeout(() => { t.classList.add("toast-out"); setTimeout(() => t.remove(), 300); }, 4000);
}

/* ── Helpers ── */
function authHeaders() {
  return { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` };
}

function setLoading(btn, on) {
  btn.classList.toggle("loading", on);
  btn.disabled = on;
}

function fillLogin(user, pass) {
  document.getElementById("loginUsername").value = user;
  document.getElementById("loginPassword").value = pass;
}
window.fillLogin = fillLogin;

function findPatientName(id) {
  const p = patientsCache.find(x => x.id === id);
  return p ? p.full_name : `Patient #${id}`;
}
function findDoctorName(id) {
  const d = doctorsCache.find(x => x.id === id);
  return d ? d.full_name : `Doctor #${id}`;
}
function formatDateTime(iso) {
  return new Date(iso).toLocaleString("vi-VN", {
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit"
  });
}

/* ── Tab switching ── */
document.getElementById("showRegisterLink").addEventListener("click", e => {
  e.preventDefault();
  loginTab.style.display = "none";
  registerTab.style.display = "block";
  registerTab.style.animation = "fadeUp 400ms ease-out";
});

document.getElementById("showLoginLink").addEventListener("click", e => {
  e.preventDefault();
  registerTab.style.display = "none";
  loginTab.style.display = "block";
  loginTab.style.animation = "fadeUp 400ms ease-out";
});

/* ── Hamburger ── */
hamburgerBtn.addEventListener("click", () => {
  hamburgerBtn.classList.toggle("open");
  navMenu.classList.toggle("open");
});
navMenu.addEventListener("click", () => {
  hamburgerBtn.classList.remove("open");
  navMenu.classList.remove("open");
});
logoutBtn.addEventListener("click", () => {
  hamburgerBtn.classList.remove("open");
  navMenu.classList.remove("open");
});

/* ── Task Page Navigation ── */
function switchTaskPage(pageId, navEl) {
  document.querySelectorAll('.task-page').forEach(p => p.style.display = 'none');
  document.querySelectorAll('#navMenu a').forEach(a => a.classList.remove('active'));

  const targetPage = document.getElementById(pageId);
  if (targetPage) {
    targetPage.style.display = 'block';
    targetPage.style.animation = "fadeUp 400ms ease-out";
  }
  if (navEl) navEl.classList.add('active');
}

document.getElementById("navHome").addEventListener("click", e => {
  e.preventDefault();
  switchTaskPage("pageHome", e.target);
});
document.getElementById("navBooking").addEventListener("click", e => {
  e.preventDefault();
  switchTaskPage("pageBooking", e.target);
});
document.getElementById("navAppointments").addEventListener("click", async e => {
  e.preventDefault();
  switchTaskPage("pageAppointmentsView", e.target);
  await loadAppointments();
});

/* ── Hero CTA buttons ── */
document.getElementById("heroCTABook").addEventListener("click", () => {
  switchTaskPage("pageBooking", document.getElementById("navBooking"));
});
document.getElementById("heroCTAAppts").addEventListener("click", async () => {
  switchTaskPage("pageAppointmentsView", document.getElementById("navAppointments"));
  await loadAppointments();
});

/* ── Navigate to dashboard ── */
function enterDashboard(username, role) {
  currentUsername = username;
  currentRole = role;
  pageAuth.style.display = "none";
  pageDashboard.style.display = "block";
  pageDashboard.style.animation = "fadeUp 500ms ease-out";

  topbarUsername.textContent = username;
  topbarRoleBadge.textContent = role.toUpperCase();
  topbarAvatar.textContent = username.charAt(0).toUpperCase();
  topbarAvatar.className = `user-avatar user-avatar-sm role-${role}`;

  // Role-based nav visibility
  const navBooking = document.getElementById("navBooking");
  const navHome = document.getElementById("navHome");
  navBooking.style.display = (role === "doctor") ? "none" : "block";

  switchTaskPage("pageHome", navHome);
}

/* ── Load data ── */
async function loadPatients() {
  if (currentRole === "patient") {
    const r = await fetch(`${API_BASE}/patients/self`, { headers: { Authorization: `Bearer ${accessToken}` } });
    if (!r.ok) throw new Error("Cannot load self");
    const p = await r.json();
    currentPatientId = p.id;
    selfPatient.value = `${p.full_name} (ID ${p.id})`;
    patientSelectWrap.style.display = "none";
    selfPatientWrap.style.display = "flex";
    return;
  }
  const r = await fetch(`${API_BASE}/patients`, { headers: { Authorization: `Bearer ${accessToken}` } });
  if (!r.ok) throw new Error("Cannot load patients");
  const data = await r.json();
  patientsCache = data;
  patientSelect.innerHTML = data.map(p => `<option value="${p.id}">${p.full_name} (ID ${p.id})</option>`).join("");
  patientSelectWrap.style.display = "flex";
  selfPatientWrap.style.display = "none";
}

async function loadDoctors() {
  const r = await fetch(`${API_BASE}/doctors`, { headers: { Authorization: `Bearer ${accessToken}` } });
  if (!r.ok) throw new Error("Cannot load doctors");
  const data = await r.json();
  doctorsCache = data;
  doctorSelect.innerHTML = data.map(d => `<option value="${d.id}">${d.full_name} — ${d.specialty}</option>`).join("");
}

function renderAppointmentCard(a) {
  const canManage = currentRole === "staff" || currentRole === "doctor";
  let btns = "";
  if (canManage && a.status === "BOOKED") {
    btns = `<button class="cta cta-sm" onclick="updateStatus(${a.id},'CONFIRMED')">✓ Confirm</button>`
         + `<button class="cta cta-sm cta-danger" onclick="updateStatus(${a.id},'CANCELED')">✕ Cancel</button>`;
  } else if (canManage && a.status === "CONFIRMED") {
    btns = `<button class="cta cta-sm" onclick="updateStatus(${a.id},'COMPLETED')">✓ Complete</button>`
         + `<button class="cta cta-sm cta-danger" onclick="updateStatus(${a.id},'CANCELED')">✕ Cancel</button>`;
  }
  return `
    <div class="appointment-card">
      <div class="appt-id">#${a.id}</div>
      <div class="appt-details">
        <div class="appt-reason">${a.reason || "No reason specified"}</div>
        <div class="appt-meta">
          <span>👤 ${findPatientName(a.patient_id)}</span>
          <span>🩺 ${findDoctorName(a.doctor_id)}</span>
          <span>📅 ${formatDateTime(a.appointment_time)}</span>
          <span class="status-badge status-${a.status}">${a.status}</span>
        </div>
      </div>
      <div class="appt-actions">${btns}</div>
    </div>`;
}

async function loadAppointments() {
  appointmentsLoading.style.display = "flex";
  noAppointments.style.display = "none";
  appointmentsList.innerHTML = "";
  try {
    const r = await fetch(`${API_BASE}/appointments`, { headers: { Authorization: `Bearer ${accessToken}` } });
    if (!r.ok) throw new Error("Failed");
    const appts = await r.json();
    appointmentsLoading.style.display = "none";
    if (!appts.length) {
      noAppointments.style.display = "block";
      appointmentsSubtitle.textContent = "No appointments found.";
      return;
    }
    const label = currentRole === "staff" ? " (all)" : currentRole === "doctor" ? " (assigned)" : "";
    appointmentsSubtitle.textContent = `${appts.length} appointment(s)${label}`;
    appointmentsList.innerHTML = appts.map(renderAppointmentCard).join("");
  } catch {
    appointmentsLoading.style.display = "none";
    showToast("Failed to load appointments.", "error");
  }
}

async function updateStatus(id, status) {
  try {
    const r = await fetch(`${API_BASE}/appointments/${id}/status`, {
      method: "PATCH", headers: authHeaders(), body: JSON.stringify({ status })
    });
    if (!r.ok) { const e = await r.json(); showToast(e.detail || "Failed", "error"); return; }
    showToast(`Appointment #${id} → ${status}`, "success");
    await loadAppointments();
  } catch { showToast("Network error.", "error"); }
}
window.updateStatus = updateStatus;

/* ── Handle successful auth ── */
async function handleAuthSuccess(auth) {
  accessToken = auth.access_token;
  currentRole = auth.role;
  currentPatientId = auth.patient_id || null;

  enterDashboard(auth.username || currentUsername, currentRole);

  try {
    await Promise.all([loadPatients(), loadDoctors()]);
  } catch {
    showToast("Some data could not be loaded.", "info");
  }
}

/* ── LOGIN ── */
loginForm.addEventListener("submit", async e => {
  e.preventDefault();
  setLoading(loginBtn, true);
  const username = document.getElementById("loginUsername").value;
  const password = document.getElementById("loginPassword").value;
  try {
    const r = await fetch(`${API_BASE}/auth/login`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!r.ok) { showToast("Login failed. Check your credentials.", "error"); return; }
    const auth = await r.json();
    currentUsername = username;
    showToast(`Welcome back, ${username}!`, "success");
    await handleAuthSuccess(auth);
  } catch { showToast("Cannot connect to the server.", "error"); }
  finally { setLoading(loginBtn, false); }
});

/* ── REGISTER ── */
registerForm.addEventListener("submit", async e => {
  e.preventDefault();
  setLoading(registerBtn, true);
  const payload = {
    username: document.getElementById("regUsername").value,
    password: document.getElementById("regPassword").value,
    full_name: document.getElementById("regFullName").value,
    age: Number(document.getElementById("regAge").value),
    phone: document.getElementById("regPhone").value,
  };
  try {
    const r = await fetch(`${API_BASE}/auth/register`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!r.ok) {
      const err = await r.json();
      showToast(err.detail || "Registration failed.", "error");
      return;
    }
    const auth = await r.json();
    currentUsername = payload.username;
    showToast(`Account created! Welcome, ${payload.username}!`, "success");
    await handleAuthSuccess(auth);
  } catch { showToast("Cannot connect to the server.", "error"); }
  finally { setLoading(registerBtn, false); }
});

/* ── LOGOUT ── */
logoutBtn.addEventListener("click", () => {
  accessToken = "";
  currentRole = "";
  currentPatientId = null;
  currentUsername = "";
  patientsCache = [];
  doctorsCache = [];

  pageDashboard.style.display = "none";
  pageAuth.style.display = "flex";
  pageAuth.style.animation = "fadeUp 400ms ease-out";

  appointmentsList.innerHTML = "";
  patientSelect.innerHTML = "";
  doctorSelect.innerHTML = "";
  selfPatient.value = "";
  loginForm.reset();
  registerForm.reset();
  loginTab.style.display = "block";
  registerTab.style.display = "none";

  showToast("Logged out successfully.", "info");
});

/* ── BOOK APPOINTMENT ── */
appointmentForm.addEventListener("submit", async e => {
  e.preventDefault();
  if (!accessToken) { showToast("Please log in first.", "error"); return; }
  setLoading(bookBtn, true);
  const patientId = currentRole === "patient" ? currentPatientId : Number(patientSelect.value);
  try {
    const r = await fetch(`${API_BASE}/appointments`, {
      method: "POST", headers: authHeaders(),
      body: JSON.stringify({
        patient_id: patientId,
        doctor_id: Number(doctorSelect.value),
        appointment_time: new Date(document.getElementById("visitTime").value).toISOString(),
        reason: document.getElementById("reason").value,
      }),
    });
    if (!r.ok) { const err = await r.json(); showToast(`Booking failed: ${err.detail || "Unknown error"}`, "error"); return; }
    const a = await r.json();
    showToast(`Appointment #${a.id} created!`, "success");
    appointmentForm.reset();
  } catch { showToast("Cannot connect to the server.", "error"); }
  finally { setLoading(bookBtn, false); }
});