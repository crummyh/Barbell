async function getLabels() {
  const response = await fetch("/api/v1/stats/labels", {
    method: "GET",
  });

  const data = await response.json();
  console.log(data);
  return data;
}

getLabels();

const tempTreeData = [
  {
    id: "1",
    name: "2025",
    children: [
      {
        id: "1.1",
        name: "coral",
      },
      {
        id: "1.2",
        name: "algae",
      },
    ],
  },
  {
    id: "2",
    name: "2024",
    children: [
      {
        id: "2.1",
        name: "note",
      },
    ],
  },
  {
    id: "3",
    name: "2023",
    children: [
      {
        id: "3.1",
        name: "cube",
      },
      {
        id: "3.2",
        name: "cone",
      },
    ],
  },
];

const treeViewContainer = document.getElementById("annotationTreeView");

const tree = new Treeview({
  containerId: "annotationTreeView",
  data: tempTreeData,
  searchEnabled: true,
  searchPlaceholder: "Search...",
  initiallyExpanded: false,
  multiSelectEnabled: true,
  cascadeSelectChildren: true,
  onSelectionChange: (selectedNodesData) => {
    console.log("Selected Nodes:", selectedNodesData);
  },
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

async function getBatches() {
  const response = await fetch("/internal/download-batches/history/", {
    method: "GET",
    credentials: "include",
  });

  if (response.status === 401) {
    throw new Error("Not authorized");
  }

  const data = await response.json();
  console.log(data);
  return data;
}

function capitalizeFirstLetter(val) {
  return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

const statusTable = {
  starting: "bg-secondary",
  assembling_labels: "bg-secondary",
  assembling_images: "bg-secondary",
  adding_manifest: "bg-secondary",
  ready: "bg-success",
  failed: "bg-danger",
};

async function renderTable() {
  const tableBody = document.getElementById("downloadBatchTableBody");
  const batches = await getBatches();

  if (batches === null) {
    return;
  }

  for (let i = 0; i < batches.length; i++) {
    const date = new Date(batches[i].start_time.replace(/\.\d+/, ""));

    let dd = String(date.getDate()).padStart(2, "0");
    let mm = String(date.getMonth() + 1).padStart(2, "0");
    let yy = String(date.getFullYear()).slice(-2);
    let hh = String(date.getHours()).padStart(2, "0");
    let min = String(date.getMinutes()).padStart(2, "0");
    let sec = String(date.getSeconds()).padStart(2, "0");

    let condensedDate = `${dd}-${mm}-${yy} ${hh}:${min}:${sec}`;

    const error_msg = batches[i].error_message;
    if (error_msg === null) {
      const error_msg = "None";
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
// getLabels();
