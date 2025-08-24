class ImageSelector {
  constructor(selector, onSelectCallback = null) {
    this.images = Array.from(document.querySelectorAll(selector));
    this.selected = new Set();
    this.lastClickedIndex = null;
    this.onSelectCallback = onSelectCallback;

    this.images.forEach((img, index) => {
      img.addEventListener("click", (e) => this.handleClick(e, index));
    });

    // Global keyboard listener
    document.addEventListener("keydown", (e) => this.handleKey(e));
  }

  handleClick(event, index) {
    const img = this.images[index];
    const id = img.id;

    if (event.shiftKey && this.lastClickedIndex !== null) {
      // SHIFT = select range
      const [start, end] = [this.lastClickedIndex, index].sort((a, b) => a - b);
      for (let i = start; i <= end; i++) {
        this.select(this.images[i].id);
      }
    } else if (event.ctrlKey || event.metaKey) {
      // CTRL/CMD = toggle
      if (this.selected.has(id)) {
        this.deselect(id);
      } else {
        this.select(id);
      }
      this.lastClickedIndex = index;
    } else {
      // Normal click = single select
      this.clear();
      this.select(id);
      this.lastClickedIndex = index;
    }

    this.triggerCallback();
  }

  handleKey(event) {
    // Ctrl+A / Cmd+A = select all
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "a") {
      event.preventDefault(); // prevent "select all text"
      this.selectAll();
      this.triggerCallback();
    }

    // Escape = clear selection
    if (event.key === "Escape") {
      this.clear();
      this.triggerCallback();
    }
  }

  select(id) {
    const img = document.getElementById(id);
    if (img) {
      img.classList.add("selected");
      this.selected.add(id);
    }
  }

  deselect(id) {
    const img = document.getElementById(id);
    if (img) {
      img.classList.remove("selected");
      this.selected.delete(id);
    }
  }

  clear() {
    this.selected.forEach((id) => {
      const img = document.getElementById(id);
      if (img) img.classList.remove("selected");
    });
    this.selected.clear();
  }

  selectAll() {
    this.images.forEach((img) => {
      this.select(img.id);
    });
  }

  getSelected() {
    return Array.from(this.selected);
  }

  triggerCallback() {
    if (this.onSelectCallback) {
      this.onSelectCallback(this.getSelected());
    }
  }
}

const selector = new ImageSelector(".img-selectable", (selected) => {
  console.log("Selected images:", selected);
});
