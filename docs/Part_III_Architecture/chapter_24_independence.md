# Chapter 24: Independence

A good architecture must support:

- The use cases of the system.
- The operation of the system.
- The development of the system.
- The deployment of the system.

## Use Cases

The architecture of a system must support its intent. If the system is a shopping cart application, its architecture must support shopping cart use cases. This is the first priority of architecture.

Architecture does not wield much influence over the behavior of a system. There are few behavioral options that architecture can leave open. But architecture can clarify and expose behavior so that the intent of the system is visible at the architectural level.

A shopping cart application with a good architecture will look like a shopping cart application. Its use cases will be plainly visible in the structure of the system. Developers will not have to hunt for behaviors because those behaviors will be first-class elements at the top level. They will be classes, functions, or modules with prominent positions and names that clearly describe their purpose.

## Operation

Architecture plays a more substantial role in supporting system operation. If a system must handle 100,000 transactions per second, the architecture must support that throughput and the required response time. If the system must query large data sets in milliseconds, the architecture must allow that operation.

For some systems, this means arranging processing elements as services that run in parallel on many servers. For others, it means lightweight threads sharing the address space of a single process. Still others need only a few processes in isolated address spaces, or a simple monolithic program in one process.

A good architecture leaves this choice open. A system written as a monolith and dependent on that monolithic structure cannot easily be upgraded to multiple processes, threads, or services. An architecture that isolates its components and does not assume how they communicate is much easier to move through the spectrum of threads, processes, and services as operational needs change.

## Development

Architecture plays a significant role in supporting the development environment. Conway’s law and the Single Responsibility Principle apply here. A system developed by many teams with many concerns needs an architecture that facilitates independent work without interference.

This is accomplished by partitioning the system into well-isolated, independently developable components. Those components can then be allocated to teams that work independently.

## Deployment

Architecture also plays a major role in the ease of deployment. The goal is immediate deployment. A good architecture does not rely on dozens of configuration scripts, property-file tweaks, or manual creation of directories and files. It helps the system become deployable after each build.

Again, this is achieved by partitioning and isolating components, including the master components that tie the system together and ensure that each component is started, integrated, and supervised properly.

## Leaving Options Open

A good architecture balances all these concerns with a component structure that satisfies them together. In practice, this is difficult because we often do not know all the use cases, operational constraints, team structures, or deployment requirements. Even when we know them, they change throughout the system’s life cycle.

Principles of architecture can help even when the goals are unclear. They help us partition systems into well-isolated components and leave as many options open as possible for as long as possible. A good architecture makes the system easy to change in all the ways it must change by leaving options open.
