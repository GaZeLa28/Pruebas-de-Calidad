(() => {
  "use strict";
  const generateButton = document.querySelector("[data-generate-qr]");
  const associateButton = document.querySelector("[data-associate-reception]");
  const modal = document.querySelector("[data-association-modal]");
  const form = modal?.querySelector("form");
  const receptionSelect = modal?.querySelector("[name='reception_id']");
  const weightInput = modal?.querySelector("[name='assigned_weight_kg']");
  const errorNode = modal?.querySelector("[data-association-error]");

  generateButton?.addEventListener("click", async () => {
    const lotId = generateButton.dataset.lotId;
    generateButton.disabled = true;
    generateButton.textContent = "Generando…";
    try {
      const response = await window.CoffeeTrace.apiFetch(`/api/v1/lots/${lotId}/generate-qr/`, { method: "POST", body: "{}" });
      if (!response.ok) throw new Error("No fue posible generar el código QR.");
      window.CoffeeTrace.notify("Código QR listo", "La consulta pública quedó habilitada.");
      window.location.reload();
    } catch (error) {
      window.CoffeeTrace.notify("Error", error.message, "error");
    } finally {
      generateButton.disabled = false;
      generateButton.textContent = "Generar QR";
    }
  });

  async function openAssociation() {
    if (!modal || !receptionSelect) return;
    receptionSelect.innerHTML = '<option value="">Cargando recepciones…</option>';
    modal.showModal();
    try {
      const response = await window.CoffeeTrace.apiFetch("/api/v1/receptions/?status=VALIDATED&page_size=100");
      const payload = await response.json();
      const rows = Array.isArray(payload) ? payload : payload.results || [];
      receptionSelect.innerHTML = '<option value="">Seleccione una recepción validada…</option>';
      rows.forEach((item) => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = `${item.code} · ${item.producer_name} · ${item.calculated_net_weight_kg} kg`;
        option.dataset.maxWeight = item.calculated_net_weight_kg;
        receptionSelect.append(option);
      });
    } catch {
      receptionSelect.innerHTML = '<option value="">No se pudieron cargar las recepciones</option>';
    }
  }

  associateButton?.addEventListener("click", openAssociation);
  modal?.querySelectorAll("[data-close-association]").forEach((button) => button.addEventListener("click", () => modal.close()));
  receptionSelect?.addEventListener("change", () => {
    const option = receptionSelect.selectedOptions[0];
    if (option?.dataset.maxWeight) weightInput.value = option.dataset.maxWeight;
  });
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const lotId = associateButton.dataset.lotId;
    errorNode.hidden = true;
    try {
      const response = await window.CoffeeTrace.apiFetch(`/api/v1/lots/${lotId}/associate-reception/`, {
        method: "POST",
        body: JSON.stringify({
          reception_id: receptionSelect.value,
          assigned_weight_kg: weightInput.value,
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(Object.values(payload).flat().join(" "));
      window.CoffeeTrace.notify("Recepción asociada", "El peso total del lote fue recalculado.");
      window.location.reload();
    } catch (error) {
      errorNode.textContent = error.message;
      errorNode.hidden = false;
    }
  });
})();
