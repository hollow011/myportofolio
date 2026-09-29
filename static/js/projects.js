"use strict";

(() => {
  const app = document.getElementById("projects-app");
  if (!app) return;
  const grid = document.getElementById("projects-grid");
  const search = document.getElementById("project-title-search");
  const form = document.getElementById("project-form");
  const modal = document.getElementById("add-project-modal");
  const token = document.querySelector("#project-csrf input").value;
  let controller;
  let revision = 0;
  let debounce;
  const UUID = "00000000-0000-0000-0000-000000000000";

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  // Text never enters innerHTML. Restrict URLs too: escaping cannot stop javascript:.
  function safeUrl(value) {
    try {
      const url = new URL(value);
      return ["https:", "http:"].includes(url.protocol) ? url.href : "";
    } catch { return ""; }
  }

  function link(label, href) {
    const node = element("a", label);
    node.href = href;
    return node;
  }

  function postForm(url, button) {
    const node = element("form");
    node.method = "post";
    node.action = url;
    const csrf = element("input");
    csrf.type = "hidden";
    csrf.name = "csrfmiddlewaretoken";
    csrf.value = token;
    node.append(csrf, button);
    return node;
  }

  function buildProjectCardElement(item) {
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(item.pk)) {
      throw new Error("Invalid project identifier");
    }
    const project = item.fields;
    const detailUrl = app.dataset.detailUrl.replace(UUID, item.pk);
    const card = element("article", undefined, "project-card");
    if (project.is_featured) card.classList.add("project-card--featured");
    const imageUrl = safeUrl(project.project_image_url);
    if (imageUrl) {
      const image = element("img", undefined, "project-image");
      image.src = imageUrl;
      image.alt = "Preview of " + project.title;
      image.loading = "lazy";
      image.referrerPolicy = "no-referrer";
      card.append(image);
    }
    const header = element("div", undefined, "project-card-header");
    header.append(element("span", project.technology, "project-technology"));
    if (project.is_featured) header.append(element("span", "Featured", "featured-badge"));
    const heading = element("h2");
    heading.append(link(project.title, detailUrl));
    const actions = element("div", undefined, "project-actions");
    actions.append(link("View details", detailUrl));
    const sourceUrl = safeUrl(project.repository_url);
    if (sourceUrl) actions.append(link("Source code", sourceUrl));

    const star = element("button", project.is_starred ? "★ Unstar " : "★ Star ", "button button-star");
    star.type = "submit";
    star.classList.toggle("is-starred", project.is_starred);
    star.setAttribute("aria-pressed", String(project.is_starred));
    star.title = project.star_count ? "Starred by " + project.starred_by_names : "Be the first to star";
    star.append(element("span", project.star_count, "star-count"));
    actions.append(postForm(app.dataset.starUrl.replace(UUID, item.pk), star));

    if (app.dataset.isOwner === "true") {
      const remove = element("button", "Delete", "button button-danger");
      remove.type = "submit";
      const deletion = postForm(app.dataset.deleteUrl.replace(UUID, item.pk), remove);
      deletion.addEventListener("submit", event => {
        if (!window.confirm('Delete "' + project.title + '"? This cannot be undone.')) event.preventDefault();
      });
      actions.append(deletion);
    }
    card.append(header, heading, element("p", project.description), actions);
    return card;
  }

  function displayPageSection(state) {
    for (const name of ["loading", "error", "empty", "grid"]) {
      document.getElementById("projects-" + name).hidden = name !== state;
    }
    grid.setAttribute("aria-busy", String(state === "loading"));
  }

  async function fetchProjects() {
    const current = ++revision;
    if (controller) controller.abort();
    controller = new AbortController();
    const query = search.value.trim();
    displayPageSection("loading");
    try {
      const url = new URL(app.dataset.listUrl, window.location.href);
      if (query) url.searchParams.set("title", query);
      const response = await fetch(url, {
        headers: { Accept: "application/json" },
        credentials: "same-origin",
        signal: controller.signal,
        cache: "no-store",
      });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const projects = await response.json();
      if (current !== revision) return;
      if (!Array.isArray(projects)) throw new Error("Invalid response");
      // Build first; a malformed response never leaves partially rendered results.
      const cards = projects.map(buildProjectCardElement);
      grid.replaceChildren(...cards);
      document.getElementById("projects-empty").textContent = query
        ? 'No projects match "' + query + '".' : "No projects added yet.";
      displayPageSection(cards.length ? "grid" : "empty");
    } catch (error) {
      if (error.name === "AbortError" || current !== revision) return;
      displayPageSection("error");
    }
  }

  function searchProjects() {
    clearTimeout(debounce);
    const url = new URL(window.location.href);
    if (search.value.trim()) url.searchParams.set("title", search.value.trim());
    else url.searchParams.delete("title");
    window.history.replaceState(null, "", url);
    fetchProjects();
  }
  search.addEventListener("input", () => {
    clearTimeout(debounce);
    // Invalidate immediately, even during the debounce window.
    revision++;
    if (controller) controller.abort();
    debounce = setTimeout(searchProjects, 300);
  });
  document.getElementById("project-search-form").addEventListener("submit", event => {
    event.preventDefault();
    searchProjects();
  });
  document.getElementById("clear-search").addEventListener("click", () => {
    search.value = "";
    searchProjects();
    search.focus();
  });
  document.getElementById("retry-projects").addEventListener("click", searchProjects);

  if (form) {
    // Older browsers retain the standalone form rather than a non-working button.
    if (typeof modal.showPopover !== "function") {
      document.querySelector('[popovertarget="add-project-modal"]').addEventListener("click", () => {
        window.location.assign(form.action);
      });
    }
    modal.addEventListener("toggle", event => {
      if (event.newState === "open") form.querySelector('input:not([type="hidden"])').focus();
    });
    form.addEventListener("submit", async event => {
      event.preventDefault();
      const submit = form.querySelector('[type="submit"]');
      if (submit.disabled) return;
      submit.disabled = true;
      const feedback = document.getElementById("project-form-error");
      feedback.hidden = true;
      try {
        const response = await fetch(app.dataset.createUrl, {
          method: "POST",
          credentials: "same-origin",
          headers: { "X-CSRFToken": token, Accept: "application/json" },
          body: new FormData(form),
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) {
          const message = result.errors
            ? Object.values(result.errors).flat().map(error => error.message).join(" ")
            : result.message || "Request failed (HTTP " + response.status + "). Please reload if your session expired.";
          throw new Error(message);
        }
        form.reset();
        modal.hidePopover();
        showToast("Project added", "Your project was saved. The current search filter still applies.", "success");
        clearTimeout(debounce);
        fetchProjects();
      } catch (error) {
        feedback.textContent = error.message || "Unable to connect. Please try again.";
        feedback.hidden = false;
        showToast("Could not add project", feedback.textContent, "error", 6000);
      } finally {
        submit.disabled = false;
      }
    });
  }
  fetchProjects();
})();
