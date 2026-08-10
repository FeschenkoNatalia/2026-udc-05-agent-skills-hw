import { register, type WidgetProps } from "../../core/registry.js";

export interface SpinnerProps extends WidgetProps {
  label?: string;
  size?: "sm" | "md" | "lg";
}

// Markup only — the spin animation is the consuming app's CSS, since this
// library ships no dependencies and no stylesheet.
export function createSpinner(props: SpinnerProps): string {
  const size = props.size ?? "md";
  const label = props.label ?? "Loading";
  return `<span class="spinner spinner--${size}" role="status" aria-label="${label}"></span>`;
}

register("spinner", createSpinner);