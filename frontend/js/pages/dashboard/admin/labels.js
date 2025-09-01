import { callBackend } from "../base";

async function getLabelData() {
  const response = await callBackend(
    "/api/v1/stats/labels",
    {
      method: "GET",
    },
    {
      500: {
        title: "Error getting catagory data",
        body: 'Try again later, or <a href="https://github.com/crummyh/Barbell/issues">submit and issue</a>',
      },
    },
  );

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
    containerId: "labelTreeView",
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

document
  .getElementById("labelSuperCatagoryForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = document.getElementById("superCatagoryName").value;
    const data = { name: name };

    const response = await callBackend("/internal/categories/super/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const output = document.getElementById("superCatagoryOutput");

    if (response.status !== 200) {
      output.innerHTML = "An error occurred. Check console";
      console.error(await response.json());
    } else {
      output.innerHTML = "Created!";
      updateSuperCategoriesList();
      tree.setData(await getLabelData());
    }
  });

async function getSuperCategoriesList() {
  const response = await callBackend("/internal/categories/super", {
    method: "GET",
  });
  let data = await response.json();
  return data;
}

async function updateSuperCategoriesList() {
  const optionInput = document.getElementById("superCatagorySelect");
  optionInput.innerHTML = '<option value="0" selected>none</option>';

  let data = await getSuperCategoriesList();

  for (var i = 0; i < data.length; i++) {
    optionInput.innerHTML += `<option value="${data[i].id}">${data[i].name}</option>`;
  }
}
updateSuperCategoriesList();

document
  .getElementById("labelCatagoryForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const name = document.getElementById("catagoryName").value;
    const superCatagory = document.getElementById("superCatagorySelect").value;

    let data;

    if (superCatagory === "0") {
      data = { name: name };
    } else {
      data = {
        name: name,
        super_category_id: superCatagory,
      };
    }

    const response = await callBackend("/internal/categories/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
      credentials: "include",
    });

    const output = document.getElementById("catagoryOutput");

    if (response.status !== 200) {
      output.innerHTML = "An error occurred. Check console";
      console.error(await response.json());
    } else {
      output.innerHTML = "Created!";
      tree.setData(await getLabelData());
    }
  });

document.getElementById("deleteBtn").onclick = async function () {
  let currentSelection = tree.getSelectedNodes();

  for (var i = 0; i < currentSelection.length; i++) {
    if (Object.hasOwn(currentSelection[i], "children")) {
      const response = await callBackend(
        `/internal/categories/super/remove?id=${currentSelection[i].id}`,
        {
          method: "DELETE",
        },
      );
    } else {
      try {
        const response = await callBackend(
          `/internal/categories/remove?id=${currentSelection[i].id}`,
          {
            method: "DELETE",
          },
        );
      } catch {}
    }
  }
  tree.setData(await getLabelData());
};

document.getElementById("modifyBtn").onclick = async function () {
  let currentSelection = tree.getSelectedNodes();

  if (
    currentSelection.length > 1 &&
    !Object.hasOwn(currentSelection[0], "children")
  ) {
    const modifyOutput = document.getElementById("modifyOutput");
    modifyOutput.innerHTML = "Only select 1 catagory or super catagory";
  } else {
    const modalForm = document.getElementById("modifyModalBody");

    if (Object.hasOwn(currentSelection[0], "children")) {
      modalForm.innerHTML = [
        '<div class="mb-3">',
        '<label for="newNameInput" class="form-label">New Name</label>',
        `<input type="text" class="form-control" id="newNameInput" placeholder="${currentSelection[0].name}">`,
        "</div>",
      ].join("");
    } else {
      modalData = [
        '<div class="mb-3">',
        '<label for="newNameInput" class="form-label">New Name</label>',
        `<input type="text" class="form-control" id="newNameInput" placeholder="${currentSelection[0].name}">`,
        "</div>",
        '<div class="mb-3">',
        '<label for="superCatOption" class="form-label">Super Catagory</label>',
        '<select class="form-select" id="superCatOption">',
        '<option value="0" selected>...</option>',
      ];

      let superCategories = await getSuperCategoriesList();
      for (var i = 0; i < superCategories.length; i++) {
        modalData.push(
          `<option value="${superCategories[i].id}">${superCategories[i].name}</option>`,
        );
      }
      modalData.push("</select");
      modalForm.innerHTML = modalData.join("");
    }

    new bootstrap.Modal("#modifyModal").show();
  }
};

document.getElementById("modifySaveBtn").onclick = async function () {
  let currentSelection = tree.getSelectedNodes();
  const newName = document.getElementById("newNameInput").value;

  if (Object.hasOwn(currentSelection[0], "children")) {
    const response = await callBackend(
      `/internal/categories/super/modify?id=${currentSelection[0].id}&new_name=${newName}`,
      {
        method: "PUT",
      },
    );
  } else {
    const newSuperCat = document.getElementById("superCatOption").value;
    const response = await callBackend(
      `/internal/categories/modify?id=${currentSelection[0].id}&new_name=${newName}&new_super_cat=${newSuperCat}`,
      {
        method: "PUT",
      },
    );
  }
  new bootstrap.Modal("#modifyModal").hide();
  tree.setData(await getLabelData());
};
