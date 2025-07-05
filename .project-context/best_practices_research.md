# Code Enhancement Research & Best Practices

This document summarizes the findings from web research aimed at enhancing the CityPulse codebase by applying modern best practices.

## Frontend: Next.js 15

Research based on the official [Next.js 15 Blog Post](https://nextjs.org/blog/next-15).

### 1. Caching Semantics

*   **GET Route Handlers No Longer Cached by Default**: In a significant shift from Next.js 14, `GET` API routes are now dynamic by default. This is beneficial for CityPulse, as it ensures that API endpoints always return fresh data without extra configuration. Caching can be explicitly enabled with `export const dynamic = 'force-static';` if needed.
*   **Client Router Cache Defaults Changed**: The client-side cache for page navigations is now disabled by default (`staleTime: 0`). This means navigating between pages will always fetch the latest data, which is ideal for a dynamic application like CityPulse where event statuses can change frequently.

### 2. React 19 Integration

*   **React 19 is the Default**: Next.js 15 uses React 19, bringing new capabilities like Server Actions to the forefront.
*   **Server Actions are More Secure**: Unused Server Actions are now automatically removed from the client bundle, and the IDs used to call them are unguessable and periodically recalculated. This is a critical security enhancement that we will leverage when building forms and data mutation features.

### 3. Performance Optimizations

*   **Automatic Bundling of External Packages**: In the App Router, external packages are bundled by default to improve cold-start performance. This is the recommended approach. If a package needs to be excluded, it can be done via the `serverExternalPackages` option in `next.config.ts`.
*   **Automatic `sharp` Installation**: For self-hosted image optimization, the `sharp` package is now used automatically, simplifying the setup for production environments.

### 4. Tooling

*   **ESLint 9 Support**: The project already uses ESLint 9 with the modern flat config (`eslint.config.mjs`), aligning with the latest standards.

## Actionable Items for CityPulse Frontend

*   **Leverage New Caching Defaults**: For all future API routes and page navigations, rely on the new dynamic-by-default behavior to ensure data freshness.
*   **Use Server Actions for Mutations**: When implementing features like submitting citizen reports or updating event statuses, use the secure-by-default Server Actions provided by React 19.
*   **Monitor Bundle Dependencies**: While the default bundling is good, remain mindful of which packages are included. For a library like Firebase, we may later choose to exclude server-side components from the client bundle if they are not needed.

## Backend: Python, Apache Beam, and Google Cloud

Research based on Google Cloud's [Dataflow pipeline best practices](https://cloud.google.com/dataflow/docs/guides/pipeline-best-practices).

### 1. Code Structure & Reusability

*   **Create Libraries of Reusable Transforms**: Instead of defining `DoFn` classes within the pipeline script, they should be moved to a shared library (e.g., a `transforms` module). This improves reusability, testability, and separation of concerns. The CityPulse project can benefit from creating a central library for common tasks like data validation, enrichment, and I/O operations.

### 2. Error Handling

*   **Implement Dead-Letter Queues**: Currently, the pipelines catch exceptions but simply log and drop the failing element. A more robust pattern is to use a dead-letter queue. By using `beam.pvalue.TaggedOutput`, we can route failing elements to a separate `PCollection` and write them to a BigQuery table or GCS file for later inspection and reprocessing. This prevents data loss and provides better insight into data quality issues.

### 3. Performance & Cost Optimization

*   **Minimize Expensive Per-Element Operations**: Any expensive initialization (like creating a client for an external service) should be done in the `setup` or `start_bundle` method of a `DoFn`, not in the `process` method. In `citizen_report_pipeline.py`, the `storage.Client()` is created for every element, which is highly inefficient. This should be instantiated once per `DoFn` instance or bundle.
*   **Limit Batch Sizes and Concurrent Calls**: For interactions with external services that may have rate limits, use `beam.GroupIntoBatches` to group elements and process them as a single payload. This reduces per-call overhead and helps manage load on external systems.

### 4. Monitoring

*   **Use Apache Beam Metrics**: To gain deeper insights into pipeline execution, we should use `beam.metrics.Metrics` to create custom counters, distributions, and gauges. For example, we can track the number of malformed JSON records, successful API calls, or the distribution of processing times. These metrics are automatically available in Cloud Monitoring.

### Actionable Items for CityPulse Backend

*   **Refactor `DoFn`s into a `transforms` Module**: Create a new `data_models/transforms` directory and move classes like `ProcessMultimedia` into it.
*   **Implement a Dead-Letter Queue**: In the citizen report pipeline, add a tagged output to the `ProcessMultimedia` DoFn to capture elements that fail during processing and write them to a dedicated BigQuery error table.
*   **Optimize Client Instantiation**: Modify `ProcessMultimedia` to create the `storage.Client` in the `start_bundle` method.
*   **Add Custom Metrics**: Implement counters for key business events, such as `successful_reports` and `failed_media_uploads`.
