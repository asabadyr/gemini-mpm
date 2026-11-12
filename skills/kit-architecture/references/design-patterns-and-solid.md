# Design Patterns and SOLID Principles

## Core Principle
**"Patterns solve concrete structural smells; no problem => no pattern."** 

Before applying any pattern, calibrate against the context:
- **Production Mainline**: Requires strict decoupling, testability, and adherence to SOLID.
- **Prototype/Scratch**: Emphasizes speed; tolerate minor coupling, but avoid deep anti-patterns.

## SOLID & OOP Foundations Table

| Principle | Description | Implementation Guidelines |
| :--- | :--- | :--- |
| **SRP** (Single Responsibility) | A class should have one reason to change. | Separate domain logic from persistence and transport. |
| **OCP** (Open/Closed) | Open for extension, closed for modification. | Use interfaces/protocols to add behavior without editing core files. |
| **LSP** (Liskov Substitution) | Subtypes must be substitutable for base types. | Avoid throwing `NotImplementedError` in subclasses. |
| **ISP** (Interface Segregation) | Clients shouldn't depend on methods they don't use. | Favor small, focused interfaces (e.g., 1-3 methods) over fat ones. |
| **DIP** (Dependency Inversion) | Depend on abstractions, not concretions. | Inject dependencies via Constructor DI; use Ports & Adapters. |

### General OOP Guidelines
- **Composition over Inheritance**: Keep inheritance depth `<=2`. Use composition and interfaces to share behavior.
- **Constructor DI**: Always inject dependencies through the constructor for testability. Avoid global state or singletons.
- **Immutable Boundary DTOs**: Data crossing system boundaries (network, database) should be mapped to immutable DTOs/records.

## Decision Tree

Use this diagnostic tree to map architectural smells to appropriate patterns:

- **Untestable tight coupling** ➔ **Constructor Dependency Injection (DI)**
- **Scattered business rules / Mixed concerns** ➔ **Service Layer** (Domain Facade)
- **Persistence leakage into domain** ➔ **Repository Pattern**
- **External 3rd-party churn / API changes** ➔ **Adapter / Anti-Corruption Layer (ACL)**
- **`3+` repeated type-tag switches** ➔ **Strategy / Handler Registry**
- **Complex multi-variant construction** ➔ **Factory / Builder**
- **Cyclic `A->B->C->A` calls** ➔ **Domain Events / Mediator**
- **Cascading slow upstream dependencies** ➔ **Circuit Breaker / Bulkhead**
- **Repeated cross-cutting boilerplate (logs, auth)** ➔ **Decorator / Middleware**

## Code-Smell -> Pattern Diagnostic Matrix

| Smell / Symptom | Diagnosis | Recommended Pattern |
| :--- | :--- | :--- |
| Hardcoded `new Database()` inside Domain | Tightly coupled I/O | Constructor DI + Repository |
| Fat controller processing JSON & DB logic | Missing boundary | Service Layer + DTOs |
| Endless `if/else` on user types | Missing polymorphism | Strategy Pattern |
| Churn from 3rd-party SDK updates | Domain infected by vendor | Anti-Corruption Layer |
| 10 parameters in a constructor | Too many dependencies | Builder or Facade |

## Anti-Patterns / Red Flags

Avoid these common traps when trying to implement clean architecture:

1. **Service Locator hidden dependencies**: Do not pass a `Container` or `Locator` around. It obscures what dependencies a class actually needs. Use explicit Constructor DI.
2. **Anemic pass-through wrappers**: Don't create Repositories or Services that just forward 1:1 to an ORM without adding any domain value. If it's a CRUD prototype, just use the ORM.
3. **Premature abstract factory hierarchies**: Applying `AbstractWidgetFactory` on a `<200` LOC script is speculative YAGNI. Keep it simple until variation is actually needed.
4. **Wrong-DRY cross-domain coupling**: Do not deduplicate code that just *happens* to look structurally similar if it belongs to different business domains (e.g., `User` and `Product` having a `name`). Let them evolve independently.


## Deep Dive: Composition Over Inheritance

One of the most violated principles in legacy codebases is the overuse of inheritance. Deep inheritance trees (depth > 2) lead to the Fragile Base Class problem, where a change in a base class inadvertently breaks distant subclasses. 

To mitigate this:
- **Favor Interfaces/Protocols:** Define what an object *does* rather than what it *is*.
- **Use Decorators:** If you need to add behavior to a class, wrap it in a decorator rather than subclassing it. This allows behaviors to be composed at runtime.
- **Extract Strategies:** If a subclass only exists to override a specific algorithm, extract that algorithm into a Strategy object and inject it into the base class.

## Deep Dive: The Repository Pattern Done Right

The Repository Pattern is frequently misunderstood, leading to anemic wrappers around ORMs. A true repository operates at the domain level, dealing exclusively in Domain Models, not database rows or Active Records.

- **Interface in Domain, Implementation in Infrastructure:** The repository interface must be defined in the Domain layer to invert the dependency. The implementation lives in the Infrastructure layer.
- **Collection-Like Interface:** Methods should resemble a collection (e.g., `add`, `remove`, `findById`), abstracting away the fact that it's backed by a database.
- **No Persistence Logic in Domain:** The domain model should not know how to save itself.

By rigidly applying these guidelines, you guarantee a testable, decoupled architecture capable of scaling and adapting to changing requirements over time.