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

const treeViewContainer = document.getElementById("labelTreeView");

const tree = new Treeview({
  containerId: "labelTreeView",
  data: tempTreeData,
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
