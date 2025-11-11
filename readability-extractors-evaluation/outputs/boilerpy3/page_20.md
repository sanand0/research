Robustness
Flexibility
Now, remember, these dimensions are all in opposition to one another. You can spend three days writing a routine which is really beautiful and fast, so you’ve gotten two of your dimensions up, but you’ve spent three days, so the “time spent coding” dimension is way down.
So, when is this worth it? How do we make these decisions? The answer turns out to be very sane, very simple, and also the one nobody, ever, listens to: Start with brevity. Increase the other dimensions as required by testing.
I couldn’t agree more. I’ve given similar advice when I exhorted developers to Code Smaller . And I’m not talking about a reductio ad absurdum contest where we use up all the clever tricks in our books to make the code fit into less physical space. I’m talking about practical, sensible strategies to reduce the volume of code an individual programmer has to read to understand how a program works. Here’s a trivial little example of what I’m talking about:
if (s == String.Empty)
if (s == "")
It seems obvious to me that the latter case is better because it’s just plain smaller. And yet I’m virtually guaranteed to encounter developers who will fight me, almost literally to the death , because they’re absolutely convinced that the verbosity of String.Empty is somehow friendlier to the compiler. As if I care about that. As if anyone cared about that!
It’s painful for most software developers to acknowledge this, because they love code so much, but the best code is no code at all. Every new line of code you willingly bring into the world is code that has to be debugged, code that has to be read and understood, code that has to be supported. Every time you write new code, you should do so reluctantly, under duress, because you completely exhausted all your other options. Code is only our enemy because there are so many of us programmers writing so damn much of it. If you can’t get away with no code, the next best thing is to start with brevity.
If you love writing code – really, truly love to write code – you’ll love it enough to write as little of it as possible.
software development concepts programming languages technical practices
Written by Jeff Atwood
Indoor enthusiast. Co-founder of Stack Overflow and Discourse. Disclaimer: I have no idea what I'm talking about. Let's be kind to each other. Find me https://infosec.exchange/@codinghorror
✉️ Subscribe
❗ Something's gone wrong. Please try again.
✅ Success! Check your inbox (and your spam folder, just in case).
