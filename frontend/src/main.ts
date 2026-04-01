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
      <pre id="details-json"></pre>
    </section>
  </main>
`;

const statusEl = document.getElementById("status") as HTMLParagraphElement;
const listEl = document.getElementById("calculation-list") as HTMLUListElement;
const detailsEl = document.getElementById("details") as HTMLElement;
const detailsNameEl = document.getElementById("details-name") as HTMLParagraphElement;
const detailsJsonEl = document.getElementById("details-json") as HTMLPreElement;

const transport = new PostMessageTransport(parentOrigin);
const app = new App(transport, {
  ontoolinput: () => {
    statusEl.textContent = "Loading details…";
  },
  ontoolresult: (payload: MCPToolResultPayload) => {
    const structured = payload.structuredContent ?? payload.result ?? {};
    if (payload.toolName === "get_calculation_details") {
      const details = structured as Record<string, unknown>;
      detailsEl.hidden = false;
      detailsNameEl.textContent = `${String(details.id ?? "unknown")} — ${String(details.name ?? "")}`;
      detailsJsonEl.textContent = JSON.stringify(details, null, 2);
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
