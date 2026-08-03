(() => {
  "use strict";

  const root = document.querySelector("[data-resource-root]");
  const configNode = document.querySelector("#resource-config");
  if (!root || !configNode || !window.CoffeeTrace) return;

  const config = JSON.parse(configNode.textContent);
  const tableBody = root.querySelector("[data-resource-table]");
  const countNode = root.querySelector("[data-result-count]");
  const searchInput = root.querySelector("[data-resource-search]");
  const refreshButton = root.querySelector("[data-resource-refresh]");
  const pagination = root.querySelector("[data-pagination]");
  const previousButton = root.querySelector("[data-page-prev]");
  const nextButton = root.querySelector("[data-page-next]");
  const pageLabel = root.querySelector("[data-page-label]");
  const modal = document.querySelector("[data-resource-modal]");
  const form = modal?.querySelector("[data-resource-form]");
  const fieldsRoot = modal?.querySelector("[data-form-fields]");
  const formError = modal?.querySelector("[data-form-error]");
  const submitButton = modal?.querySelector("[data-form-submit]");
  const modalTitle = modal?.querySelector("[data-modal-title]");

  let currentUrl = config.api_url;
  let nextUrl = null;
  let previousUrl = null;
  let currentPage = 1;
  let editId = null;
  let searchTimer = null;
  const records = new Map();

  const normalizeResults = (payload) => Array.isArray(payload) ? payload : (payload.results || []);
  const escapeStatus = (value) => String(value || "").toLowerCase().replace(/[^a-z0-9_-]/g, "-");

  async function load(url = config.api_url) {
    currentUrl = url;
    renderLoading();
    try {
      const response = await window.CoffeeTrace.apiFetch(url);
      if (!response.ok) throw new Error("No fue posible consultar la información.");
      const payload = await response.json();
      const rows = normalizeResults(payload);
      records.clear();
      rows.forEach((row) => records.set(String(row.id), row));
      nextUrl = payload.next || null;
      previousUrl = payload.previous || null;
      currentPage = getPageNumber(url);
      renderRows(rows);
      updatePagination(payload.count ?? rows.length);
    } catch (error) {
      renderError(error.message);
    }
  }

  function renderLoading() {
    tableBody.innerHTML = "";
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = config.columns.length + (config.can_write ? 1 : 0);
    cell.innerHTML = '<div class="loading-state"><span class="spinner"></span> Cargando información…</div>';
    row.append(cell);
    tableBody.append(row);
  }

  function renderError(message) {
    tableBody.innerHTML = "";
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = config.columns.length + (config.can_write ? 1 : 0);
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.innerHTML = "<span>!</span><h3>No se pudo cargar</h3>";
    const paragraph = document.createElement("p");
    paragraph.textContent = message;
    empty.append(paragraph);
    cell.append(empty);
    row.append(cell);
    tableBody.append(row);
  }

  function renderRows(rows) {
    tableBody.innerHTML = "";
    if (!rows.length) {
      const row = document.createElement("tr");
      const cell = document.createElement("td");
      cell.colSpan = config.columns.length + (config.can_write ? 1 : 0);
      cell.innerHTML = '<div class="empty-state"><span>⌕</span><h3>Sin resultados</h3><p>No se encontraron registros con los criterios actuales.</p></div>';
      row.append(cell);
      tableBody.append(row);
      return;
    }
    const fragment = document.createDocumentFragment();
    rows.forEach((record) => {
      const row = document.createElement("tr");
      config.columns.forEach((column) => row.append(renderCell(record, column)));
      if (config.can_write) row.append(renderActions(record));
      fragment.append(row);
    });
    tableBody.append(fragment);
  }

  function renderCell(record, column) {
    const cell = document.createElement("td");
    const value = getNestedValue(record, column.key);
    if (column.type === "boolean") {
      const span = document.createElement("span");
      span.className = `boolean-pill ${value ? "is-true" : ""}`;
      span.textContent = value ? "Activo" : "Inactivo";
      cell.append(span);
      return cell;
    }
    if (column.type === "status") {
      const span = document.createElement("span");
      span.className = `status-pill status-${escapeStatus(value)}`;
      span.textContent = value || "—";
      cell.append(span);
      return cell;
    }
    if (column.type === "datetime") {
      cell.textContent = value ? new Intl.DateTimeFormat("es-CR", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "—";
      return cell;
    }
    if (column.type === "decimal") {
      const number = Number(value);
      cell.textContent = Number.isFinite(number) ? `${new Intl.NumberFormat("es-CR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(number)}${column.suffix || ""}` : "—";
      return cell;
    }
    if (column.type === "number") {
      cell.textContent = value === null || value === undefined || value === "" ? "—" : `${value}${column.suffix || ""}`;
      return cell;
    }
    if (column.type === "link") {
      const link = document.createElement("a");
      link.className = "button button-ghost button-small";
      link.href = column.path.replace("{value}", encodeURIComponent(value));
      link.textContent = "Abrir";
      cell.append(link);
      return cell;
    }
    cell.textContent = value === null || value === undefined || value === "" ? "—" : value;
    return cell;
  }

  function renderActions(record) {
    const cell = document.createElement("td");
    const wrapper = document.createElement("div");
    wrapper.className = "table-actions";
    const edit = document.createElement("button");
    edit.type = "button";
    edit.className = "table-action";
    edit.title = "Editar";
    edit.setAttribute("aria-label", `Editar ${record.code || record.name || record.id}`);
    edit.textContent = "✎";
    edit.addEventListener("click", () => openModal(record));
    wrapper.append(edit);
    cell.append(wrapper);
    return cell;
  }

  function updatePagination(total) {
    countNode.textContent = `${total} ${total === 1 ? "registro" : "registros"}`;
    const visible = Boolean(nextUrl || previousUrl);
    pagination.hidden = !visible;
    previousButton.disabled = !previousUrl;
    nextButton.disabled = !nextUrl;
    pageLabel.textContent = `Página ${currentPage}`;
  }

  function getPageNumber(url) {
    try {
      return Number(new URL(url, window.location.origin).searchParams.get("page") || 1);
    } catch {
      return 1;
    }
  }

  function getNestedValue(object, path) {
    return path.split(".").reduce((value, key) => value?.[key], object);
  }

  function fieldElement(field, record = {}) {
    const group = document.createElement("div");
    group.className = `field-group ${field.wide ? "is-wide" : ""} ${field.type === "checkbox" ? "checkbox-field" : ""}`;
    const inputId = `resource-${field.name}`;
    const label = document.createElement("label");
    label.htmlFor = inputId;
    label.textContent = field.label;
    if (field.required) {
      const required = document.createElement("span");
      required.className = "required";
      required.textContent = " *";
      label.append(required);
    }
    const input = createInput(field, inputId);
    applyInitialValue(input, field, record[field.name]);
    if (field.type === "checkbox") group.append(input, label);
    else group.append(label, input);
    return group;
  }

  function createInput(field, inputId) {
    let input;
    if (field.type === "textarea") {
      input = document.createElement("textarea");
    } else if (field.type === "select" || field.type === "remote-select") {
      input = document.createElement("select");
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Seleccione…";
      input.append(placeholder);
      if (field.type === "select") appendOptions(input, field.options || []);
      else loadRemoteOptions(input, field);
    } else {
      input = document.createElement("input");
      input.type = field.type || "text";
    }
    input.id = inputId;
    input.name = field.name;
    input.required = Boolean(field.required);
    if (field.step) input.step = field.step;
    return input;
  }

  function appendOptions(select, options) {
    options.forEach((option) => {
      const element = document.createElement("option");
      element.value = option.value;
      element.textContent = option.text;
      select.append(element);
    });
  }

  async function loadRemoteOptions(select, field) {
    select.disabled = true;
    try {
      const response = await window.CoffeeTrace.apiFetch(field.source);
      const payload = await response.json();
      appendOptions(select, normalizeResults(payload).map((item) => ({ value: item[field.value], text: item[field.text] })));
    } catch {
      const option = document.createElement("option");
      option.textContent = "No se pudieron cargar las opciones";
      option.disabled = true;
      select.append(option);
    } finally {
      select.disabled = false;
      if (select.dataset.pendingValue) {
        select.value = select.dataset.pendingValue;
        delete select.dataset.pendingValue;
      }
    }
  }

  function applyInitialValue(input, field, value) {
    if (field.type === "checkbox") {
      input.checked = value === undefined ? Boolean(field.default) : Boolean(value);
      return;
    }
    let finalValue = value ?? field.default ?? "";
    if (finalValue === "now") {
      const now = new Date(Date.now() - new Date().getTimezoneOffset() * 60000);
      finalValue = now.toISOString().slice(0, 16);
    } else if (field.type === "datetime-local" && finalValue) {
      const date = new Date(finalValue);
      finalValue = new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    }
    if (field.type === "remote-select" && input.disabled) input.dataset.pendingValue = String(finalValue);
    else input.value = finalValue;
  }

  function buildForm(record = {}) {
    fieldsRoot.innerHTML = "";
    config.fields.forEach((field) => fieldsRoot.append(fieldElement(field, record)));
  }

  function openModal(record = null) {
    editId = record?.id ?? null;
    modalTitle.textContent = editId ? `Editar ${config.title.toLowerCase()}` : config.create_label;
    formError.hidden = true;
    formError.textContent = "";
    buildForm(record || {});
    modal.showModal();
  }

  function closeModal() {
    modal.close();
    editId = null;
  }

  function formPayload() {
    const payload = {};
    config.fields.forEach((field) => {
      const input = form.elements.namedItem(field.name);
      if (!input) return;
      if (field.type === "checkbox") {
        payload[field.name] = input.checked;
        return;
      }
      const value = input.value.trim();
      if (value !== "") payload[field.name] = value;
      else if (editId && ["latitude", "longitude", "altitude_masl", "area_hectares", "moisture_percentage", "reception"].includes(field.name)) payload[field.name] = null;
    });
    return payload;
  }

  function formatErrors(payload) {
    if (!payload || typeof payload !== "object") return "No fue posible guardar el registro.";
    const details = payload.errors && typeof payload.errors === "object" ? payload.errors : payload;
    return Object.entries(details).map(([field, messages]) => {
      const label = config.fields.find((item) => item.name === field)?.label || field;
      const text = Array.isArray(messages) ? messages.join(" ") : (typeof messages === "object" ? JSON.stringify(messages) : messages);
      return `${label}: ${text}`;
    }).join("\n");
  }

  async function submit(event) {
    event.preventDefault();
    if (!form.reportValidity()) return;
    submitButton.disabled = true;
    submitButton.textContent = "Guardando…";
    formError.hidden = true;
    const url = editId ? `${config.api_url}${editId}/` : config.api_url;
    try {
      const response = await window.CoffeeTrace.apiFetch(url, {
        method: editId ? "PATCH" : "POST",
        body: JSON.stringify(formPayload()),
      });
      const payload = response.status === 204 ? {} : await response.json();
      if (!response.ok) throw new Error(formatErrors(payload));
      closeModal();
      window.CoffeeTrace.notify("Registro guardado", "La información se actualizó correctamente.");
      await load(currentUrl);
    } catch (error) {
      formError.textContent = error.message;
      formError.hidden = false;
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Guardar";
    }
  }

  document.querySelector("[data-open-resource-modal]")?.addEventListener("click", () => openModal());
  document.querySelectorAll("[data-close-resource-modal]").forEach((button) => button.addEventListener("click", closeModal));
  modal?.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });
  form?.addEventListener("submit", submit);
  refreshButton?.addEventListener("click", () => load(currentUrl));
  previousButton?.addEventListener("click", () => previousUrl && load(previousUrl));
  nextButton?.addEventListener("click", () => nextUrl && load(nextUrl));
  searchInput?.addEventListener("input", () => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => {
      const url = new URL(config.api_url, window.location.origin);
      if (searchInput.value.trim()) url.searchParams.set("search", searchInput.value.trim());
      load(`${url.pathname}${url.search}`);
    }, 320);
  });

  load();
})();
