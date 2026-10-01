const exportForm = document.getElementById("exportForm");
const loader = document.getElementById("loader");
const exportPlaceholder = document.getElementById("exportPlaceholder");
const exportResult = document.getElementById("exportResult");
const csvPreview = document.getElementById("csvPreview");
const submitButton = document.getElementById("submitButton");
const exportMeta = document.getElementById("exportMeta");
const exportStatusBadge = document.getElementById("exportStatusBadge");
const resultMeta = document.getElementById("resultMeta");
const downloadAgainBtn = document.getElementById("downloadAgainBtn");

let lastExportedCsvData = null;
let lastExportedFilename = "playlist.csv";

const setLoadingState = (isLoading) => {
  if (isLoading) {
    loader.classList.remove("d-none");
    submitButton.disabled = true;
    submitButton.innerHTML = `
      <span class="cmd-spinner me-2" style="width: 14px; height: 14px; border-width: 2px;"></span>
      <span>Orchestrating Export...</span>
    `;
    if (exportStatusBadge) {
      exportStatusBadge.className = "badge-status warning";
      exportStatusBadge.innerHTML = `<span class="status-dot"></span> Processing API Request`;
    }
  } else {
    loader.classList.add("d-none");
    submitButton.disabled = false;
    submitButton.innerHTML = `<span>Run Metadata Export</span>`;
  }
};

const updateExportMeta = (filename, lineCount) => {
  exportMeta.textContent = "";

  const filenameSpan = document.createElement("span");
  filenameSpan.className = "me-3";
  filenameSpan.innerHTML = `File: <strong class="text-primary">${filename}</strong>`;

  const rowsSpan = document.createElement("span");
  rowsSpan.innerHTML = `Rows: <strong class="text-primary">${lineCount}</strong>`;

  exportMeta.appendChild(filenameSpan);
  exportMeta.appendChild(rowsSpan);

  if (resultMeta) {
    resultMeta.innerHTML = `Generated <strong class="text-primary">${filename}</strong> (${lineCount} records exported)`;
  }
};

const triggerFileDownload = (csvData, filename) => {
  const blob = new Blob([csvData], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const downloadLink = document.createElement("a");
  downloadLink.href = url;
  downloadLink.download = filename;
  document.body.appendChild(downloadLink);
  downloadLink.click();
  document.body.removeChild(downloadLink);
  URL.revokeObjectURL(url);
};

if (downloadAgainBtn) {
  downloadAgainBtn.addEventListener("click", () => {
    if (lastExportedCsvData) {
      triggerFileDownload(lastExportedCsvData, lastExportedFilename);
    }
  });
}

if (exportForm) {
  exportForm.addEventListener("submit", (event) => {
    event.preventDefault();

    if (exportPlaceholder) {
      exportPlaceholder.classList.add("d-none");
    }
    setLoadingState(true);

    const formData = new FormData(exportForm);
    fetch(exportForm.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          window.location.reload();
          return Promise.reject(new Error("Server error, reloading to show flash message."));
        }

        const contentDisposition = response.headers.get("content-disposition");
        let filename = "playlist.csv";
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename\*?=(?:UTF-8'')?([^;]+)/);
          if (filenameMatch && filenameMatch.length > 1) {
            filename = decodeURIComponent(filenameMatch[1].replace(/"/g, ""));
          }
        }

        return Promise.all([response.text(), filename]);
      })
      .then(([csvData, filename]) => {
        if (!csvData) {
          setLoadingState(false);
          return;
        }

        lastExportedCsvData = csvData;
        lastExportedFilename = filename;

        exportResult.classList.remove("d-none");
        exportResult.classList.add("d-flex");
        csvPreview.textContent = csvData;

        const lineCount = Math.max(0, csvData.trim().split("\n").length - 1);
        updateExportMeta(filename, lineCount);

        if (exportStatusBadge) {
          exportStatusBadge.className = "badge-status active";
          exportStatusBadge.innerHTML = `<span class="status-dot"></span> Complete (${lineCount} Rows)`;
        }

        triggerFileDownload(csvData, filename);
        setLoadingState(false);
      })
      .catch((error) => {
        setLoadingState(false);
        if (exportStatusBadge) {
          exportStatusBadge.className = "badge-status danger";
          exportStatusBadge.innerHTML = `<span class="status-dot"></span> Export Failed`;
        }
        console.error("Export failed:", error);
        if (error.message !== "Server error, reloading to show flash message.") {
          alert("A network error occurred. Please check your connection and try again.");
        }
      });
  });
}
