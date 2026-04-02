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
      <form id="execution-form" hidden>
        <h3>Execute</h3>
        <div id="form-fields"></div>
        <p id="form-status" class="muted"></p>
        <button id="execute-button" type="submit">Ausführen</button>
      </form>
      <section id="execution-result" hidden>
        <h3>Ergebnis</h3>
        <p id="result-status"></p>
        <div id="result-content" class="result-box"></div>
      </section>
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
const executionFormEl = document.getElementById("execution-form") as HTMLFormElement;
const formFieldsEl = document.getElementById("form-fields") as HTMLDivElement;
const formStatusEl = document.getElementById("form-status") as HTMLParagraphElement;
const executeButtonEl = document.getElementById("execute-button") as HTMLButtonElement;
const executionResultEl = document.getElementById("execution-result") as HTMLElement;
const resultStatusEl = document.getElementById("result-status") as HTMLParagraphElement;
const resultContentEl = document.getElementById("result-content") as HTMLDivElement;

type CalculationDetailField = {
  name?: string;
  field_type?: string;
  required?: boolean;
  description?: string;
  min_value?: number;
  max_value?: number;
  allowed_values?: Array<string | number | boolean>;
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

type CalculationExecutionResult = {
  ok?: boolean;
  calculation_id?: string;
  result?: unknown;
  error?: {
    message?: string;
    details?: Array<{ field?: string; message?: string; code?: string }>;
  };
};

const state: {
  details: CalculationDetails | null;
  formValues: Record<string, string>;
  fieldErrors: Record<string, string>;
  isSubmitting: boolean;
} = {
  details: null,
  formValues: {},
  fieldErrors: {},
  isSubmitting: false,
};

function buildFieldDisplayDescription(field: CalculationDetailField): string {
  const required = field.required ? "required" : "optional";
  return `${String(field.name ?? "unknown")} (${String(field.field_type ?? "unknown")}, ${required})${
    field.description ? ` — ${field.description}` : ""
  }`;
}

function createValueDisplay(value: unknown): Node {
  if (Array.isArray(value)) {
    const ul = document.createElement("ul");
    value.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = typeof item === "object" ? JSON.stringify(item) : String(item);
      ul.appendChild(li);
    });
    return ul;
  }

  if (value !== null && typeof value === "object") {
    const dl = document.createElement("dl");
    Object.entries(value as Record<string, unknown>).forEach(([key, nested]) => {
      const dt = document.createElement("dt");
      dt.textContent = key;
      const dd = document.createElement("dd");
      dd.appendChild(createValueDisplay(nested));
      dl.appendChild(dt);
      dl.appendChild(dd);
    });
    return dl;
  }

  const span = document.createElement("span");
  span.textContent = value === null ? "null" : String(value);
  return span;
}

function renderExecutionResult(payload: CalculationExecutionResult): void {
  executionResultEl.hidden = false;
  resultContentEl.innerHTML = "";

  const success = Boolean(payload.ok);
  resultStatusEl.className = success ? "status-success" : "status-error";
  resultStatusEl.textContent = success ? "Berechnung erfolgreich." : "Berechnung fehlgeschlagen.";

  if (success) {
    const dl = document.createElement("dl");

    const calcIdDt = document.createElement("dt");
    calcIdDt.textContent = "calculation_id";
    const calcIdDd = document.createElement("dd");
    calcIdDd.textContent = String(payload.calculation_id ?? state.details?.id ?? "unknown");
    dl.appendChild(calcIdDt);
    dl.appendChild(calcIdDd);

    const resultDt = document.createElement("dt");
    resultDt.textContent = "result";
    const resultDd = document.createElement("dd");
    resultDd.appendChild(createValueDisplay(payload.result));
    dl.appendChild(resultDt);
    dl.appendChild(resultDd);

    resultContentEl.appendChild(dl);
    return;
  }

  const message = document.createElement("p");
  message.textContent = payload.error?.message ?? "Unbekannter Fehler";
  resultContentEl.appendChild(message);

  const errorDetails = payload.error?.details ?? [];
  if (errorDetails.length > 0) {
    const ul = document.createElement("ul");
    errorDetails.forEach((detail) => {
      const li = document.createElement("li");
      const fieldPrefix = detail.field ? `${detail.field}: ` : "";
      li.textContent = `${fieldPrefix}${detail.message ?? detail.code ?? "Validation error"}`;
      ul.appendChild(li);
    });
    resultContentEl.appendChild(ul);
  }
}

