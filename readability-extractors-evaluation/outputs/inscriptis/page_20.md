      * Archive
      * Discourse
      * Stackexchange
      * Markdown
      * Reading List
      * About Me
      * Shop

  The Best Code is No Code At All

      Jeff Atwood

        30 May 2007 — 3 min read — Comments

  Rich Skrenta writes that code is our enemy.

  Code is bad. It rots. It requires periodic maintenance. It has bugs that need to be found. New features mean old code has to be adapted. The more code you have, the more places there are for bugs to hide. The longer checkouts or compiles take. The longer it takes a new employee to make sense of your system. If you have to refactor there’s more stuff to move around.

  Code is produced by engineers. To make more code requires more engineers. Engineers have n^2 communication costs, and all that code they add to the system, while expanding its capability, also increases a whole basket of costs. You should do whatever possible to increase the productivity of individual programmers in terms of the expressive power of the code they write. Less code to do the same thing (and possibly better). Less programmers to hire. Less organizational communication costs.

  Rich hints at it here, but the real problem isn’t the code. The code, like a newborn babe, is blameless and innocent the minute it is written into the world. Code isn’t our enemy. You want to see the real enemy? Go look in the mirror. There’s your problem, right there.

  As a software developer, you are your own worst enemy. The sooner you realize that, the better off you’ll be.

  I know you have the best of intentions. We all do. We’re software developers; we love writing code. It’s what we do. We never met a problem we couldn’t solve with some duct tape, a jury-rigged coat hanger, and a pinch of code. But Wil Shipley argues that we should rein in our natural tendencies to write lots of code:

  The fundamental nature of coding is that our task, as programmers, is to recognize that every decision we make is a trade-off. To be a master programmer is to understand the nature of these trade-offs, and be conscious of them in everything we write.

  In coding, you have many dimensions in which you can rate code:

    * Brevity of code
    * Featurefulness
    * Speed of execution
    * Time spent coding
    * Robustness
    * Flexibility

  Now, remember, these dimensions are all in opposition to one another. You can spend three days writing a routine which is really beautiful and fast, so you’ve gotten two of your dimensions up, but you’ve spent three days, so the “time spent coding” dimension is way down.

  So, when is this worth it? How do we make these decisions? The answer turns out to be very sane, very simple, and also the one nobody, ever, listens to: Start with brevity. Increase the other dimensions as required by testing.

  I couldn’t agree more. I’ve given similar advice when I exhorted developers to Code Smaller. And I’m not talking about a reductio ad absurdum contest where we use up all the clever tricks in our books to make the code fit into less physical space. I’m talking about practical, sensible strategies to reduce the volume of code an individual programmer has to read to understand how a program works. Here’s a trivial little example of what I’m talking about:

  
  if (s == String.Empty)
  if (s == "") 
  

  It seems obvious to me that the latter case is better because it’s just plain smaller. And yet I’m virtually guaranteed to encounter developers who will fight me, almost literally to the death, because they’re absolutely convinced that the verbosity of String.Empty is somehow friendlier to the compiler. As if I care about that. As if anyone cared about that!

  It’s painful for most software developers to acknowledge this, because they love code so much, but the best code is no code at all. Every new line of code you willingly bring into the world is code that has to be debugged, code that has to be read and understood, code that has to be supported. Every time you write new code, you should do so reluctantly, under duress, because you completely exhausted all your other options. Code is only our enemy because there are so many of us programmers writing so damn much of it. If you can’t get away with no code, the next best thing is to start with brevity.

  If you love writing code – really, truly love to write code – you’ll love it enough to write as little of it as possible.

    software development concepts programming languages technical practices

    Written by Jeff Atwood

    Indoor enthusiast. Co-founder of Stack Overflow and Discourse. Disclaimer: I have no idea what I'm talking about. Let's be kind to each other. Find me https://infosec.exchange/@codinghorror

  ✉️ Subscribe

  ⏲️ Busy signing you up.

  ❗ Something's gone wrong. Please try again.

  ✅ Success! Check your inbox (and your spam folder, just in case).

        ← Previous Post

        Let’s Build a Grid

        Next Post →

        Gates and Jobs, Then and Now

    Related posts

        Complaint-Driven Development

        If I haven’t blogged much in the last year, it’s because we’ve been busy building that civilized discourse construction kit thing I talked about. (Yes, that’s actually the name of the company. This is what happens when you put me in charge of naming things. Pinball

        By Jeff Atwood · 18 Feb 2014
        Comments

        The Rule of Three

        Every programmer ever born thinks whatever idea just popped out of their head into their editor is the most generalized, most flexible, most one-size-fits all solution that has ever been conceived. We think we’ve built software that is a general purpose solution to some set of problems, but we

        By Jeff Atwood · 18 Jul 2013
        Comments

        Today is Goof Off at Work Day

        When you’re hired at Google, you only have to do the job you were hired for 80% of the time. The other 20% of the time, you can work on whatever you like – provided it advances Google in some way. At least, that’s the theory. Google’s 20

        By Jeff Atwood · 01 Aug 2012
        Comments

        Coding Horror: The Book

        If I had to make a list of the top 10 things I’ve done in my life that I regret, “writing a book” would definitely be on it. I took on the book project mostly because it was an opportunity to work with a few friends whose company I

        By Jeff Atwood · 10 Jul 2012
        Comments

    Recent Posts

        The Road Not Taken is Guaranteed Minimum Income

        The dream is incomplete until we share it with our fellow Americans.

        By Jeff Atwood · 20 Mar 2025
        Comments

        Let's Talk About The American Dream

        A few months ago I wrote about what it means to stay gold — to hold on to the best parts of ourselves, our communities, and the American Dream itself. But staying gold isn’t passive. It takes work. It takes action. It takes hard conversations that ask us to confront

        By Jeff Atwood · 06 Mar 2025
        Comments

        Stay Gold, America

        We are at an unprecedented point in American history, and I'm concerned we may lose sight of the American Dream.

        By Jeff Atwood · 07 Jan 2025
        Comments

        The Great Filter Comes For Us All

        With a 13 billion year head start on evolution, why haven’t any other forms of life in the universe contacted us by now? (Arrival is a fantastic movie. Watch it, but don’t stop there – read the Story of Your Life novella it was based on for so much

        By Jeff Atwood · 02 Dec 2024
        Comments
  I’m feeling unlucky... 🎲 See All Posts
        * Archive
        * Reading List
        * About Me
        * Shop
        Powered by Ghost · Themed by Obox