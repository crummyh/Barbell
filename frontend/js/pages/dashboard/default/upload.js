import { capitalizeFirstLetter } from "../../../utils/text";
import { formatBytes, humanDateTime } from "../../../utils/numbers";
import "../../../utils/tooltips";
import * as bootstrap from "bootstrap";
import { callBackend } from "../base";

async function getBatches() {
  const response = await callBackend("/api/v1/upload-batches/history/", {
    method: "GET",
  });

  if (response.status === 401) {
    throw new Error("Not authorized");
  }

  const data = await response.json();
  return data;
}

const statusTable = {
  uploading: "bg-secondary",
  processing: "bg-secondary",
  completed: "bg-success",
  failed: "bg-danger",
};

async function renderTable(clear) {
  const tableBody = document.getElementById("uploadBatchTableBody");
  const batches = await getBatches();

  if (batches === null) {
    return;
  }

  for (let i = 0; i < batches.length; i++) {
    const date = new Date(batches[i].start_time.replace(/\.\d+/, ""));
    let condensedDate = humanDateTime(date);

    const error_msg = batches[i].error_message;
    if (error_msg === null) {
      const error_msg = "None";
    }

    if (clear) {
      tableBody.innerHTML = "";
    }

    tableBody.innerHTML += [
      `<tr data-bs-toggle="collapse" data-bs-target="#row${i}" class="clickable">`,
      '<td class="uuid-cell">',
      `<a href="#" data-bs-toggle="tooltip" data-bs-title="${batches[i].id}" class="text-decoration-none"id="id${i}">${batches[i].id.substring(0, 6)}</a>`,
      `<button class="btn btn-sm btn-link p-0 ms-2 border-0" onclick="copyID(${i}, event)" type="button">`,
      `<iconify-icon id="copyIcon${i}" icon="bi:clipboard-fill" width="16" height="16"></iconify-icon>`,
      "</button>",
      "</td>",
      `<td><span class="badge ${statusTable[batches[i].status]} capitalize">${capitalizeFirstLetter(batches[i].status.replace("_", " "))}</span></td>`,
      `<td class="text-success-emphasis">${batches[i].images_valid.toLocaleString()}</td>`,
      `<td class="text-danger-emphasis">${batches[i].images_rejected.toLocaleString()}</td>`,
      `<td>${condensedDate}</td>`,
      "</tr>",
      "<tr>",
      `<td colspan="6" class="p-0"><div class="collapse" id="row${i}"><div class="p-3">`,
      `<strong>Images Total:</strong> ${batches[i].images_total}<br />`,
      `<strong>File Size:</strong> ${formatBytes(batches[i].file_size)}<br />`,
      `<strong>Capture Date:</strong> ${condensedDate}<br />`,
      `<strong>Error:</strong> ${error_msg}`,
      "</div></div></td></tr>",
    ].join("");
  }
}

renderTable();

function copyID(numb, event) {
  event.stopPropagation();

  const node = document.getElementById(`id${numb}`);
  navigator.clipboard.writeText(node.getAttribute("data-bs-title"));

  const copyIcon = document.getElementById(`copyIcon${numb}`);
  copyIcon.setAttribute("icon", "bi:clipboard-check-fill");

  const tooltip = new bootstrap.Tooltip(copyIcon, {
    title: "Copied!",
    trigger: "manual",
  });
  tooltip.show();

  setTimeout(() => {
    tooltip.hide();
    tooltip.dispose();
    copyIcon.setAttribute("icon", "bi:clipboard-fill");
  }, 1200);
}

window.copyID = copyID;

document.getElementById("uploadForm").addEventListener("submit", async () => {
  const hash = document.getElementById("hashInput").value;
  const date = document.getElementById("dateInput").value;
  const archive = document.getElementById("archiveInput").files[0];
});