function coerceFieldValue(field: CalculationDetailField, rawValue: string | undefined): { hasValue?: boolean; value?: unknown; error?: string } {
  const value = rawValue ?? "";
  if (value === "") {
    return { hasValue: false };
  }

  if (field.allowed_values && field.allowed_values.length > 0) {
    return { hasValue: true, value };
  }

  if (field.field_type === "number") {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return { error: "Bitte eine gültige Zahl eingeben." };
    return { hasValue: true, value: numeric };
  }

  if (field.field_type === "integer") {
    const numeric = Number(value);
    if (!Number.isInteger(numeric)) return { error: "Bitte eine gültige Ganzzahl eingeben." };
    return { hasValue: true, value: numeric };
  }

  if (field.field_type === "boolean") {
    if (value !== "true" && value !== "false") return { error: "Bitte true oder false auswählen." };
    return { hasValue: true, value: value === "true" };
  }

  if (field.field_type === "number_list") {
    const numbers = value
      .split(/[\n,;]/)
      .map((item) => item.trim())
      .filter((item) => item.length > 0)
      .map((item) => Number(item));

    if (numbers.length === 0 || numbers.some((entry) => !Number.isFinite(entry))) {
      return { error: "Bitte eine Liste gültiger Zahlen eingeben (z. B. 1, 2, 3)." };
    }

    return { hasValue: true, value: numbers };
  }

  return { hasValue: true, value };
}

function validateAndBuildInput(fields: CalculationDetailField[]): { input: Record<string, unknown>; errors: Record<string, string> } {
  const input: Record<string, unknown> = {};
  const errors: Record<string, string> = {};

  fields.forEach((field) => {
    const fieldName = String(field.name ?? "");
    if (!fieldName) return;

    const parsed = coerceFieldValue(field, state.formValues[fieldName]);
    if (parsed.error) {
      errors[fieldName] = parsed.error;
      return;
    }

    if (!parsed.hasValue) {
      if (field.required) {
        errors[fieldName] = "Dieses Feld ist erforderlich.";
      }
      return;
    }

    const parsedValue = parsed.value;
    if (typeof parsedValue === "number") {
      if (typeof field.min_value === "number" && parsedValue < field.min_value) {
        errors[fieldName] = `Wert muss >= ${field.min_value} sein.`;
        return;
      }
      if (typeof field.max_value === "number" && parsedValue > field.max_value) {
        errors[fieldName] = `Wert muss <= ${field.max_value} sein.`;
        return;
      }
    }

    if (field.allowed_values && field.allowed_values.length > 0 && !field.allowed_values.includes(parsedValue as never)) {
      errors[fieldName] = "Bitte einen erlaubten Wert auswählen.";
      return;
    }

    input[fieldName] = parsedValue;
  });

  return { input, errors };
}

function updateFormValue(fieldName: string, value: string): void {
  state.formValues[fieldName] = value;
}

function buildInputElement(field: CalculationDetailField): HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement {
  const fieldName = String(field.name ?? "");
  const inputId = `input-${fieldName}`;

  if (field.allowed_values && field.allowed_values.length > 0) {
    const select = document.createElement("select");
    select.id = inputId;
    select.name = fieldName;

    if (!field.required) {
      const emptyOption = document.createElement("option");
      emptyOption.value = "";
      emptyOption.textContent = "—";
      select.appendChild(emptyOption);
    }

    field.allowed_values.forEach((allowedValue) => {
      const option = document.createElement("option");
      option.value = String(allowedValue);
      option.textContent = String(allowedValue);
      select.appendChild(option);
    });

    if (state.formValues[fieldName] === undefined && field.required) {
      state.formValues[fieldName] = String(field.allowed_values[0]);
    }

    select.value = state.formValues[fieldName] ?? "";
    select.disabled = state.isSubmitting;
    select.addEventListener("change", (event) => {
      updateFormValue(fieldName, (event.target as HTMLSelectElement).value);
    });
    return select;
  }

  if (field.field_type === "boolean") {
    const select = document.createElement("select");
    select.id = inputId;
    select.name = fieldName;
    [
      { value: "", label: field.required ? "Bitte wählen" : "—" },
      { value: "true", label: "true" },
      { value: "false", label: "false" },
    ].forEach((item) => {
      const option = document.createElement("option");
      option.value = item.value;
      option.textContent = item.label;
      select.appendChild(option);
    });

    select.value = state.formValues[fieldName] ?? "";
    select.disabled = state.isSubmitting;
    select.addEventListener("change", (event) => {
      updateFormValue(fieldName, (event.target as HTMLSelectElement).value);
    });
    return select;
  }

  if (field.field_type === "number_list") {
    const textarea = document.createElement("textarea");
    textarea.id = inputId;
    textarea.name = fieldName;
    textarea.rows = 3;
    textarea.placeholder = "1, 2, 3";
    textarea.value = state.formValues[fieldName] ?? "";
    textarea.disabled = state.isSubmitting;
    textarea.addEventListener("input", (event) => {
      updateFormValue(fieldName, (event.target as HTMLTextAreaElement).value);
    });
    return textarea;
  }

  const input = document.createElement("input");
  input.id = inputId;
  input.name = fieldName;
  if (field.field_type === "number") {
    input.type = "number";
    input.step = "any";
  } else if (field.field_type === "integer") {
    input.type = "number";
    input.step = "1";
  } else {
    input.type = "text";
  }

  if (typeof field.min_value === "number") input.min = String(field.min_value);
  if (typeof field.max_value === "number") input.max = String(field.max_value);
  input.placeholder = String(field.description ?? "");
  input.value = state.formValues[fieldName] ?? "";
  input.disabled = state.isSubmitting;
  input.addEventListener("input", (event) => {
    updateFormValue(fieldName, (event.target as HTMLInputElement).value);
  });
  return input;
}

