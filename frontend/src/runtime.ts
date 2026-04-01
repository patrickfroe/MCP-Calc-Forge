export type MCPToolResultPayload = {
  toolName?: string | null;
  structuredContent?: unknown;
  result?: unknown;
};

export type MCPToolInputPayload = {
  toolName: string;
  arguments: Record<string, unknown>;
};

export type MCPHostContext = {
  safeAreaInsets?: { top?: number; right?: number; bottom?: number; left?: number };
  insets?: { top?: number; right?: number; bottom?: number; left?: number };
  theme?: "light" | "dark" | string;
};

export class PostMessageTransport {
  private readonly parentOrigin: string;

  constructor(parentOrigin: string) {
    this.parentOrigin = parentOrigin;
  }

  sendToolCallRequest(payload: MCPToolInputPayload): void {
    const message = {
      type: "tool-call-request",
      toolName: payload.toolName,
      arguments: payload.arguments,
      mcpUi: {
        version: "1.0",
        type: "tool-call-request",
        payload,
      },
    };
    window.parent.postMessage(message, this.parentOrigin);
  }

  parseIncomingMessage(data: unknown): { type: "tool-result"; payload: MCPToolResultPayload } | { type: "host-context"; payload: MCPHostContext } | null {
    if (!data || typeof data !== "object") return null;

    const typedData = data as Record<string, unknown>;
    if (typedData.mcpUi && typeof typedData.mcpUi === "object") {
      const mcpUi = typedData.mcpUi as Record<string, unknown>;
      const mcpUiType = mcpUi.type;
      const mcpUiPayload = (mcpUi.payload as Record<string, unknown> | undefined) ?? {};

      if (mcpUiType === "host-context" || mcpUiType === "host-update") {
        return { type: "host-context", payload: (mcpUiPayload.hostContext as MCPHostContext | undefined) ?? (mcpUiPayload as MCPHostContext) };
      }
      if (mcpUiType === "tool-result") {
        return {
          type: "tool-result",
          payload: {
            toolName: (mcpUiPayload.toolName as string | undefined) ?? (typedData.toolName as string | undefined),
            structuredContent: mcpUiPayload.structuredContent ?? typedData.structuredContent,
            result: mcpUiPayload.result ?? typedData.result,
          },
        };
      }
      return null;
    }

    if (typedData.type === "host-context" || typedData.type === "host-update") {
      return { type: "host-context", payload: (typedData.hostContext as MCPHostContext | undefined) ?? {} };
    }

    if (typedData.type !== "tool-result") return null;
    return {
      type: "tool-result",
      payload: {
        toolName: typedData.toolName as string | undefined,
        structuredContent: typedData.structuredContent,
        result: typedData.result,
      },
    };
  }
}

type AppHandlers = {
  ontoolinput?: (payload: MCPToolInputPayload) => void;
  ontoolresult?: (payload: MCPToolResultPayload) => void;
  onhostcontext?: (payload: MCPHostContext) => void;
};

export class App {
  private readonly transport: PostMessageTransport;
  private readonly handlers: AppHandlers;

  constructor(transport: PostMessageTransport, handlers: AppHandlers) {
    this.transport = transport;
    this.handlers = handlers;
  }

  requestToolCall(payload: MCPToolInputPayload): void {
    this.handlers.ontoolinput?.(payload);
    this.transport.sendToolCallRequest(payload);
  }

  connect(): void {
    window.addEventListener("message", (event) => {
      if (event.source !== window.parent) return;
      if (this.transportOrigin() !== "*" && event.origin !== this.transportOrigin()) return;
      const parsed = this.transport.parseIncomingMessage(event.data);
      if (!parsed) return;
      if (parsed.type === "host-context") {
        this.handlers.onhostcontext?.(parsed.payload);
        return;
      }
      this.handlers.ontoolresult?.(parsed.payload);
    });
  }

  private transportOrigin(): string {
    return (this.transport as unknown as { parentOrigin: string }).parentOrigin;
  }
}
