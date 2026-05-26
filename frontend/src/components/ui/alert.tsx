import * as React from "react";

import { cn } from "@/lib/utils";

const Alert = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      role="alert"
      className={cn(
        "relative w-full rounded-3xl border border-destructive/20 bg-destructive/5 p-4 text-sm text-destructive",
        className
      )}
      {...props}
    />
  )
);

const AlertTitle = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h5 ref={ref} className={cn("mb-1 font-medium", className)} {...props} />
  )
);

const AlertDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p ref={ref} className={cn("leading-6", className)} {...props} />
));

Alert.displayName = "Alert";
AlertTitle.displayName = "AlertTitle";
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertDescription, AlertTitle };