function renderExecutionForm(details: CalculationDetails): void {
  const fields = details.input_fields ?? [];
  executionFormEl.hidden = fields.length === 0;
  formFieldsEl.innerHTML = "";

  fields.forEach((field) => {
    const fieldName = String(field.name ?? "");
    const wrapper = document.createElement("div");
    wrapper.className = "field";

    const label = document.createElement("label");
    label.htmlFor = `input-${fieldName}`;
    label.textContent = field.required ? `${fieldName} *` : fieldName;
    wrapper.appendChild(label);

    wrapper.appendChild(buildInputElement(field));

    const meta = document.createElement("p");
    meta.className = "inline-meta";
    const segments: string[] = [];
    if (field.field_type) segments.push(`Typ: ${field.field_type}`);
    if (typeof field.min_value === "number") segments.push(`Min: ${field.min_value}`);
    if (typeof field.max_value === "number") segments.push(`Max: ${field.max_value}`);
    if (segments.length > 0) {
      meta.textContent = segments.join(" · ");
      wrapper.appendChild(meta);
    }

    if (field.description) {
      const help = document.createElement("p");
      help.className = "field-help muted";
      help.textContent = field.description;
      wrapper.appendChild(help);
    }

    if (state.fieldErrors[fieldName]) {
      const error = document.createElement("p");
      error.className = "field-error";
      error.textContent = state.fieldErrors[fieldName];
      wrapper.appendChild(error);
    }

    formFieldsEl.appendChild(wrapper);
  });

  executeButtonEl.disabled = state.isSubmitting;
}

function resetExecutionState(): void {
  state.formValues = {};
  state.fieldErrors = {};
  state.isSubmitting = false;
  executionResultEl.hidden = true;
  formStatusEl.textContent = "";
  resultStatusEl.textContent = "";
  resultContentEl.innerHTML = "";
}

function renderDetails(details: CalculationDetails): void {
  state.details = details;
  resetExecutionState();

  detailsEl.hidden = false;
  detailsNameEl.textContent = `${String(details.id ?? "unknown")} — ${String(details.name ?? "")}`;
  detailsDescriptionEl.textContent = String(details.description ?? "");
  detailsUsageHintEl.textContent = details.llm_usage_hint ? `Hint: ${details.llm_usage_hint}` : "";

  detailsInputsEl.innerHTML = "";
  (details.input_fields ?? []).forEach((field) => {
    const li = document.createElement("li");
    li.textContent = buildFieldDisplayDescription(field);
    detailsInputsEl.appendChild(li);
  });

  detailsExamplesEl.innerHTML = "";
  (details.examples ?? []).forEach((example) => {
    const li = document.createElement("li");
    li.textContent = String(example.title ?? "Example");
    detailsExamplesEl.appendChild(li);
  });

  renderExecutionForm(details);
}

executionFormEl.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!state.details?.id || state.isSubmitting) return;

  const fields = state.details.input_fields ?? [];
  const { input, errors } = validateAndBuildInput(fields);
  state.fieldErrors = errors;
  if (Object.keys(errors).length > 0) {
    formStatusEl.className = "status-error";
    formStatusEl.textContent = "Bitte Eingabefehler korrigieren.";
    renderExecutionForm(state.details);
    return;
  }

  state.isSubmitting = true;
  formStatusEl.className = "muted";
  formStatusEl.textContent = "Berechnung wird ausgeführt…";
  renderExecutionForm(state.details);

  app.requestToolCall({
    toolName: "execute_calculation",
    arguments: {
      calculation_id: state.details.id,
      input,
    },
  });
});

const transport = new PostMessageTransport(parentOrigin);
const app = new App(transport, {
  ontoolresult: (payload: MCPToolResultPayload) => {
    const structured = (payload.structuredContent ?? payload.result ?? {}) as Record<string, unknown>;
    const isDetailsTool = payload.toolName === "get_calculation_details";
    const isDetailsShape = typeof structured === "object" && structured !== null && "input_fields" in structured;

    if (payload.toolName === "execute_calculation") {
      state.isSubmitting = false;
      formStatusEl.textContent = "";
      if (state.details) {
        renderExecutionForm(state.details);
      }
      renderExecutionResult(structured as CalculationExecutionResult);
      return;
    }

    if (isDetailsTool || isDetailsShape) {
      renderDetails(structured as CalculationDetails);
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
