import { Component, ReactNode } from "react";

interface Props { children: ReactNode; label?: string }
interface State { error: Error | null }

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex flex-col items-center justify-center h-48 gap-2 rounded-xl border border-subtle bg-card p-4">
          <p className="text-[11px] font-semibold text-negative uppercase tracking-widest">
            {this.props.label ?? "Rendering error"}
          </p>
          <p className="text-[10px] text-muted text-center max-w-xs">
            {this.state.error.message}
          </p>
          <button
            onClick={() => this.setState({ error: null })}
            className="mt-1 text-[10px] px-3 py-1 rounded-lg border border-subtle text-secondary hover:text-primary transition-colors"
          >
            Retry
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
