import { cn } from "@/lib/utils";

export const Input = ({
  className,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) => (
  <input
    className={cn(
      "w-full px-4 py-2 rounded-md border border-border-strong bg-bg focus:outline-none focus:ring-2 focus:ring-brand",
      className
    )}
    {...props}
  />
);

export const TextArea = ({
  className,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement>) => (
  <textarea
    className={cn(
      "w-full px-4 py-2 rounded-md border border-border-strong bg-bg focus:outline-none focus:ring-2 focus:ring-brand",
      className
    )}
    {...props}
  />
);
