export default function initTabSwitches() {
  document.querySelectorAll(".code-switch").forEach((container) => {
    const options = JSON.parse(container.dataset.options);
    const tabList = document.createElement("ul");
    tabList.className = "nav nav-tabs";
    const content = document.createElement("div");
    content.className = "tab-content";

    options.forEach((opt, i) => {
      // Tab button
      const li = document.createElement("li");
      li.className = "nav-item";
      const button = document.createElement("button");
      button.className = "nav-link" + (i === 0 ? " active" : "");
      button.id = opt.id + "-tab";
      button.dataset.bsToggle = "tab";
      button.dataset.bsTarget = "#" + opt.id + "-pane";
      button.type = "button";
      button.role = "tab";
      button.ariaControls = opt.id + "-pane";
      button.ariaSelected = i === 0 ? "true" : "false";
      button.textContent = opt.label;
      li.appendChild(button);
      tabList.appendChild(li);

      // Tab content
      const pane = document.createElement("div");
      pane.className = "tab-pane fade" + (i === 0 ? " show active" : "");
      pane.id = opt.id + "-pane";
      pane.role = "tabpanel";
      pane.tabIndex = 0;
      pane.innerHTML = `<pre><code class="language-md">${opt.code}</code></pre>`;
      content.appendChild(pane);
    });

    container.appendChild(tabList);
    container.appendChild(content);
  });
}
