# Chapter 17: AIs, LLMs, and God Knows What

## God Knows What

In the late 1940s, Grace Hopper wrote her first lines of code. Each line looked something like this:

```text
| 521|   53|   2|
```

Each digit represented a particular hole on a paper tape that looked like this:

Each row of that paper tape was an instruction for the Harvard Mark I to execute. The instructions were very simple —something like “Add Register 10 to Register 12.” I’ll leave you to imagine just how hard programming was back then. Within a few years, it became clear that a computer program could be used to generate codes like that from a more abstract textual representation like “add 10, 12.” Hopper called this automatic programming. Before a decade had passed from Hopper’s first line of code, John Backus and his team had produced the first Fortran compiler, which used statements like “a = b + c.” Algol came a handful of years later, and within a decade, Dahl and

Nygaard had created Simula-67, the first object-oriented language. C, Unix, Smalltalk, and C++ were born within a few years. And within the next few, Java and C# appeared. At each one of those transitions, the productivity of programmers increased. The first leap in productivity was the greatest. In the ’50s, the productivity of programmers using a Fortran-like compiler was shown to be 45 times that of programmers using machine code. Each productivity leap thereafter was smaller than the previous. C was probably twice that of Fortran. C++ was likely a 20% improvement on C. Java/C# was perhaps on the order of another 20%. Ruby/Python are likely 20% better than Java, and Clojure likely adds another 10%. Each of these transitions in language was driven by an increase in abstraction. Each new language in that sequence was another step further removed from Grace Hopper’s holes in that paper tape. And each of those steps was accompanied by the fear that programming was being ruined. Yes, you read that correctly. At every stage, there were those who predicted the end of programming. Books were published that predicted the doom of the industry. They claimed that programmers would become as rare as dodo birds. Every time we made programming a little easier, those of us who were invested in the current complexity were liable to fear that unwashed masses would take our jobs. And so we predicted the doom of the profession. And every time, those fears and predictions were the exact opposite of the actual outcomes. With every new advance, the number of projects and the demand for programmers grew.

Today, we face yet another such transition—the transition of AI. And there is, of course, rampant fear that programming is dead and that programmers will soon go extinct. Baloney! This is just another increase in the level of abstraction of our languages—another step away from the holes in the paper tape. And as we come to grips with it, the number of projects and the demand for programmers will continue to grow.

## Programming by Prompt

This is a very new technology, and we don’t have a good handle on how to use it yet. This is reminiscent of our first forays into Java and the Web. Does anybody remember applets? It took several years before we worked out the rudiments of how to use Java/C# well. It took several more to refine those rudiments. The same happened with Ruby and Python. At first we stumbled and bumbled around, and then we gradually figured out the best ways to proceed. And believe me, when Fortran first came out, there was plenty of fear, anguish, doubt, and bumbling and stumbling. And so it will be with AIs. At this point, we have no idea what to do. We are just now barely able to bumble and stumble our way to write programs with prompts. We have no idea how to do it well. So, for example, consider the following prompt that I gave to Grok.

```text
write a clojure program that finds all sentences

in a given file that contain a given substring.

Choose one of those sentences at random and find the next word in the substring, or a . if no word follows.

Add the found word to the substring and remove the

first if the substring is longer than three words.

Repeat the entire process until the substring ends in a . or has exceeded 50 words.

Accumulate all the words that were found and return them appended to the initial substring.
```

Here’s the code that Grok generated. It works—after a fashion.


It is easy to be impressed by this. I certainly am. But it also terrifies me. I am not terrified by the power of the AI to generate code. I am terrified by the structure of that horrible prompt. Look carefully at that prompt. What is the definition of sentence? What is the definition of word? What does the clause the found word mean? Are those dot characters punctuation or nouns? What does it mean to accumulate words? Yes, Grok figured all this out well enough for this little experiment. But the program that resulted was by no means ready for production. It makes lots of dumb little mistakes, most of which have to do with the questions I raised in the previous paragraph. Here, for example, is a sample run: >clj -M -m markov

~/Documents/Books/Clean\ Code\ 2ded\ 20250311.txt "The Single"

> The Single Responsibility Principle, and the Dependency

relationships and wind up back at that first solution, the one wit

the project you were working on   it every day   business and persona

Notice the double spaces in the third and fourth lines. Why is it doing that? I could fix those mistakes by adding clarification to the prompt. For example, I might add: Make sure all accumulated words are separated by just one space.

But there are a number of problems with this approach. First, I haven’t figured out why those double spaces are there, so this change to the prompt is just a patch to fix the

symptom. Second, am I sure that the clause all accumulated words will properly refer to the return value?

I could try it to find out; but that causes another problem. With each new change to the prompt, Grok regenerates the program from scratch as opposed to modifying the existing program. With all the ambiguities in the prompt, how can I be sure that the regenerated program doesn’t break something that worked in the previous one? Will it use the same definitions of word and sentence that it did before? Will it interpret the found word the same as it did before? Given the statistical and fuzzy nature of the LLM algorithms, there’s a good chance it won’t! Here is what Grok generated for that modified prompt. Notice that the two programs look like they were written by two different programmers.


