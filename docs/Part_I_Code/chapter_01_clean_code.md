# Chapter 1: Clean Code

> "'Clean' isn't a ding at anyone. Our notion of 'unclean' is a way of characterizing code that demands more effort from the average developer to understand or maintain." (Jeff Langr)

## There Will Be Code

Some argue that a book about code is behind the times: that code is no longer the issue, and that we should be concerned about AI, large language models (LLMs), and requirements instead. Some have suggested that we are close to the end of code, that soon all code will be generated instead of written, and that programmers won't be needed because businesspeople will generate programs from specifications or prompts.

This is wrong. We will never be rid of code, because code represents the details of the requirements. At some level, those details cannot be ignored or abstracted; they have to be specified. Specifying requirements in such detail that a machine can execute them is programming, and such a specification is code. The level of abstraction of our languages will continue to increase, and the number of domain-specific languages and powerful AIs will continue to grow. This will be a good thing, but it will not eliminate code. All the specifications written in higher-level and domain-specific languages, and all the prompts written to guide a really good AI, will be code. They will still need to be rigorous, accurate, and so formal and detailed that a machine can understand and execute them.

The people who think code will one day disappear are like "mathematicians" who hope to discover a mathematics that does not have to be formal. They hope to create machines that do what they want rather than what they say. Such machines would have to understand us so well that they could translate vaguely specified needs into perfectly executing programs that precisely meet those needs.

This will never happen. Not even humans, with all their intuition and creativity, have been able to create successful systems from the vague feelings of their customers. The discipline of requirements specification has taught us that well-specified requirements are as formal as code and can act as executable tests of that code. Code is the language in which we ultimately express the requirements. We may create languages that are closer to the requirements, and tools that help us parse and assemble those requirements into formal structures, but we will never eliminate the necessary precision and formality. There will always be code.

## Bad Code

Kent Beck wrote in the preface of *Implementation Patterns* that his book "is based on a rather fragile premise: that good code matters." The author disagrees: that premise is one of the most robust, well-supported premises in the craft. We know good code matters because we have had to deal for so long with its lack.

**Anecdote: the company killed by bad code.** In the late 1980s a company wrote a killer app. It was very popular, and lots of professionals bought and used it. Then the release cycles began to stretch. Bugs were not repaired from one release to the next. Load times grew and crashes increased. The author shut the product down in frustration and never used it again. The company went out of business a short time later. Two decades later, the author met one of the company's early employees and asked what had happened. They had rushed the product to market and made a huge mess in the code. As they added more and more features, the code got worse and worse until they could not manage it any longer. It was the bad code that brought the company down.

Programmers of any experience have been significantly impeded by bad code. It is called wading and slogging: we wade through bad code, slog through a morass of tangled brambles and hidden pitfalls, and struggle to find some hint of what is going on while seeing only more senseless code.

So why do we write bad code? Were we trying to go fast, or in a rush? Perhaps we felt we didn't have time to do a good job, or that our boss would be angry if we took time to clean up. Perhaps we were tired of working on the program and wanted it to be over, or we looked at the backlog of other work we had promised and needed to slam this module together to move on. We have all looked at the mess we made and chosen to leave it for another day. We have all felt the relief of seeing a messy program work and decided that a working mess is better than nothing. We have all said we'd go back and clean it up later. But later equals never.

## Attitude

Have you ever waded through a mess so grave that it took weeks to do what should have taken hours? Have you seen what should have been a one-line change made instead in hundreds of different modules? These symptoms are common. Why does good code rot so quickly into bad code?

We have many explanations. We complain that the requirements changed in ways that thwarted the original design. We bemoan schedules that were too tight to do things right. We blame stupid managers, intolerant customers, and useless marketing people. But the fault, dear Dilbert, is not in our stars, but in ourselves. We are unprofessional.

Managers and marketers look to us for the information they need to make promises and commitments, and even when they don't, we should not be shy about telling them what we think. Users look to us to validate how the requirements will fit into the system. Project managers look to us to help work out the schedule. We are deeply complicit in the planning of the project and share a great deal of the responsibility for failures, especially failures caused by bad code.

