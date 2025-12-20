import { capitalizeFirstLetter } from "../../../utils/text";
import { humanDateTime } from "../../../utils/numbers";
import "../../../utils/tooltips";
import * as bootstrap from "bootstrap";
import { callBackend } from "../base";

async function getLabelData() {
  const response = await callBackend("/api/v1/stats/labels", {
    method: "GET",
  });

  let jsonData = await response.json();
  let treeData = [];

  for (var i = 0; i < jsonData.length; i++) {
    let children = [];
    for (var j = 0; j < jsonData[i].categories.length; j++) {
      children.push({
        id: jsonData[i].categories[j].id,
        name: jsonData[i].categories[j].name,
      });
    }

    treeData.push({
      id: jsonData[i].id,
      name: jsonData[i].name,
      children: children,
    });
  }

  return treeData;
}

document.addEventListener("DOMContentLoaded", async () => {
  tree = new Treeview({
    containerId: "annotationTreeView",
    data: await getLabelData(),
    searchEnabled: true,
    searchPlaceholder: "Search...",
    initiallyExpanded: false,
    multiSelectEnabled: true,
    cascadeSelectChildren: true,
    onSelectionChange: (selectedNodes) => {
      const names = selectedNodes.map((n) => `"${n.name}"`);
      const label = document.getElementById("selectedLabelsTitle");
      const output = document.getElementById("selectedLabels");
      const count = names.length;
      const nodeWord = count === 1 ? "Label" : "Labels";
      label.textContent = `${count} ${nodeWord} selected:`;
      output.textContent = `[${names.join(", ")}]`;
    },
  });
});

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

async function getBatches() {
  const response = await callBackend("/api/v1/download-batches/history/", {
    method: "GET",
    credentials: "include",
  });

  if (response.status === 401) {
    throw new Error("Not authorized");
  }

  const data = await response.json();
  return data;
}

const statusTable = {
  starting: "bg-secondary",
  assembling_labels: "bg-secondary",
  assembling_images: "bg-secondary",
  adding_manifest: "bg-secondary",
  ready: "bg-success",
  failed: "bg-danger",
};

async function renderTable(clear) {
  const tableBody = document.getElementById("downloadBatchTableBody");
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
      `<td>${batches[i].image_count.toLocaleString()}</td>`,
      `<td>${condensedDate}</td>`,
      "</tr>",
      "<tr>",
      `<td colspan="5" class="p-0"><div class="collapse" id="row${i}"><div class="p-3">`,
      `<strong>Hash:</strong> ${batches[i].hash}<br />`,
      `<strong>Annotations:</strong> ${batches[i].annotations}<br />`,
      `<strong>Error:</strong> ${error_msg}`,
      '<a class="btn btn-primary" href="#" role="button>Download</a>',
      "</div></div></td></tr>",
    ].join("");
  }
}

renderTable();

// Force only numbers in input
function isNumber(evt) {
  evt = evt ? evt : window.event;
  var charCode = evt.which ? evt.which : evt.keyCode;
  if (charCode > 31 && (charCode < 48 || charCode > 57)) {
    return false;
  }
  return true;
}

function treeToSelectionMap(tree) {
  const result = [];

  for (const node of tree) {
    if (!node.children) {
      // It's not a super-category
      result.push({ id: node.id, super: false });
    }
  }

  return result;
}

document.getElementById("openDownloadModal").onclick = async function () {
  const imageCount = document.getElementById("countInput").value;
  const helpText = document.getElementById("countHelp");

  if (imageCount > 10000 || imageCount < 1) {
    helpText.classList.add("text-danger-emphasis");
  } else {
    helpText.classList.remove("text-danger-emphasis");
    new bootstrap.Modal("#confirmDownloadModal").show();
  }
};

document.getElementById("confirmDownloadBtn").onclick = async function () {
  const treeData = tree.getSelectedNodes();
  const imageCount = Number(document.getElementById("countInput").value);
  const nonMatchImg = document.getElementById("nonMatchCheck").checked;

  const selections = treeToSelectionMap(treeData);

  const body = {
    annotations: selections,
    count: imageCount,
    non_match_images: nonMatchImg,
  };

  const response = await callBackend("/api/v1/download", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  new bootstrap.Modal("#confirmDownloadModal").hide();

  renderTable(true);
};