This new program solves the double-space problem but creates a new problem at the end of the sentence. It also doesn’t deal with uppercase and lowercase very well.

> clean code is hard Writing a system that handles one user at a time

## Infancy

These are problems related to the infancy of the approach. In order to effectively program large systems by prompt, we are going to need AI tools that allow for incremental

changes. We are also going to need ways to eliminate the ambiguities in our prompts. In short, we are going to need a formalism—a prompt language that is unambiguous and precise and that cannot be misinterpreted by the statistical and fuzzy nature of the LLM algorithm. We’ll need to come up with a way to precisely say what we mean. We’ll also need to come up with a way to mean what we say. Or, in other words, even if we have a perfectly precise language, it is easy to precisely say something that is wrong. To ensure that our precise statements are accurate descriptions of our intent, we should state our intent in at least two different ways (just as I did in this paragraph!). When you say something in two different ways, you are overloading the concept you are trying to communicate. Such overloading is a way to ensure that any error in either of the two statements will be detected by the other. We error-prone humans absolutely require overloading. Overloading is the strategy behind double-entry bookkeeping and the testing disciplines described in earlier chapters. It would be supremely irresponsible to trust a single set of precise statements written by a human if those statements aren’t overloaded. What we are going to need is a way to create precise and overloaded prompts and a way to quickly verify their consistency.

## A SWAG

So let me make a Scientific Wild-Axx Guess. Imagine a prompt language that contains formal definitions and constraints overloaded by a set of BDD-style Given-When-Then scenarios.

Let’s give that a try with a slightly simpler problem. Notice how much it looks like COBOL. That similarity might give us pause.

### Language: Clojure

### Name: Markov

Command-line arguments:

- `f`: a text file.
- `s`: a text string.

Definitions: Word: A string of alphabetic characters.

Sentence: One or more words separated by spaces and ending with a period, question mark, or exclamation mark.

Constraints:

Ignore case in all comparisons.

Description:

Find all sentences in f that contain s.

Choose a sentence c at random with equal probability.

Return the word in c that immediately follows s;

    if none return a period.

Scenarios to be tested with speclj:

Given f contains the following lines:

Oh, Hello there Bob, how are you today? I'm fine.

Hello there Bill, I trust you are well.      How's the wife?

Ah yes     hello there John   great day!   Kowabunga!

Ah yes, hello there John, great day!     Kowabunga!

When s is "not in any sentence"

Then return "."

When s is "hello"

Then return "there"

When s is "are well"

Then return "."

When s is "hello there"

Then return "Bob", "Bill", or "John". Assert a uniform distribution after 100 iterations.

Grok was quite happy to generate an implementation and corresponding tests from the scenarios.


Despite a valiant effort by Grok, the generated tests do not pass. That should drive home just how important it is to overload a prompt with testing scenarios!

Failures:

 1) Markov returns 'there' when searching for 'hello'

    Expected: "there"

            got: "." (using =)

 2) Markov returns period when searching for 'are well'

    Expected: "."

            got: "i" (using =)

 3) Markov returns Bob, Bill, or John for
    'hello there' with uniform distribution

    Expected: 3

         got: 1 (using =)

Debugging the code is relatively simple; but can you debug the prompt? And even if you can “fix” the prompt, are you sure it will generate code and tests that pass if you apply the prompt more than once? The fact that Grok wrote the tests and yet could not use them to infer the desired behavior exposes the limitation of the LLM approach. LLMs are statistical in nature; they create their responses through probability and not inference. It is true that many inferences are trained into the statistical model; but the evaluation of the prompt does not infer in real time. Inference is the primary operation of reason. If LLMs do not actively infer, then LLMs do not reason! If you debug the code that Grok produced, you will find that Grok apparently ignored the provided definition of “word” and did not properly interpret the case insensitivity constraint. The fact that Grok got confused by a formal prompt overloaded with test scenarios is not encouraging. It seems obvious, at least to me, that without overloaded formality, the prospect of using AIs to write our systems is doomed to spectacular failure. After all, programming is formal, and humans require overloading.

## Conclusion

In the end, I expect that the LLMs and AIs will improve to the point that long, formal specifications will be within their grasp. I also expect that we programmers will design formal and overloaded specification languages that the AIs can consume to produce complex systems.

And who will learn and apply these formalisms? Who will provide the ability to reason that the AIs lack? Programmers, of course. We programmers will become the lawyers of AI, responsible (as we always have been) to reason through and draw up the precise and accurate formal requirements and contracts for the applications our clients need.

In this part of the book, we’re going to raise our perspective slightly above coding issues and look at the principles of clean design. You’ll still see plenty of code—but the level will continuously rise as each chapter goes by. We’ll cover the basics of lower-level boundaries and systems, Kent Beck’s rules of simple design, the SOLID principles, and the principles of component design. Portions of the following chapters are edited and abridged excerpts from my books Clean Craftsmanship and Clean Architecture.