"But if I don't do what my manager says, I'll be fired." Probably not. Most managers want the truth, even when they don't act like it. Most managers want good code, even when they are obsessing about the schedule. They may defend the schedule and requirements with passion, but that's their job. It's the programmer's job to defend the code with equal passion.

**Analogy: the doctor and handwashing.** Suppose you were a doctor and a patient demanded that you stop all the silly handwashing in preparation for surgery because it was taking too much time. The patient is the boss, and yet the doctor should absolutely refuse to comply, because the doctor knows more than the patient about the risks of disease and infection. It would be unprofessional (never mind criminal) for the doctor to comply. In the same way, it is unprofessional for programmers to bend to the will of managers who don't understand the risks of making messes.

## The Primal Conundrum

Programmers face a conundrum of basic values. All developers with more than a few years of experience know that messes slow them down. And yet all developers feel pressure to make messes in order to meet deadlines. In short, they don't take the time to go fast.

True professionals know that the second part of the conundrum is wrong. You will not make the deadline by making the mess. The mess will slow you down, and it will slow down everyone else who must deal with it. That slowness builds and compounds and forces you to miss deadline after deadline. The only way to make the deadlines, the only way to go fast, is to keep the code clean at all times. The only way to go fast is to go well.

## The Art of Clean Code

If you believe that messy code is a significant impediment, and that the only way to go fast is to keep your code clean, then you must ask: how do I write clean code? It's no good trying to write clean code if you don't know what it means for code to be clean.

Writing clean code requires the disciplined use of myriad little techniques applied through a painstakingly acquired sense of cleanliness. It is always a transformation: nobody writes clean code. We all write messy code. Only those who take the extra step to clean it produce clean code. This follows Kent Beck's law: **First, make it work. Then, make it right.**

## What Is Clean Code?

There are probably as many definitions as there are programmers. The author asked several well-known, deeply experienced programmers for theirs.

### Bjarne Stroustrup: "Clean code does one thing well."

Bjarne Stroustrup is the inventor of C++ and author of *The C++ Programming Language*. This is an old and well-worn maxim. In the 1970s, people said that a module should do one thing, do it well, and do it only. But what does "one thing" mean? In the late 1980s the author wrote a 3,000-line C function named `gi`, which stood for graphic interpreter. If someone had warned him that his long function did more than one thing, he would have replied, "No, it interprets graphics." The problem with the "one thing" rule is that "one thing" is entirely subjective.

### Grady Booch: "Clean code reads like well-written prose."

Grady Booch is the author of many software engineering books. When is the last time you encountered code that read like well-written prose? Code will not read like a Hemingway novel, but it is entirely possible to construct code that reads so nicely that even nonprogrammers can make some sense of it.

### Michael Feathers: "Clean code always looks like it was written by someone who cares."

Michael Feathers is the author of *Working Effectively with Legacy Code*. The words he left out of that quotation were "about you." A programmer goes to the effort of cleaning code because they care about the next person to come along. They care that their code will not mislead, misdirect, or befuddle those who must maintain it. The word that best defines cleanliness is care. The implication is that code that has not been cleaned was written and released carelessly.

### Ward Cunningham: "You know you are working on clean code when each routine you read turns out to be pretty much what you expected."

Ward Cunningham is the inventor of Wiki and Fit, a co-inventor of Extreme Programming, and a motive force behind Design Patterns. Imagine reading code and simply agreeing with it. As you scroll down, you nod in acceptance and affirmation. Reading the code is as fluid as the laminar flow of air over an airplane wing: no turbulence, no clever tricks, no jarring non sequiturs. You simply read and agree, from top to bottom. This may seem like an impossible utopian dream, but it is a dream to strive for.

### Mark Seeman: "Clean code fits in your head."

Mark Seeman is the author of *Code That Fits in Your Head*. His full definition: "Clean code fits in your head. A function fits on a single screen, involves no more than a handful of moving parts, and has good names. It's understandable by peers years after it was written. It minimizes surprises, composes well, and is easy to delete." In some ways, that definition is a summary of the whole book.

