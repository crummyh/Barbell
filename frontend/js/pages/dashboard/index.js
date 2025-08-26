const role = document.body.dataset.role;
const section = document.body.dataset.section;
// e.g. <body data-page="dashboard" data-section="download" data-role="UserRole.DEFAULT">

switch (role) {
  case "UserRole.DEFAULT":
    switch (section) {
      case "home":
        import("./default/home.js");
        break;
      case "images":
        import("./default/images.js");
        break;
      case "upload":
        import("./default/upload.js");
        break;
      case "download":
        import("./default/download.js");
        break;
      case "settings":
        import("./default/settings.js");
        break;
    }
  case "UserRole.MODERATOR":
    switch (section) {
      case "home":
        import("./moderator/home.js");
        break;
      case "image-review":
        import("./moderator/image-review.js");
        break;
    }
  case "UserRole.ADMIN":
    switch (section) {
      case "home":
        import("./admin/home.js");
        break;
      case "labels":
        import("./admin/labels.js");
        break;
      case "ratelimit":
        import("./admin/ratelimit.js");
        break;
    }
}
