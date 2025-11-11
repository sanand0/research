I test in prod – Increment: Testing

# [Increment](/)

[NEW

### Buy the print edition](https://store.increment.com/)

* [Issues](/issues/)
* [Topics](/topics/)
* [Store](https://store.increment.com/)
* [About](/about/)

![I test in prod](https://images.ctfassets.net/3njn2qm7rrbs/6xofBuoTVh1uDLg3Ot9oNd/f0e1599bb3cb9a3186805ed56b5b251f/cover-2000-cc97eb23.jpeg?w=1000)

#### [Charity Majors](#authors)

# I test in prod

Testing in production is a superpower. It’s our inability to acknowledge it that’s the trouble.

[Part of

Issue 10 August 2019

## Testing](/testing/)

“I don’t always test my code,” muses The Most Interesting Man in the World in one of the sturdiest tech memes of all time, “but when I do, I test in production.”

I’ve been laughing at that meme since I first saw it back in . . . 2013? It’s more than funny. It’s hilarious!

Since then, “test in prod” has become shorthand for all the irresponsible ways we interact with production services or cut corners in our rush to ship, and for this I blame The Most Interesting Man and his irresistible meme.

Because, frankly, all of us test in production all the time. (At least, the good engineers do.) It’s not inherently bad or a sign of negligence—it’s actually an unqualified good for engineers to be interacting with production on a daily basis, observing the code they wrote as it interacts with infrastructure and users in ways they could never have predicted.

Testing in production is a superpower. It’s our inability to acknowledge that we’re doing it, and then invest in the tooling and training to do it safely, that’s killing us.

At its core, testing is about reducing uncertainty by checking for known failures, past failures, and predictable failures—your known unknowns, as it were. If I run a piece of deterministic code in a particular environment, I expect the result to succeed or fail in a repeatable way, and this gives me confidence in that code for that environment. Cool.

Modern systems are built out of these testable building blocks, but also:

![](https://images.ctfassets.net/3njn2qm7rrbs/1NR5fVwqGtDKqUSou2q1Ys/445faf001e9cfa4d10d7da71607112ff/spot-1000-92e367dd.jpeg?w=500)

* Many concurrent connections
* A specific network stack with specific tunables, firmware, and NICs
* Iffy or nonexistent serializability within a connection
* Race conditions
* Services loosely coupled over networks
* Network flakiness
* Ephemeral runtimes
* Specific CPUs and their bugs; multiprocessors
* Specific hardware RAM and memory bugs
* Specific distro, kernel, and OS versions
* Specific library versions for all dependencies
* Build environment
* Deployment code and process
* Runtime restarts
* Cache hits or misses
* Specific containers or VMs and their bugs
* Specific schedulers and their quirks
* Clients with their own specific back-offs, retries, and time-outs
* The internet at large
* Specific times of day, week, month, year, and decade
* Noisy neighbors
* Thundering herds
* Queues
* Human operators and debuggers
* Environment settings
* Deaths, trials, and other real-world events

When we say “production,” we typically mean the constellation of all these things and more. Despite our best efforts to abstract away such pesky low-level details as the firmware version on your eth0 card on an EC2 instance, I’m here to disappoint: You’ll still have to care about those things on unpredictable occasions.

And if testing is about uncertainty, you “test” any time you deploy to production. Every deploy, after all, is a unique and never-to-be-replicated combination of artifact, environment, infra, and time of day. By the time you’ve tested, it has changed.

> Once you deploy, you aren’t testing code anymore, you’re testing systems.

Once you deploy, you aren’t testing code anymore, you’re testing systems—complex systems made up of users, code, environment, infrastructure, and a point in time. These systems have unpredictable interactions, lack any sane ordering, and develop emergent properties which perpetually and eternally defy your ability to deterministically test.

The phrase “I don’t always test, but when I do, I test in production” seems to insinuate that you can only do one or the other: test before production or test in production. But that’s a false dichotomy. All responsible teams perform both kinds of tests.

Yet we only confess to the first type of testing, the “responsible” type. Nobody admits to the second, much less talks about how we could do it better and more safely. Nobody invests in their “test in prod” tooling. And that’s one reason we do it so poorly.

## “Worked fine in dev; ops problem now.”

For most of us, the scarcest resource in the world is engineering cycles. Any time we choose to do something with our time, we implicitly choose not to do hundreds of other things. Selecting what to spend our precious time on is one of the most difficult things any team can do. It can make or break a company.

As an industry, we’ve systematically underinvested in tooling for production systems. The way we talk about testing and the way we actually work with software has centered exclusively on preventing problems from ever reaching production. Admitting that some bugs will make it to prod no matter what we do has been an unspeakable reality. Because of this, we find ourselves starved of ways to understand, observe, and rigorously test our code in its most important, luteal phase of development.

> Admitting that some bugs will make it to prod no matter what has been an unspeakable reality.

Let me tell you a story. In May 2019, we decided to upgrade Ubuntu for the entire Honeycomb production infrastructure. The Ubuntu 14.04 AMI was about to age out of support, and it hadn’t been systematically rolled out since I first set up our infra way back in 2015. We did all the responsible things: We tested it, we wrote a script, we rolled it out to staging and dogfood servers first. Then we decided to roll it out to prod. Things did not go as planned. (Do they ever?)

There was an issue with cron jobs running on the hour while the bootstrap was still running. (We make extensive use of auto-scaling groups, and our data storage nodes bootstrap from one another.) Turns out, we had only tested bootstrapping during 50 out of the 60 minutes of the hour. Naturally, most of the problems we saw were with our storage nodes, because of course they were.

There were issues with data expiring while rsync-ing over. Rsync panicked when it did not see metadata for segment files, and vice versa. There were issues around instrumentation, graceful restarts, and namespacing. The usual. But they are all great examples of responsibly testing in prod.

We did the appropriate amount of testing in a faux environment. We did as much as we could in nonproduction environments. We built in safeguards. We practiced observability-driven development. We added instrumentation so we could track progress and spot failures. And we rolled it out while watching it closely with our human eyes for any unfamiliar behavior or scary problems.

Could we have ironed out all the bugs before running it in prod? No. You can never, ever guarantee that you have ironed out all the bugs. We certainly could have spent a lot more time trying to increase our confidence that we had ironed out all possible bugs, but you quickly reach a point of fast-diminishing returns.

We’re a startup. Startups don’t tend to fail because they moved too fast. They tend to fail because they obsess over trivialities that don’t actually provide business value. It was important that we reach a reasonable level of confidence, handle errors, and have multiple levels of fail-safes (i.e., backups).

## “What do we say to the god of downtime? Not today.”

We conduct experiments in risk management every single day, often unconsciously. Every time you decide to merge to master or deploy to prod, you’re taking a risk. Every time you decide not to merge or deploy, you’re taking a risk. And if you think too hard about all the risks you’re taking, it can actually be paralyzing.

It can feel less risky to not deploy than to deploy, but that’s just not the case. It’s simply a different kind of risk. You risk not shipping things your users need or want; you risk a sluggish deploy culture; you risk losing to your competition. It’s better to practice risky things often and in small chunks, with a limited blast radius, than to avoid risky things altogether.

> It’s better to practice risky things often and in small chunks, with a limited blast radius, than to avoid risky things altogether.

Organizations will differ in their appetite for risk. And even within an organization, there may be a wide range of tolerances for risk. Tolerance tends to be lowest and paranoia highest the closer you get to laying bits down on disk, especially user data or billing data. Tolerance tends to be higher toward the developer tools side or with offline or stateless services, where mistakes are less user-visible or permanent. Many engineers, if you ask them, will declare their absolute rejection of all risk. They passionately believe that any error is one too many. Yet these engineers somehow manage to leave the house each morning and sometimes even drive cars. (The horror!) Risk pervades everything that we do.

The risks of not acting are less visible, but no less deadly. They’re simply harder to internalize when they are amortized over longer periods of time or felt by different teams. Good engineering discipline consists of forcing oneself to take little risks every day and keep in good practice.

## “One does not simply roll out software with no bugs.”

The fact is, distributed systems exist in a continual state of partial degradation. Failure is the only constant. Failure is happening on your systems right now in a hundred ways you aren’t aware of and may never learn about. Obsessing over individual errors will, at best, drive you to the bottom of the nearest whiskey bottle and keep you up all night. Peace of mind (and a good night’s sleep) can only be regained by embracing error budgets via service-level objectives (SLOs) and service-level indicators (SLIs), thinking critically about how much failure users can tolerate, and hooking up feedback loops to empower software engineers to own their systems from end to end.

A system’s resilience is not defined by its lack of errors; it’s defined by its ability to survive many, many, many errors. We build systems that are friendlier to humans and users alike not by decreasing our tolerance for errors, but by increasing it. Failure is not to be feared. Failure is to be embraced, practiced, and made your good friend.

This means we need to help each other get over our fear and paranoia around production systems. You should be up to your elbows in prod every single day. Prod is where your users live. Prod is where users interact with your code on your infrastructure.

And because we’ve systematically underinvested in prod-related tooling, we’ve chosen to bar people from prod outright rather than build guardrails that by default help them do the right thing and make it hard to do the wrong thing. We’ve assigned deploy tooling to interns, not to our most senior engineers. We’ve built a glass castle where we ought to have a playground.

## “Some people like to debug only in staging. I also like to live dangerously.”

How do we get ourselves out of this mess? There are three aspects to this answer: technical, cultural, and managerial.

### Technical

This is an instrumentation game. We’re behind where we ought to be as an industry when it comes to developing and propagating sane conventions around observability and instrumentation because we’ve been building to fit the strictures of stupid data formats for too long. Instead of seeing instrumentation as a last-ditch effort of strings and metrics, we must think about propagating the full context of a request and emitting it at regular pulses. No pull request should ever be accepted unless the engineer can answer the question, “How will I know if this breaks?”

### Cultural

Engineers should be on call for their own code. While deploying, we should reflexively be looking at the world through the lens of our instrumentation. Is it working the way we expected it to? Does anything seem weird? Though fuzzy and imprecise, it’s the only way you’re going to catch those perilous unknown unknowns, the problems you never knew to expect.

### Managerial

> Errors and failure are our friends and humble teachers.

This unhealthy zero-tolerance approach to errors comes most often from control-freak management pressures. Managers need to learn to speak the language of error budgets, SLOs, and SLIs, to be outcome-oriented rather than diving into low-level details in a catastrophic and unpredictable way. It’s management’s job to set the tone (and hold the line) that errors and failure are our friends and humble teachers, not something to fear and avoid. Be calm. Chill out. Praise the behaviors you want to see more of.

It’s also management’s job to allocate resources at a high level. Managers need to recognize that 80 percent of the bugs are caught with 20 percent of the effort, and after that you get sharply diminishing returns. Modern software systems need less investment in pre-prod hardening and more investment in post-prod resiliency.

## I test in prod.

![](https://images.ctfassets.net/3njn2qm7rrbs/3o5Kfo4ZumLNViG3gpOcuT/8e0993e020c692d6b235f0cd8dfd6b83/most-interesting-man-1000-33333c10.jpeg?w=500)

There’s a lot of daylight between just throwing your code over the wall and waiting to get paged and having alert eyes on your code as it’s shipped, watching your instrumentation, and actively flexing the new features. There’s plenty of room for variation according to security needs, product requirements, and even sociocultural differences between teams. The one constant, however, is this: A modern software engineer’s job is not done until they have watched users use their code in production.

We now know that the only way to build high-quality systems is to invest in software ownership, making engineers who write services responsible for them all the way up to production. We also know that we can only expect people to be on call for the long run if we vastly pay down the amount of interruptions and paging incidents that most teams encounter. Resiliency goes hand in hand with ownership, which goes hand in hand with quality of life. All three reinforce each other in a virtuous cycle. You cannot work on one in isolation: A healthy culture of experimentation and testing in production pulls together all three.

Removing some cycles from the known unknowns and allocating them to the unknown unknowns—the really, truly hard problems—is the only way to close the loop and build truly mature systems that offer a high quality of service to users and a high quality of life to their human tenders.

Yes, you should test before and in prod. But if I had to choose—and thankfully I do not—I would choose the ability to watch my code in production over all the pre-prod testing in the world. Only one represents reality. Only one gives you the power and flexibility to answer any question. That’s why I test in prod.

#### About the author

**Charity Majors** is the cofounder and CTO of honeycomb.io and has been on call for half her life. She’s the coauthor of O’Reilly’s *Database Reliability Engineering*, and she loves free speech, free software, and single malt Scotch.

[@mipsytipsy](https://twitter.com/mipsytipsy)

#### Artwork by

**Sean Suchara**

[seansuchara.info](https://seansuchara.info/)

#### Topics

[Essays & Opinion](/topics/opinion/)

## Buy the print edition

Visit the Increment Store to purchase print issues.

[Store](https://store.increment.com/)

## Continue Reading

* [10

  ### Testing

  #### Kent Beck

  ### Testing the boundaries of col­labo­ra­tion

  Two experiments—small changes, instantly deployed; and automatically committing code that passes its tests, while deleting what fails—should have gone horribly wrong. They didn’t.](/testing/testing-the-boundaries-of-collaboration/)
* [3

  ### Development

  #### Dan Abramov

  ### The melting pot of JavaScript

  The JavaScript ecosystem is inventive, incremental, messy, and ubiquitous. Here’s how we can make it more approachable.](/development/the-melting-pot-of-javascript/)
* [10

  ### Testing

  #### Ipsita Agarwal

  ### A test of meaning

  For AARP, AutoCAD, Google, and Pinterest, qualitative research can include everything from focus groups to hand-drawn maps.](/testing/a-test-of-meaning/)
* [10

  ### Testing

  #### Tammy Butow

  ### Tests from the crypt

  Think of chaos engineering as unit testing your monitoring and alerting—or as exorcising your haunted house.](/testing/tests-from-the-crypt/)
* [10

  ### Testing

  #### David MacIver

  ### In praise of property-based testing

  Example-based tests hinge on a single scenario. Property-based tests get to the root of software behavior across multiple parameters.](/testing/in-praise-of-property-based-testing/)
* [10

  ### Testing

  #### Keyur Govande

  ### Ask an expert: What’s the value of transparency in testing and deployment?

  Etsy’s chief architect explains why visibility increases collaboration and builds confidence.](/testing/ask-an-expert-transparency-testing/)
* [10

  ### Testing

  #### Increment Staff

  ### Testing at scale

  Rob Zuber (CircleCI), Greg Bell and Claudiu Coman (Hootsuite), and Scott Triglia (Yelp) talk test suite times, manual versus automated testing, and how to build testing infrastructure.](/testing/testing-at-scale/)
* [10

  ### Testing

  #### Increment Staff

  ### The QA Q&A

  NPR test engineer Ijeoma Ezeonyebuchi discusses the limits of automation and the unique challenges of mobile testing.](/testing/qa-q-and-a/)
* [10

  ### Testing

  #### Myra Awodey and Karin Tsai

  ### The process: Launching Duolingo’s Arabic language course

  How the language-learning app used staggered releases, dogfooding, and a culture of A/B testing everything to ship its first Arabic course for English speakers.](/testing/launching-duolingos-arabic-language-course/)

### Explore Topics

* [Learn Something New](/topics/learn/)
* [Scaling & Growth](/topics/scaling/)
* [Ask an Expert](/topics/ask-an-expert/)
* [Interviews & Surveys](/topics/interviews/)
* [Guides & Best Practices](/topics/guides/)
* [Essays & Opinion](/topics/opinion/)
* [Workplace & Culture](/topics/culture/)

### All Issues

* [Issue 19 November 2021

  # Planning](/planning/)
* [Issue 18 August 2021

  # Mobile](/mobile/)
* [Issue 17 May 2021

  # Containers](/containers/)
* [Issue 16 February 2021

  # Reliability](/reliability/)
* [Issue 15 November 2020

  # Remote](/remote/)
* [Issue 14 August 2020

  # APIs](/apis/)
* [Issue 13 May 2020

  # Frontend](/frontend/)
* [Issue 12 February 2020

  # Software Architecture](/software-architecture/)
* [Issue 11 November 2019

  # Teams](/teams/)
* [Issue 10 August 2019

  # Testing](/testing/)
* [Issue 9 May 2019

  # Open Source](/open-source/)
* [Issue 8 February 2019

  # Internationalization](/internationalization/)
* [Issue 7 October 2018

  # Security](/security/)
* [Issue 6 August 2018

  # Documentation](/documentation/)
* [Issue 5 April 2018

  # Programming Languages](/programming-languages/)
* [Issue 4 February 2018

  # Energy & Environment](/energy-environment/)
* [Issue 3 October 2017

  # Development](/development/)
* [Issue 2 July 2017

  # Cloud](/cloud/)
* [Issue 1 April 2017

  # On-Call](/on-call/)

[@incrementmag](https://twitter.com/incrementmag)  [incrementmag](https://facebook.com/incrementmag)  [RSS Feed](/feed.xml)

#### About

*Increment* is a print and digital magazine about how teams build and operate software systems at scale. [Learn more](/about/)

#### Work with us

Interested in joining the team at Stripe? [View job openings](https://stripe.com/jobs)

© 2022 *Increment* [Published by Stripe](https://stripe.com) [Privacy policy](https://stripe.com/privacy/media-policy)