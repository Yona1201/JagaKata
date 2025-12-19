document.addEventListener("DOMContentLoaded", () => {
  // Sidebar tombol mode input
  document.querySelectorAll(".side-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".side-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const mode = btn.getAttribute("data-mode");
      document.querySelectorAll(".mode-pane").forEach(p => p.classList.add("hidden"));
      document.getElementById(`mode-${mode}`).classList.remove("hidden");
      clearAll();
    });
  });

  document.getElementById("btn-detect-text")?.addEventListener("click", submitText);
  document.getElementById("btn-detect-youtube")?.addEventListener("click", submitYouTube);
  document.getElementById("btn-detect-file")?.addEventListener("click", submitFile);
});

// === Helper Loading & Error Handling ===
const loader = document.getElementById("loader");
const allButtons = document.querySelectorAll(".btn-detect");

function showLoader() {
  loader.classList.remove("hidden");
  clearOutput(); 
  allButtons.forEach(btn => btn.disabled = true);
}

function hideLoader() {
  loader.classList.add("hidden");
  allButtons.forEach(btn => btn.disabled = false);
}

function showError(mode, message) {
  const errorContainer = document.getElementById(`error-${mode}`);
  if (errorContainer) {
    errorContainer.textContent = message;
  }
}

function clearErrors() {
  document.querySelectorAll(".error-container").forEach(el => el.textContent = "");
}

// === Fungsi Submit ===
async function submitRequest(url, formData, mode) {
  clearAll();
  showLoader();
  try {
    const res = await fetch(url, { method: "POST", body: formData });
    const json = await res.json();
    if (!res.ok) {
      showError(mode, json.error || `Gagal memproses permintaan.`);
      return;
    }
    if (json.results && Array.isArray(json.results)) {
      renderResultsAndChart(json.results);
    } else {
      showError(mode, "Format respons dari server tidak sesuai.");
    }
  } catch (e) {
    showError(mode, "Terjadi kesalahan jaringan saat berkomunikasi dengan server.");
    console.error(e);
  } finally {
    hideLoader();
  }
}

async function submitText() {
  const text = document.getElementById("input-text").value.trim();
  if (!text) {
    showError("text", "Input teks tidak boleh kosong.");
    return;
  }
  const fd = new FormData();
  fd.append("text", text);
  await submitRequest("/predict/text", fd, "text");
}

async function submitYouTube() {
  const url = document.getElementById("input-youtube").value.trim();
  if (!url) {
    showError("youtube", "URL YouTube tidak boleh kosong.");
    return;
  }
  const fd = new FormData();
  fd.append("url", url);
  await submitRequest("/predict/youtube", fd, "youtube");
}

async function submitFile() {
  const file = document.getElementById("input-file").files[0];
  if (!file) {
    showError("file", "Pilih file terlebih dahulu.");
    return;
  }
  const fd = new FormData();
  fd.append("file", file);
  await submitRequest("/predict/file", fd, "file");
}

// === Fungsi CSV ===
function convertToCSV(data) {
  const headers = "Teks,HS,Target,Kategori,Level\n";
  const rows = data.map(row => {
    const text = `"${(row.text || '').replace(/"/g, '""')}"`;
    const hs = row.HS || 'Tidak';
    const target = row.Target || '-';
    const kategori = row.Kategori || '-';
    const level = row.Level || '-';
    return [text, hs, target, kategori, level].join(',');
  }).join('\n');
  return headers + rows;
}

function downloadCSV(csvContent, fileName = 'predictions.csv') {
  const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", fileName);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

// === Render & Clear Functions ===
function renderResultsAndChart(results) {
  const tableContainer = document.getElementById("tableContainer");
  const chartContainer = document.getElementById("chartContainer");

  if (!results || results.length === 0) {
    tableContainer.innerHTML = "<p>Tidak ada hasil yang terdeteksi.</p>";
    if (chartContainer) chartContainer.classList.add("hidden");
    return;
  }

  // Render tabel terlebih dahulu untuk menstabilkan layout
  const keys = ["text", "HS", "Target", "Kategori", "Level"];
  const headers = {"text": "Teks", "HS": "HS", "Target": "Target", "Kategori": "Kategori", "Level": "Level"};
  
  let tableHTML = "<table class='result-table'><thead><tr>";
  keys.forEach(k => tableHTML += `<th>${headers[k]}</th>`);
  tableHTML += "</tr></thead><tbody>";

  results.forEach(r => {
    tableHTML += "<tr>";
    keys.forEach(k => {
      const val = r[k] || "-";
      tableHTML += `<td>${val}</td>`;
    });
    tableHTML += "</tr>";
  });
  tableHTML += "</tbody></table>";
  tableContainer.innerHTML = tableHTML;

  const btnHTML = `<button id="btn-download-csv" class="btn-primary btn-secondary" style="margin-top:15px;">Download CSV</button>`;
  tableContainer.insertAdjacentHTML("beforeend", btnHTML);

  document.getElementById("btn-download-csv").addEventListener("click", () => {
    const csvData = convertToCSV(results);
    downloadCSV(csvData);
  });
  
  let hsCount = 0;
  let nonHsCount = 0;
  results.forEach(r => {
    if (r.HS === "Ya") hsCount++;
    else nonHsCount++;
  });
  const chart_data = {
    labels: ["Hate Speech", "Bukan Hate Speech"],
    values: [hsCount, nonHsCount]
  };

  setTimeout(() => {
    if (chartContainer) chartContainer.classList.remove("hidden");
    const ctx = document.getElementById("chartCanvas").getContext("2d");
    if (window._jagaChart) {
      window._jagaChart.destroy();
    }
    window._jagaChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: chart_data.labels,
        datasets: [{
          data: chart_data.values,
          backgroundColor: ['#f44336', '#4caf50'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom"
          }
        }
      }
    });
  }, 0);
}

function clearOutput() {
  const tableContainer = document.getElementById("tableContainer");
  const chartContainer = document.getElementById("chartContainer");
  tableContainer.innerHTML = "<p>Belum ada hasil.</p>";
  if(chartContainer) chartContainer.classList.add("hidden");
  if (window._jagaChart) {
    window._jagaChart.destroy();
    window._jagaChart = null;
  }
}

function clearAll() {
  clearOutput();
  clearErrors();
}