### Putting all this together

Clean code reads like well-written prose because it has been carefully partitioned into functions and modules the way prose is partitioned into sentences and paragraphs, each dealing with one thing, one topic, one irreducible concept that flows from one to the next to create the expected whole.

## Why Should We Be Clean?

### Because civilization depends on software

Nearly everything we do in the modern world is mediated by software: smart phones, watches, cars, appliances, thermostats, security systems. You can't cook a hot dog, watch TV, make a phone call, drive to the store, buy or sell anything, pass or enforce a law, or file an insurance claim without software being in the middle of it. Very little happens in our society without the involvement of software. Programmers write the actual rules that run in the machines that govern everything. Without programmers, civilization would grind to a halt overnight.

Are we moral, professional, and responsible enough to bear that responsibility? We have seen hints of catastrophe:

- Software drove two jet airliners into the ground at the speed of sound, killing 346 people.
- Software errors killed dozens and injured hundreds when cars' computers accelerated out of control.
- Knight Capital lost $450M in 45 minutes due to a software error.
- Healthcare.gov stumbled and nearly fell over when it was first launched.

One day, possibly soon, a software error may kill tens of thousands of people in a single incident. When that happens, programmers will be blamed, because it will have been their fingers on the keyboards. Imagine the testimony of expert consultants complaining about thousands of global variables, poorly named arguments, mismanaged and missing semaphores, memory leaks, improperly allocated stacks, heap fragmentation, overdependence on performance over quality, 3,000-line functions, and modules with duplicated code of which some, but not all, had been repaired.

Politicians would pass new laws dictating which languages, platforms, frameworks, processes, signatures, documents, review procedures, courses, and books programmers must use. Those laws would be inconvenient and would do little to improve the situation. So the first reason to clean our code is that our civilization needs us to behave as professionals, and if we fail, our governments will force inconvenient and ineffective rules upon us.

## Productivity

The second reason to clean our code is productivity. Why do we write code that we know will significantly impede us? The answer is always: to go fast. The excuse is "they never give us time," but this is false. The only way to go fast is to go well. The best way to meet the schedule is to do a good job. If you want to go as fast as you can, don't do the things that slow you down. Clean your code.

### The vicious cycle

A messy module slows down everyone who has to deal with it, every time they deal with it. The cost of the mess repeats over and over, whereas the cost of cleaning is a one-time cost. A team that allows messes to persist will gradually slow to a tiny fraction of its potential productivity. The author has seen teams expand their estimates to weeks and months for jobs that ought to take a day or two. The slower the team goes, the more the pressure builds. The more the pressure builds, the more messes are left uncleaned. Each mess impedes the team even more, and the team goes slower still.

### Hiring more people makes it worse

Managers, desperate to increase productivity, hire new people. This has the opposite of the desired effect. The new people, thrown into the mass of messy code, see how things are done and emulate it. Now there are even more people making messes, which drives the cycle faster and drags productivity lower. Managers, astounded that adding people did not increase productivity, may add even more, trying the same thing over and over and expecting different results. In the end, the managers have no choice but to consult the developers to find out why everything is going so slowly.

### The redesign from scratch and the Tiger Team

The developers have known the answer for months, if not years: redesign the whole system from scratch. The managers are shocked and horrified, because the developers have just told them that all their previous work is worthless and must be scrapped, and that the new design won't suffer the same fate. The managers don't believe it and fight the idea, but they have no real choice, and eventually they agree. The developers cheer: no more mess, life will be good.

But that is not what actually happens. The ten best developers, the Tiger Team, are chosen to redesign the system. These are the people who made the mess in the first place. They go into a room to take the project in a "new and beautiful" direction. Meanwhile, the rest of the team is stuck maintaining the old system, because it is part of the business. Bugs have to be fixed and new features added.

Where does the Tiger Team get its requirements? Is there a requirements document anyone seriously trusts? After so many late-night scrambles and midnight modifications, the old requirements are a mess. The requirements are reliably recorded in one place only: the old code. So the Tiger Team pores over the old code trying to figure out what the system actually does, while the maintenance team keeps changing that code by fixing bugs and adding features.

