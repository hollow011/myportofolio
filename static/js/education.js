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
  let editing = null;
  const fields = ["institution", "degree", "field_of_study", "description", "website", "is_current"];
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

  async function write(url, method, expected, payload) {
    const response = await fetch(url, {
      method, credentials: "same-origin",
      headers: { "X-CSRFToken": token, Accept: "application/json", "Content-Type": "application/json" },
      body: payload === undefined ? undefined : JSON.stringify(payload),
    });
    if (response.status === 204 && expected === 204) return;
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = Object.entries(data).map(([field, errors]) =>
        field === "detail" ? errors : field + ": " + [].concat(errors).join(" ")
      ).join(" ");
      throw new Error(message || "Request failed (HTTP " + response.status + "). Please try again.");
    }
    if (response.redirected || response.status !== expected || !data.id) {
      throw new Error("Unexpected server response. Reload before trying again.");
    }
  }

  async function changeRow(button, endpoint, method, status, message) {
    if (button.disabled) return;
    button.disabled = true;
    try {
      await write(endpoint, method, status);
      showToast("Education", message, "success");
      await fetchEducation();
    } catch (error) {
      showToast("Request failed", error.message, "error");
    } finally { button.disabled = false; }
  }

  function buildEducationCardElement(education) {
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(education.id)) {
      throw new Error("Invalid education identifier");
    }
    const detailUrl = app.dataset.detailUrl.replace(UUID, education.id);
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

    if (app.dataset.authenticated === "true") {
      const star = element("button", education.is_starred ? "★ Unstar " : "★ Star ", "button button-star");
      star.type = "button";
      star.classList.toggle("is-starred", education.is_starred);
      star.setAttribute("aria-pressed", String(education.is_starred));
      star.title = education.star_count ? "Starred by " + education.starred_by_names : "Be the first to star";
      star.append(element("span", education.star_count, "star-count"));
      star.addEventListener("click", () => changeRow(star, app.dataset.starUrl.replace(UUID, education.id), "POST", 200, "Star updated."));
      actions.append(star);
    } else {
      actions.append(link("Log in to star (" + education.star_count + ")", app.dataset.loginUrl));
    }
    if (app.dataset.canEdit === "true") {
      const edit = link("Edit education", app.dataset.editUrl.replace(UUID, education.id));
      if (typeof modal.showPopover === "function") edit.addEventListener("click", event => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        if (form.querySelector('[type="submit"]').disabled) return;
        prepareForm(education);
        modal.showPopover();
      });
      actions.append(edit);
    }
    if (app.dataset.canDelete === "true") {
      const remove = element("button", "Delete education", "button button-danger");
      remove.type = "button";
      remove.addEventListener("click", () => {
        if (window.confirm('Delete "' + education.institution + '"? This cannot be undone.')) {
          return changeRow(remove, app.dataset.apiDetailUrl.replace(UUID, education.id), "DELETE", 204, "Education deleted.");
        }
      });
      actions.append(remove);
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
      url.searchParams.set("format", "json");
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

  function prepareForm(entry) {
    if (editing || entry) {
      form.reset();
      document.getElementById("education-form-error").hidden = true;
    }
    editing = entry;
    if (entry) for (const name of fields) {
      const input = form.elements.namedItem(name);
      if (input.type === "checkbox") input.checked = entry[name];
      else input.value = entry[name];
    }
    document.getElementById("add-education-title").textContent = entry ? "Edit education" : "Add education";
    form.querySelector('[type="submit"]').textContent = entry ? "Save changes" : "Add education";
  }

  if (form) {
    const add = document.querySelector('button[popovertarget="add-education-modal"]:not([popovertargetaction])');
    if (add) add.addEventListener("click", event => {
      if (form.querySelector('[type="submit"]').disabled) { event.preventDefault(); return; }
      if (typeof modal.showPopover !== "function") window.location.assign(form.action);
      else prepareForm(null);
    });
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
        const payload = {};
        for (const name of fields) {
          const input = form.elements.namedItem(name);
          const value = input.type === "checkbox" ? input.checked : input.value;
          if (!editing || value !== editing[name]) payload[name] = value;
        }
        if (editing) await write(app.dataset.apiDetailUrl.replace(UUID, editing.id), "PATCH", 200, payload);
        else await write(app.dataset.listUrl, "POST", 201, payload);
        const title = editing ? "Education updated" : "Education added";
        editing = null;
        form.reset();
        modal.hidePopover();
        showToast(title, "Your education entry was saved. The current search filter still applies.", "success");
        clearTimeout(debounce);
        fetchEducation();
      } catch (error) {
        feedback.textContent = error.message || "Unable to connect. Please try again.";
        feedback.hidden = false;
        showToast("Could not save education", feedback.textContent, "error", 6000);
      } finally {
        submit.disabled = false;
      }
    });
  }
  fetchEducation();
})();
