const API = (window.PORTAL_API_BASE || "/api").replace(/\/$/, "").replace(/\/api$/, "");

function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstChild;
}

function setView(node) {
  const root = document.getElementById("app");
  root.innerHTML = "";
  root.appendChild(node);
}

function saveToken(t) { localStorage.setItem("token", t); }
function getToken() { return localStorage.getItem("token"); }
function clearToken() { localStorage.removeItem("token"); }

async function api(path, opts = {}) {
  const headers = opts.headers || {};
  if (!(opts.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(API + path, { ...opts, headers });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = { raw: text }; }
  if (!res.ok) throw new Error(data?.detail || "API error");
  return data;
}

// QR Code generator
function generateQRCode(text, size = 280) {
  const encoded = encodeURIComponent(text);
  return `<img src="https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${encoded}" alt="QR Code" style="max-width:100%;" />`;
}

// ============ PUBLIEKE PAGINA (geen login nodig) ============
async function publicView() {
  const node = el(`
    <div class="container">
      <div class="card header-card">
        <div class="row" style="align-items:center">
          <div>
            <h1>VasteLijn</h1>
            <p class="small">Device Owner QR Provisioning</p>
          </div>
          <div style="text-align:right">
            <button class="secondary" id="admin-btn">Admin Login</button>
          </div>
        </div>
      </div>

      <div id="content">
        <div class="card" style="text-align:center">
          <p>Laden...</p>
        </div>
      </div>
    </div>
  `);

  node.querySelector("#admin-btn").onclick = () => loginView();

  // Laad provisioning data
  try {
    const data = await api("/api/public/provisioning");
    const content = node.querySelector("#content");

    if (!data.configured) {
      content.innerHTML = `
        <div class="card" style="text-align:center">
          <h2>Nog niet geconfigureerd</h2>
          <p class="small">${data.message}</p>
          <p class="small">Klik op "Admin Login" om de APK te uploaden en configureren.</p>
        </div>
      `;
    } else {
      const qrCode = generateQRCode(data.qr_json, 300);
      const instructions = data.instructions.join("<br>");

      content.innerHTML = `
        <div class="card" style="text-align:center">
          <h2>Scan deze QR code</h2>
          <p class="small">Tijdens de Android setup (na factory reset, tik 6x op welkomstscherm)</p>
          <div class="qr-container">
            ${qrCode}
          </div>
        </div>

        <div class="card">
          <h2>Installatie instructies</h2>
          <div class="instructions">
            ${instructions}
          </div>
          <div class="warning">
            <b>Belangrijk:</b> Maak eerst een backup van foto's en contacten voordat je een factory reset doet!
          </div>
        </div>

        <div class="card">
          <h2>Problemen?</h2>
          <ul class="small troubleshoot">
            <li><b>QR scanner start niet:</b> Tik precies 6x snel achter elkaar op het welkomstscherm</li>
            <li><b>Geen WiFi optie:</b> Zorg dat WiFi aan staat op het apparaat</li>
            <li><b>Installatie mislukt:</b> Controleer de internetverbinding en probeer opnieuw</li>
            <li><b>Device Owner: false:</b> Probeer opnieuw met een verse factory reset</li>
          </ul>
        </div>

        <div class="card">
          <h2>APK Direct Downloaden</h2>
          <p class="small">Alleen voor handmatige installatie (geen Device Owner mode)</p>
          <a href="${API}/api/public/apk" class="download-btn">Download VasteLijn APK</a>
        </div>
      `;
    }
  } catch (e) {
    node.querySelector("#content").innerHTML = `
      <div class="card" style="text-align:center">
        <h2>Fout bij laden</h2>
        <p class="small" style="color:#ff6b6b">${e.message}</p>
      </div>
    `;
  }

  setView(node);
}

// ============ LOGIN PAGINA ============
function loginView() {
  const node = el(`
    <div class="container">
      <div class="card header-card">
        <div class="row" style="align-items:center">
          <div>
            <h1>VasteLijn Admin</h1>
            <p class="small">Login om APK te beheren</p>
          </div>
          <div style="text-align:right">
            <button class="secondary" id="back-btn">Terug</button>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Inloggen</h2>
        <label>Email</label>
        <input id="email" type="email" placeholder="admin@vastelijn.nl" />
        <label>Wachtwoord</label>
        <input id="pw" type="password" placeholder="••••••••" />
        <div style="height:12px"></div>
        <button id="btn">Login</button>
        <p class="small" id="err" style="margin-top:12px;color:#ff6b6b"></p>
        <p class="small">Eerste keer? Registreer via: <code>POST /api/auth/register</code></p>
      </div>
    </div>
  `);

  node.querySelector("#back-btn").onclick = () => publicView();

  node.querySelector("#btn").onclick = async () => {
    node.querySelector("#err").textContent = "";
    try {
      const email = node.querySelector("#email").value;
      const password = node.querySelector("#pw").value;
      const r = await api("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      saveToken(r.access_token);
      adminView();
    } catch (e) {
      node.querySelector("#err").textContent = e.message;
    }
  };

  node.querySelector("#pw").addEventListener("keypress", (e) => {
    if (e.key === "Enter") node.querySelector("#btn").click();
  });

  setView(node);
}

// ============ ADMIN PAGINA ============
async function adminView() {
  let config = {};
  try {
    config = await api("/api/admin/config");
  } catch (e) {
    if (e.message.includes("401") || e.message.includes("Not authenticated")) {
      clearToken();
      loginView();
      return;
    }
  }

  const node = el(`
    <div class="container">
      <div class="card header-card">
        <div class="row" style="align-items:center">
          <div>
            <h1>VasteLijn Admin</h1>
            <p class="small">APK en QR configuratie beheren</p>
          </div>
          <div style="text-align:right">
            <button class="secondary" id="public-btn">Bekijk Publieke Pagina</button>
            <button class="secondary" id="logout-btn" style="margin-left:8px">Uitloggen</button>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>APK Uploaden</h2>
        <p class="small">Upload de VasteLijn APK. De signing certificate checksum wordt automatisch berekend.</p>
        <input type="file" id="apk-file" accept=".apk" style="margin:12px 0" />
        <button id="upload-btn">Upload APK</button>
        <p class="small" id="upload-status" style="margin-top:12px"></p>
      </div>

      <div class="card">
        <h2>Huidige Configuratie</h2>

        <label>APK Download URL</label>
        <input id="apk-url" type="text" placeholder="https://jouw-domein.nl/api/public/apk" value="${config.apk_url || ''}" />
        <p class="small">Dit is de URL die in de QR code komt. Gebruik je eigen domein of de portal URL.</p>

        <label>Signing Certificate Checksum (Base64)</label>
        <input id="checksum" type="text" placeholder="ABC123...=" value="${config.checksum || ''}" />
        <p class="small">SHA-256 van het signing certificaat in Base64 formaat.</p>

        <label>Package Name</label>
        <input id="package-name" type="text" value="${config.package_name || 'com.vastelijnphone'}" />

        <label>Device Admin Receiver</label>
        <input id="admin-receiver" type="text" value="${config.admin_receiver || 'com.vastelijnphone/.admin.VasteLijnDeviceAdminReceiver'}" />

        <div style="height:12px"></div>
        <button id="save-btn">Configuratie Opslaan</button>
        <p class="small" id="save-status" style="margin-top:12px"></p>
      </div>

      <div class="card">
        <h2>Status</h2>
        <div class="status-grid">
          <div class="status-item">
            <span class="status-label">APK Bestand:</span>
            <span class="status-value ${config.apk_filename ? 'ok' : 'missing'}">${config.apk_filename || 'Niet geupload'}</span>
          </div>
          <div class="status-item">
            <span class="status-label">APK URL:</span>
            <span class="status-value ${config.apk_url ? 'ok' : 'missing'}">${config.apk_url ? 'Ingesteld' : 'Niet ingesteld'}</span>
          </div>
          <div class="status-item">
            <span class="status-label">Checksum:</span>
            <span class="status-value ${config.checksum ? 'ok' : 'missing'}">${config.checksum ? 'Ingesteld' : 'Niet ingesteld'}</span>
          </div>
          <div class="status-item">
            <span class="status-label">QR Ready:</span>
            <span class="status-value ${config.apk_url && config.checksum ? 'ok' : 'missing'}">${config.apk_url && config.checksum ? 'Ja' : 'Nee'}</span>
          </div>
        </div>
      </div>
    </div>
  `);

  node.querySelector("#logout-btn").onclick = () => { clearToken(); publicView(); };
  node.querySelector("#public-btn").onclick = () => publicView();

  // Upload handler
  node.querySelector("#upload-btn").onclick = async () => {
    const fileInput = node.querySelector("#apk-file");
    const status = node.querySelector("#upload-status");

    if (!fileInput.files.length) {
      status.textContent = "Selecteer eerst een APK bestand";
      status.style.color = "#ff6b6b";
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.textContent = "Uploaden...";
    status.style.color = "#a9b8d8";

    try {
      const result = await api("/api/admin/upload-apk", { method: "POST", body: formData });
      status.textContent = result.message;
      status.style.color = "#4CAF50";

      // Update checksum veld als berekend
      if (result.cert_checksum) {
        node.querySelector("#checksum").value = result.cert_checksum;
      }

      // Refresh de pagina na 2 seconden
      setTimeout(() => adminView(), 2000);
    } catch (e) {
      status.textContent = "Fout: " + e.message;
      status.style.color = "#ff6b6b";
    }
  };

  // Save config handler
  node.querySelector("#save-btn").onclick = async () => {
    const status = node.querySelector("#save-status");

    const body = {
      apk_url: node.querySelector("#apk-url").value || null,
      checksum: node.querySelector("#checksum").value || null,
      package_name: node.querySelector("#package-name").value || null,
      admin_receiver: node.querySelector("#admin-receiver").value || null,
    };

    status.textContent = "Opslaan...";
    status.style.color = "#a9b8d8";

    try {
      await api("/api/admin/config", { method: "PUT", body: JSON.stringify(body) });
      status.textContent = "Configuratie opgeslagen!";
      status.style.color = "#4CAF50";
      setTimeout(() => adminView(), 1500);
    } catch (e) {
      status.textContent = "Fout: " + e.message;
      status.style.color = "#ff6b6b";
    }
  };

  setView(node);
}

// ============ BOOT ============
(async function boot() {
  // Check URL hash voor admin route
  if (window.location.hash === "#admin") {
    try {
      await api("/api/me");
      adminView();
    } catch {
      loginView();
    }
  } else {
    // Altijd publieke pagina tonen
    publicView();
  }
})();