This sets up a race, like Zeno's paradox of Achilles and the tortoise. Every time the Tiger Team reaches where the maintenance team was, the maintenance team has moved ahead. Zeno used that argument to prove that motion was impossible; calculus shows that Achilles does pass the tortoise, but that math doesn't always work for software projects.

The author once worked on a project that was being redesigned from scratch. Ten years later, the "New System" had still not been deployed. Customers had been told years before to expect a glorious new system, but every time the company tried to replace the old systems, customers complained that the new one did not do everything the old one did. The maintenance team was revenue-bearing, so it got all the resources it needed, while the Tiger Team was always limited. The original Tiger Team members were eventually replaced or promoted to other projects, until none of the originals were left. In the end, the company, in utter desperation, told customers they had no choice but to accept the "new" system. The company could not afford to keep funding two development efforts. When the Tiger Team heard the new system was going to be deployed, they stood up in horror: "You can't ship this, it's crap! It's got to be redesigned!"

(The author notes that this story is embellished: it is a composite of his own experiences and the stories his clients told him.)

### Conclusion

Cleaning our code is the best way for a team to remain productive. If we allow the mess to build, we lay the groundwork for the disaster described above. If we keep the code clean, productivity stays high, the development team will not demand a redesign, and managers will not desperately try to increase productivity by adding more and more people.

## Livability

Clean code does not mean Golden Perfection. Golden Perfection is paralyzing and affords no room to move. Clean code is code that you can live with. It is not perfect code. It is like a clean house as opposed to a show house. A show house is a house you cannot live in, because the act of living degrades its show-ability. A clean house is one you can live in without degrading its livability.

Clean code is code that you can maintain, expand, enhance, and evolve without degrading its livability. It is not sparkling and shiny; it looks lived in but cared for. It may not read like Dickens, but it's readable. It may not have the perfect design and architecture, but it is carefully designed. Concepts may not be perfectly isolated, but they are isolated enough.

There might be crumbs on the floor beneath the breakfast counter, a drop of milk on the counter, dog hair on the sofa, pillows in disarray, but none of that degrades the livability of the house, so long as it doesn't get out of hand. Clean code is code that has not gotten out of hand. Those who write and maintain it are not seeking perfection and don't spend endless hours polishing it, but they strive to keep the flotsam and detritus of life from accumulating. They care.

## We Read More Than We Write

In the 1980s and 1990s, editors like Emacs kept track of every keystroke, so you could play back an editing session like a high-speed movie. When the author did this, the vast majority of the playback was scrolling and navigating to other modules. A typical session looked like this: enter the module, scroll to the function needing change, pause to consider options, scroll to the top of the module to check how a variable is initialized, scroll back and start typing, erase what was typed, retype it, erase it again, check a function that calls the function being changed to see how it is called, scroll back and type the same code that was just erased, pause, erase it again, and open a subclass to check whether the function is overridden.

The ratio of time spent reading versus writing is well over 10:1. We are constantly reading old code as part of the effort to write new code, because new code has to be kept consistent with all the old code. Because we read code so much more than we write it, we want reading to be the more efficient operation. And since there is no way to write code without reading it, making code easy to read actually makes it easier to write.

You cannot write code if you cannot read the surrounding code. The code you write today will only be easy to write if the surrounding code is easy to read. So if you want to go fast, if you want to get done quickly, if you want your code to be easy to write, make it easy to read.

## The Boy Scout Rule

It's not enough to write the code well. The code has to be kept clean over time. We have all seen code rot and degrade as time passes, so we must take an active role in preventing that degradation.

The Boy Scouts of America have a simple rule that applies to programming: **Leave the campground cleaner than you found it.** If we all checked in our code a little cleaner than when we checked it out, the code simply could not rot.

The cleanup doesn't have to be big. Do one small random act of kindness: change one variable name for the better, break up one function that's a little too large, eliminate one small bit of duplication, or clean up one composite if statement. On a project where everyone practiced this rule, the code would simply get better as time passed. Continuous improvement is an intrinsic part of professionalism.