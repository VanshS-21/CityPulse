/**
 * Integration Status: This file appears to have minimal connections.
 * Consider:
 * 1. Adding imports to connect with related modules
 * 2. Exporting key functions/types in index files
 * 3. Adding usage examples in JSDoc comments
 * 4. Reviewing if this functionality should be merged with related files
 */

import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-primary/10", className)}
      {...props}
    />
  )
}

export { Skeleton }
