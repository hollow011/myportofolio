"use strict";

(() => {
  const app = document.getElementById("education-app");
  if (!app) return;
  const grid = document.getElementById("education-grid");
  const search = document.getElementById("institution-search");
  const form = document.getElementById("education-form");
  const modal = document.getElementById("add-education-modal");
  const token = document.querySelector("#education-csrf input").value;
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

  function buildEducationCardElement(item) {
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(item.pk)) {
      throw new Error("Invalid education identifier");
    }
    const education = item.fields;
    const detailUrl = app.dataset.detailUrl.replace(UUID, item.pk);
    const card = element("article", undefined, "project-card");
    const header = element("div", undefined, "project-card-header");
    header.append(element("span", education.degree_display, "project-technology"));
    if (education.is_current) header.append(element("span", "Current", "featured-badge"));
    const heading = element("h2");
    heading.append(link(education.institution, detailUrl));
    const actions = element("div", undefined, "project-actions");
    actions.append(link("View details", detailUrl));
    const website = safeUrl(education.website);
    if (website) actions.append(link("Institution website", website));

    const starText = app.dataset.authenticated === "true"
      ? (education.is_starred ? "★ Unstar " : "★ Star ") : "Log in to star ";
    const star = element("button", starText, "button button-star");
    star.type = "submit";
    star.classList.toggle("is-starred", education.is_starred);
    star.setAttribute("aria-pressed", String(education.is_starred));
    star.title = education.star_count ? "Starred by " + education.starred_by_names : "Be the first to star";
    star.append(element("span", education.star_count, "star-count"));
    actions.append(postForm(app.dataset.starUrl.replace(UUID, item.pk), star));
    if (app.dataset.canEdit === "true") {
      actions.append(link("Edit education", app.dataset.editUrl.replace(UUID, item.pk)));
    }
    if (app.dataset.canDelete === "true") {
      const remove = element("button", "Delete education", "button button-danger");
      remove.type = "submit";
      const deletion = postForm(app.dataset.deleteUrl.replace(UUID, item.pk), remove);
      deletion.addEventListener("submit", event => {
        if (!window.confirm('Delete "' + education.institution + '"? This cannot be undone.')) event.preventDefault();
      });
      actions.append(deletion);
    }
    card.append(header, heading, element("p", education.field_of_study, "education-subject"));
    if (education.description) card.append(element("p", education.description, "education-description"));
    card.append(actions);
    return card;
  }

  function displayPageSection(state) {
    for (const name of ["loading", "error", "empty", "grid"]) {
      document.getElementById("education-" + name).hidden = name !== state;
    }
    grid.setAttribute("aria-busy", String(state === "loading"));
    document.getElementById("education-results").hidden = state !== "grid";
  }

  async function fetchEducation() {
    const current = ++revision;
    if (controller) controller.abort();
    controller = new AbortController();
    const query = search.value.trim();
    displayPageSection("loading");
    try {
      const url = new URL(app.dataset.listUrl, window.location.href);
      if (query) url.searchParams.set("institution", query);
      const response = await fetch(url, {
        headers: { Accept: "application/json" },
        credentials: "same-origin",
        signal: controller.signal,
        cache: "no-store",
      });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const entries = await response.json();
      if (current !== revision) return;
      if (!Array.isArray(entries)) throw new Error("Invalid response");
      // Build first; a malformed response never leaves partially rendered results.
      const cards = entries.map(buildEducationCardElement);
      grid.replaceChildren(...cards);
      document.getElementById("education-empty").textContent = query
        ? 'No education matches "' + query + '".' : "No education added yet.";
      document.getElementById("education-results").textContent = cards.length + " education " + (cards.length === 1 ? "entry" : "entries") + " found.";
      document.getElementById("education-json-link").href = url.href;
      displayPageSection(cards.length ? "grid" : "empty");
    } catch (error) {
      if (error.name === "AbortError" || current !== revision) return;
      displayPageSection("error");
    }
  }

  function searchEducation() {
    clearTimeout(debounce);
    const url = new URL(window.location.href);
    if (search.value.trim()) url.searchParams.set("institution", search.value.trim());
    else url.searchParams.delete("institution");
    window.history.replaceState(null, "", url);
    fetchEducation();
  }
  search.addEventListener("input", () => {
    clearTimeout(debounce);
    // Invalidate immediately, even during the debounce window.
    revision++;
    if (controller) controller.abort();
    debounce = setTimeout(searchEducation, 300);
  });
  document.getElementById("education-search-form").addEventListener("submit", event => {
    event.preventDefault();
    searchEducation();
  });
  document.getElementById("clear-education-search").addEventListener("click", () => {
    search.value = "";
    searchEducation();
    search.focus();
  });
  document.getElementById("retry-education").addEventListener("click", searchEducation);

  if (form) {
    // Older browsers retain the standalone form rather than a non-working button.
    if (typeof modal.showPopover !== "function") {
      document.querySelector('[popovertarget="add-education-modal"]').addEventListener("click", () => {
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
      const feedback = document.getElementById("education-form-error");
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
        // A login redirect or malformed success must not be treated as a saved row.
        if (response.redirected || response.status !== 201 || !result.pk) {
          throw new Error("Unexpected server response. Reload the page before trying again.");
        }
        form.reset();
        modal.hidePopover();
        showToast("Education added", "Your education entry was saved. The current search filter still applies.", "success");
        clearTimeout(debounce);
        fetchEducation();
      } catch (error) {
        feedback.textContent = error.message || "Unable to connect. Please try again.";
        feedback.hidden = false;
        showToast("Could not add education", feedback.textContent, "error", 6000);
      } finally {
        submit.disabled = false;
      }
    });
  }
  fetchEducation();
})();
