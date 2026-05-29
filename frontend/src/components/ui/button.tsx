import { cn } from "@/lib/utils";

export function Button({
  children,
  className,
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center px-4 py-2 rounded-pill font-medium transition-colors duration-base ease-out-quart",
        variant === "primary" && "bg-brand text-fg-on-brand hover:bg-brand-hover shadow-brand",
        variant === "secondary" && "bg-brand-soft text-brand-press hover:bg-brand-200",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
