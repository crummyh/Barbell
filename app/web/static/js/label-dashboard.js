async function getLabelData() {
  const response = await fetch("/api/v1/stats/labels", {
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

    const response = await fetch("/internal/categories/super/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
      credentials: "include",
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

async function updateSuperCategoriesList() {
  const optionInput = document.getElementById("superCatagorySelect");
  optionInput.innerHTML = '<option value="0" selected>none</option>';

  const response = await fetch("/internal/categories/super", {
    method: "GET",
    credentials: "include",
  });
  let data = await response.json();

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

    const response = await fetch("/internal/categories/create", {
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
      const response = await fetch(
        `/internal/categories/super/remove?id=${currentSelection[i].id}`,
        {
          method: "DELETE",
          credentials: "include",
        },
      );
    } else {
      try {
        let data = { id: currentSelection[i].id };
        const response = await fetch(
          `/internal/categories/remove?id=${currentSelection[i].id}`,
          {
            method: "DELETE",
            credentials: "include",
          },
        );
      } catch {}
    }
  }
  tree.setData(await getLabelData());
};

document.getElementById("modifyBtn").onclick = function () {
  alert("hello!");
};
