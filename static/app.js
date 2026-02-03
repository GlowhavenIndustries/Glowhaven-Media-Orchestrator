const exportForm = document.getElementById("exportForm");
const loader = document.getElementById("loader");
const exportResult = document.getElementById("exportResult");
const csvPreview = document.getElementById("csvPreview");
const submitButton = document.getElementById("submitButton");
const exportMeta = document.getElementById("exportMeta");
const exportMessage = document.getElementById("exportMessage");
const playlistUrlInput = document.getElementById("playlistUrl");

const setLoadingState = (isLoading) => {
  if (isLoading) {
    loader.classList.remove("d-none");
    submitButton.disabled = true;
    submitButton.textContent = "Exporting...";
  } else {
    loader.classList.add("d-none");
    submitButton.disabled = false;
    submitButton.textContent = "Export to CSV";
  }
};

const updateExportMeta = (filename, lineCount) => {
  exportMeta.innerHTML = `
    <span>Filename: <strong>${filename}</strong></span>
    <span>Rows exported: <strong>${lineCount}</strong></span>
  `;
};

const setMessage = (message, type = "info") => {
  exportMessage.textContent = message;
  exportMessage.classList.remove("d-none", "error", "export-message");
  exportMessage.classList.add("export-message");
  if (type === "error") {
    exportMessage.classList.add("error");
  }
};

const clearMessage = () => {
  exportMessage.textContent = "";
  exportMessage.classList.add("d-none");
  exportMessage.classList.remove("error");
};

const markInvalid = (message) => {
  playlistUrlInput.classList.add("is-invalid");
  setMessage(message, "error");
};

const clearInvalid = () => {
  playlistUrlInput.classList.remove("is-invalid");
};

playlistUrlInput.addEventListener("input", () => {
  if (playlistUrlInput.classList.contains("is-invalid")) {
    clearInvalid();
    clearMessage();
  }
});

exportForm.addEventListener("submit", (event) => {
  event.preventDefault();
  exportResult.classList.add("d-none");
  clearMessage();
  setLoadingState(true);

  const formData = new FormData(exportForm);
  const playlistUrl = playlistUrlInput.value.trim();
  if (!playlistUrl) {
    setLoadingState(false);
    markInvalid("Please enter a Spotify playlist URL to continue.");
    return;
  }

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

      clearInvalid();
      exportResult.classList.remove("d-none");
      csvPreview.textContent = csvData;
      const lineCount = csvData.trim().split("\n").length - 1;
      updateExportMeta(filename, lineCount);
      setMessage("Export complete. Your CSV is downloading now.");

      const blob = new Blob([csvData], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const downloadLink = document.createElement("a");
      downloadLink.href = url;
      downloadLink.download = filename;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      URL.revokeObjectURL(url);
      setLoadingState(false);
    })
    .catch((error) => {
      setLoadingState(false);
      console.error("Export failed:", error);
      if (error.message !== "Server error, reloading to show flash message.") {
        setMessage("A network error occurred. Please check your connection and try again.", "error");
      }
    });
});
