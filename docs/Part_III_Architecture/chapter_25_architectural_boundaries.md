# Chapter 25: Architectural Boundaries

## Boundaries

Software architecture is the art of drawing lines, or boundaries. These boundaries separate software elements and restrict elements on one side from knowing about those on the other.

Some boundaries are drawn early in a project, even before code is written. Others are drawn later. Early boundaries defer decisions and prevent those decisions from polluting the core business logic.

The goal of architecture is to minimize the manpower required to build and maintain the system. Coupling—especially coupling to premature decisions—saps manpower. Premature decisions include choices about frameworks, databases, Web servers, utility libraries, and dependency-injection mechanisms. A good architecture makes these decisions ancillary and deferrable.

## What Lines Do You Draw, and When?

Draw lines to separate things that matter from things that do not. The GUI does not matter to business rules, so there should be a boundary between them. The database does not matter to the GUI or to the business rules, so there should be boundaries between those elements as well.

The database is a tool that business rules can use indirectly. Business rules do not need to know the schema, query language, or other database details. They only need a set of functions that can fetch or save data. This allows the database to sit behind an interface.

The business rules use a `DatabaseInterface` to load and save data. `DatabaseAccess` implements that interface and directs operations to the actual database. In a real application there may be many business-rule classes, database interfaces, and database-access implementations, but they follow the same pattern.

The boundary is drawn across the inheritance or implementation relationship, just below `DatabaseInterface`. The arrows leaving `DatabaseAccess` point away from it, meaning that the business-rule classes do not know that `DatabaseAccess` exists.

At the component level, the database component depends on the business-rules component, while the business rules do not depend on the database. The database component contains translation code that turns calls made by the business rules into database queries. The business rules can therefore use Oracle, MySQL, a document database, or flat files without caring which one is selected.

This boundary allows the database decision to be deferred. The business rules can be written and tested before the database is selected.

## Plug-in Architecture

The boundaries in a plug-in architecture separate the database and GUI from the business rules. The dependency arrows point from the lower-level components toward the higher-level business-rules component.

The GUI and database are plug-ins to the business rules. This pattern can be repeated for many kinds of components. The core business rules remain independent of components that are optional or can be implemented in many forms.

Because the user interface is a plug-in, the system can support Web, client/server, service-oriented, console, or other UI technologies. The database can be replaced with a SQL database, a NoSQL database, a file system, or another technology. Such replacements may not be trivial, but a plug-in structure makes them practical.

## Case Study: FitNesse

The FitNesse project was a simple wiki that wrapped a tool for writing acceptance tests. It was written in Java, and the initial goal was that users should not need to download more than one JAR file. This constraint drove many design decisions.

One decision was to write a small Web server specific to FitNesse. This allowed the project to postpone a Web-framework decision. A small Web server was simple enough to write, and it avoided tying the application to a framework prematurely.

Another decision was to avoid committing to a database. The data-access methods were placed behind an interface named `WikiPage`. At first, the methods were stubbed while the team worked on features that did not require persistence. For several months, the team focused on translating wiki text into HTML without any data store.

When real data access became necessary, the team created `InMemoryPage`, which stored wiki pages in a hash table in memory. This allowed feature development to continue for about a year. Later, a `FileSystemWikiPage` implementation wrote the hash tables to flat files. The team eventually decided that the flat-file solution was sufficient and abandoned the database decision.

A customer later needed MySQL. Because the database boundary already existed, the customer wrote a MySQL implementation of `WikiPage` without changing the business rules. The boundary allowed the team to defer the database decision, experiment with alternatives, and change direction without impeding the original design.

Not having a database for the first 18 months also avoided schema, query, server, password, and connection-time issues. Tests ran quickly because there was no database to slow them down. Drawing boundaries that delayed and deferred decisions saved substantial effort.

## Conclusion

Draw architectural boundaries by partitioning the system into components. Some components contain core business rules. Others are plug-ins that provide necessary functions outside the core business. Arrange the code so that dependency arrows point in one direction—toward the core business.

This is an application of the Dependency Inversion Principle and the Stable Abstractions Principle. Dependencies that cross architectural boundaries must point toward the higher-level side. This is the Dependency Rule of Architecture.
