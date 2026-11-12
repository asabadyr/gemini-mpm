---
trigger: glob
globs: "**/*.ts, **/*.tsx, **/*.js, **/package.json, **/tsconfig.json"
description: "TypeScript and Node.js guardrails: unknown boundary narrowing, unhandled promise/listener leaks, AbortController timeouts, memory streaming, and unconditional API auth."
---

# Domain Pack: TypeScript & Node.js (`22`)

## Critical TypeScript / Node.js Guardrails
| Area | Trap | Mandatory Practice |
|---|---|---|
| **Boundary Validation (`🔴`)** | Casting external JSON, webhook payloads, DB docs, or `catch (e)` directly via `as MyType` or `any` | Treat I/O boundaries as `unknown`; narrow with runtime validators (`zod`, `typebox`, explicit guards) and check `e instanceof Error` |
| **Promise & Event Hygiene (`🔴`)** | Floating promises, `async` callbacks passed to `forEach` / `EventEmitter.on` without `.catch`, or unbounded `.on()` listeners per request/socket | `await` or explicitly `.catch()` every promise; pair `.on()` with `.off()` / `.once()` / `AbortSignal` cleanup to prevent listener & heap leaks |
| **Outbound Timeouts (`🔴`)** | `fetch` / `axios` / RPC / child-process calls without cancellation deadlines | Attach `AbortSignal.timeout(ms)` / `AbortController` (`clearTimeout` in `finally`) on all external I/O |
| **Stream & Buffer Memory** | Buffering large uploads, archives, or DB cursors in V8 heap (`Buffer.concat` / `res.arrayBuffer()`) | Stream large payloads via `stream/promises` `pipeline()` or bounded temp files so `pipeline()` destroys both ends on error |
| **Unconditional Server Auth (`🔴`)** | Skipping auth, signature verification, or rate/tenant checks when `NODE_ENV !== 'production'` | Enforce authn/authz and tenant scoping unconditionally in route/middleware handlers; mock auth tokens in tests instead of weakening prod routes |
| **Dependency & Lockfile Safety** | Upgrading transitive packages blindly or mixing `npm` / `yarn` / `pnpm` in the same repo | Match the lockfile already tracked (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`); verify `overrides`/`resolutions` when fixing CVEs |
| **Discriminated Unions & Exhaustive Narrowing** | Stringly-typed `if/else` chains or unsafe `instanceof` with raw objects | Use tagged/discriminated unions + `assertNever(x: never)` switch exhaustiveness over unsafe type checks or deeply nested conditionals |
| **Constructor/Factory Interface DI & Layering** | Mutable module-level singletons or tight coupling to HTTP frameworks | Inject typed interfaces into pure domain services decoupled from Express/Fastify/Nest/Hono req/res controllers; strictly ban global mutable singletons |
| **Module Graph & Barrel-Import Hygiene** | Deep `index.ts` barrel re-exports that create circular `undefined` bindings and bundle bloat | Prefer direct module imports over deep `index.ts` barrel exports; keep module graph shallow and acyclic to prevent obscure runtime initialization failures |
