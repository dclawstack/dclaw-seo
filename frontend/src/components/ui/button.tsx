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
        "inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium transition",
        variant === "primary" && "bg-emerald-600 text-white hover:bg-emerald-700",
        variant === "secondary" && "bg-gray-100 text-gray-900 hover:bg-gray-200",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
