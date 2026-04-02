import { App, PostMessageTransport, type MCPHostContext, type MCPToolResultPayload } from "./runtime";

const parentOrigin = document.referrer ? new URL(document.referrer).origin : "*";

function applyHostContext(hostContext: MCPHostContext): void {
  const style = document.documentElement.style;
  const insets = hostContext.safeAreaInsets ?? hostContext.insets ?? {};

  if (typeof insets.top === "number") style.setProperty("--host-inset-top", `${insets.top}px`);
  if (typeof insets.right === "number") style.setProperty("--host-inset-right", `${insets.right}px`);
  if (typeof insets.bottom === "number") style.setProperty("--host-inset-bottom", `${insets.bottom}px`);
  if (typeof insets.left === "number") style.setProperty("--host-inset-left", `${insets.left}px`);

  if (hostContext.theme === "light" || hostContext.theme === "dark") {
    document.documentElement.dataset.hostTheme = hostContext.theme;
  }
}

const root = document.getElementById("app-root");
if (!root) {
  throw new Error("Missing #app-root");
}

root.innerHTML = `
  <main>
    <h1>Calculations</h1>
    <p class="muted" id="status">Waiting for tool result…</p>
    <ul id="calculation-list"></ul>
    <section id="details" hidden>
      <h2>Calculation details</h2>
      <p id="details-name" class="muted"></p>
      <p id="details-description"></p>
      <h3>Input fields</h3>
      <ul id="details-inputs"></ul>
      <h3>Examples</h3>
      <ul id="details-examples"></ul>
      <p id="details-usage-hint" class="muted"></p>
    </section>
  </main>
`;

const statusEl = document.getElementById("status") as HTMLParagraphElement;
const listEl = document.getElementById("calculation-list") as HTMLUListElement;
const detailsEl = document.getElementById("details") as HTMLElement;
const detailsNameEl = document.getElementById("details-name") as HTMLParagraphElement;
const detailsDescriptionEl = document.getElementById("details-description") as HTMLParagraphElement;
const detailsInputsEl = document.getElementById("details-inputs") as HTMLUListElement;
const detailsExamplesEl = document.getElementById("details-examples") as HTMLUListElement;
const detailsUsageHintEl = document.getElementById("details-usage-hint") as HTMLParagraphElement;

type CalculationDetailField = {
  name?: string;
  field_type?: string;
  required?: boolean;
  description?: string;
};

type CalculationDetailExample = {
  title?: string;
};

type CalculationDetails = {
  id?: string;
  name?: string;
  description?: string;
  llm_usage_hint?: string;
  input_fields?: CalculationDetailField[];
  examples?: CalculationDetailExample[];
};

function renderDetails(details: CalculationDetails): void {
  detailsEl.hidden = false;
  detailsNameEl.textContent = `${String(details.id ?? "unknown")} — ${String(details.name ?? "")}`;
  detailsDescriptionEl.textContent = String(details.description ?? "");
  detailsUsageHintEl.textContent = details.llm_usage_hint ? `Hint: ${details.llm_usage_hint}` : "";

  detailsInputsEl.innerHTML = "";
  (details.input_fields ?? []).forEach((field) => {
    const li = document.createElement("li");
    const requirement = field.required ? "required" : "optional";
    li.textContent = `${String(field.name ?? "unknown")} (${String(field.field_type ?? "unknown")}, ${requirement})${
      field.description ? ` — ${field.description}` : ""
    }`;
    detailsInputsEl.appendChild(li);
  });

  detailsExamplesEl.innerHTML = "";
  (details.examples ?? []).forEach((example) => {
    const li = document.createElement("li");
    li.textContent = String(example.title ?? "Example");
    detailsExamplesEl.appendChild(li);
  });
}

const transport = new PostMessageTransport(parentOrigin);
const app = new App(transport, {
  ontoolinput: () => {
    statusEl.textContent = "Loading details…";
  },
  ontoolresult: (payload: MCPToolResultPayload) => {
    const structured = payload.structuredContent ?? payload.result ?? {};
    const detailsLike = structured as CalculationDetails;
    const isDetailsTool = payload.toolName === "get_calculation_details";
    const isDetailsShape = typeof detailsLike === "object" && !!detailsLike && "input_fields" in detailsLike;

    if (isDetailsTool || isDetailsShape) {
      renderDetails(detailsLike);
      statusEl.textContent = "Details loaded.";
      return;
    }

    const calculations = (structured as { calculations?: Array<{ id: string; name: string }> }).calculations ?? [];
    listEl.innerHTML = "";
    calculations.forEach((item) => {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `${item.id}: ${item.name}`;
      button.addEventListener("click", () => {
        app.requestToolCall({
          toolName: "get_calculation_details",
          arguments: { calculation_id: item.id },
        });
      });
      li.appendChild(button);
      listEl.appendChild(li);
    });
    statusEl.textContent = `${calculations.length} calculation(s) loaded.`;
  },
  onhostcontext: (payload: MCPHostContext) => {
    applyHostContext(payload);
  },
});

app.connect();
