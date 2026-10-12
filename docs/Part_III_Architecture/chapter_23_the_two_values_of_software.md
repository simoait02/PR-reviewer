# Chapter 23: The Two Values of Software

## The Value of Software

There are two values to software: the value of its behavior and the value of its structure. The second is the greater of the two because it is what makes software soft.

Software was invented because we needed a way to change the behavior of machines quickly and easily. That flexibility depends critically on the shape of the system, the arrangement of its components, and the way those components are interconnected.

## Keeping Options Open

The way to keep software soft is to leave as many options open as possible, for as long as possible. The options we need to leave open are the details that do not matter to the policy of the system.

All software systems can be decomposed into two major elements: policy and detail. The policy element embodies the business rules and procedures. The policy is where the true value of the system lives.

Details are the things needed to enable humans, other systems, and programmers to communicate with the policy, but that do not affect the policy’s behavior. These include I/O devices, databases, Web systems, servers, frameworks, and communication protocols.

The goal of architecture is to give the system a shape that recognizes policy as the most essential element while making details irrelevant to that policy. This allows decisions about details to be delayed and deferred.

For example:

- It is not necessary to choose a database early in development. High-level policy should not care whether the database is relational, distributed, hierarchical, or a set of flat files.
- It is not necessary to choose a Web server early. High-level policy should not know that it is being delivered over the Web. If policy is unaware of HTML, CSS, AJAX, JSP, JSF, and other Web details, the Web system can be selected much later. The system might not need to be delivered over the Web at all.
- It is not necessary to adopt REST early. High-level policy should be agnostic about the interface to the outside world. The same applies to microservices, service-oriented architecture, and UI frameworks.
- It is not necessary to adopt a dependency-injection framework early. High-level policy should not care how dependencies are resolved.

If you can develop high-level policy without committing to surrounding details, you can delay decisions about those details for a long time. The longer you wait, the more information you have with which to make the decisions properly.

Leaving options open also makes experiments possible. If a working portion of policy is agnostic about the database, you can connect it to several databases to check applicability and performance. The same is true of Web systems, frameworks, and even the Web itself.

The longer you leave options open, the more experiments you can run and the more information you will have when decisions can no longer be deferred. Even when someone else has already made a commitment to a database, Web server, or framework, it is useful to shape the system as if the decision had not been made. Such decisions can change unexpectedly.

A good architecture maximizes the number of decisions not made.
