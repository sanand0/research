# LETTER DOMINANCE: A Computational Investigation

*What percentage of a word can be just one letter before it stops being a word and starts being keyboard spam?*

---

I wrote a Python script to analyze 370,105 English words. Then I questioned my life choices. Then I ran it anyway.

## The Script

```python
from collections import Counter

def dominant_letter_pct(word):
    counts = Counter(word.lower())
    max_count = counts.most_common(1)[0][1]
    return max_count / len(word)

# That's it. That's the whole analysis.
# The rest is just making charts.
```

## The Results

Out of 370,105 words, exactly **333** have four or more letters where a single letter comprises more than half the word.

That's 0.09% of words. For context, you have better odds of:
- A coin landing on its edge (estimated 1 in 6,000)
- Being struck by lightning this year (1 in 500,000... okay, maybe not that one)

### The Champions

```
Word        Letter  Count/Total  Percentage
--------------------------------------------
mmmm        M       4/4          100% ← Debatable if this is a "word"
oooo        O       4/4          100% ← Same energy
lull        L       3/4          75%  ← Legitimately a word!
sass        S       3/4          75%
assess      S       4/6          67%
possesses   S       5/9          56%  ← Longest "real" word
```

### Does "mmmm" Count?

Look, I didn't make the dictionary. I just downloaded it from the internet.[^1]

[^1]: This is either a sound of contemplation, a sound of deliciousness, or the noise your computer fan makes when you run too many browser tabs. It appears in at least one major dictionary as an interjection. I'm counting it because excluding it requires making decisions about what constitutes a "real" word, and I'm a programmer, not a linguist.

If we require words that you could use in a Scrabble game without your opponent flipping the board, the champions become:

| Length | Best Word | Percentage |
|--------|-----------|------------|
| 4 | LULL | 75% |
| 5 | MUMMY | 60% |
| 6 | ASSESS | 67% |
| 7 | POSSESS | 57% |
| 8 | ASSESSES | 62.5% |
| 9 | POSSESSES | 56% |

Notice something? After length 6, it's just S-words and E-words all the way down.[^2]

[^2]: The letter S is doing a *lot* of heavy lifting here. It appears in plurals, third-person verbs, possessives, and the "-ness" suffix. It's the grammatical duct tape of English.

## The Letter Dominance Distribution

```
[FIGURE 1: A stick figure standing next to a bar chart]
[Alt-text: The stick figure is pointing at the E bar, which is nearly
three times taller than the others. A speech bubble reads "This is
because we keep spelling 'referee' with four E's for some reason."]

           Letters appearing as "dominant" (>50% of word)

    E ████████████████████████████████████████████ 89
    A ██████████████████████████ 57
    O ████████████████████ 40
    S █████████████████ 36
    D ██████ 13
    L ██████ 13
    T █████ 10
    M ████ 9
    N ████ 9
    ...
    W █ 1
```

E dominates the dominant letters. It's dominant at being dominant. Very meta.

## The "Impressiveness" Problem

Here's the thing: getting 75% in a 4-letter word is easy. You just need 3 of the same letter. That's practically a typo.

But getting 56% in a 9-letter word? You need 5 repetitions of a single letter while still forming a valid English word. That's *hard*.

I needed a metric that accounts for this. So I used math.[^3]

[^3]: Specifically: `score = (k/n - 1/26) * sqrt(n)` where k is the count of the dominant letter and n is word length. This is basically "how much better than random chance is this, scaled by how long the word is." There are probably better metrics. I have a day job.

```
[FIGURE 2: Two stick figures arguing]
[Alt-text: One figure holds a sign saying "LULL IS 75%!" The other
holds a sign saying "POSSESSES IS MORE IMPRESSIVE!" A third figure
in the background is calculating binomial probabilities on a chalkboard.]
```

By this metric, the most "impressive" words are:

1. **ASSESSES** (62.5% S in 8 letters) — Score: 1.66
2. **POSSESSES** (56% S in 9 letters) — Score: 1.55
3. **BEEKEEPER** (56% E in 9 letters) — Score: 1.55

## The Great Letter Inequality

Some letters are dramatically over- or under-represented:

```
Letter  Expected*  Actual  Ratio
Z       0.07%      0.6%    8.6x  ← Punching way above its weight
A       8.2%       17.1%   2.1x
E       12.7%      26.7%   2.1x
R       6.0%       0.9%    0.2x  ← R rarely dominates
T       9.1%       3.0%    0.3x
W       2.4%       0.3%    0.1x  ← W almost never dominates

*Based on standard English letter frequency
```

Z is nearly **nine times** more likely to be a dominant letter than you'd expect from its frequency! This is because:
1. Z-words tend to be weird borrowed words (PIZZAZZ, ZIZZ)
2. When Z shows up, it often shows up multiple times
3. Z has nothing better to do

Meanwhile, R and T are distributed evenly through words like responsible civic-minded letters, never clustering selfishly.

## But What About...

### MISSISSIPPI?

Doesn't qualify. It's 36% I (4 out of 11). I was disappointed too.

### BANANA?

Exactly 50%. So close! Just missed the threshold.

### WWW?

The dictionary includes it as an abbreviation for "World Wide Web." It's 100% W. But it's only 3 letters, so it doesn't meet our minimum length.

Also, if we're being honest, nobody *says* "www" — we say "dubya dubya dubya" or "triple-dub" or just skip it entirely. This raises deep questions about what a "word" is that I refuse to engage with.[^4]

[^4]: Linguists have been arguing about this for literally centuries and I'm not getting involved.

### Welsh Words?

```
[FIGURE 3: A stick figure looking confused at a sign reading "LLANFAIRPWLLGWYNGYLLGOGERYCHWYRNDROBWLLLLANTYSILIOGOGOGOCH"]
[Alt-text: The figure is counting on their fingers. A thought bubble
shows "L: 11/58 = 19%... wait, that's not even close. How does Welsh
have SO MANY consonants and NONE of them dominate?"]
```

I didn't analyze Welsh, but I'm guessing their L's would be extremely competitive.

## Extrapolation: The Theoretical Maximum

If we allowed constructed words, how far could we push this?

English has some productive suffixes:
- "-ness" adds 4 letters (1 S)
- "-less" adds 4 letters (2 S's)
- "-esses" adds 5 letters (3 S's!)

So theoretically:

```
POSSESSESSESSESSESSESSESSES
(if this were a word, which it isn't)
S count: 17
Length: 27
Percentage: 63%
```

For real constructed words, we hit a wall around 60%. English morphology just doesn't allow more repetition without sounding like you're having a stroke.

## Conclusion

```
[FIGURE 4: A pie chart where one slice is labeled "words with >50%
single-letter dominance" and the rest is labeled "normal words"]
[Alt-text: The dominant-letter slice is so thin it's basically
invisible. An arrow points to it with the label "you are here,
if you're LULL"]
```

English strongly resists letter dominance. Out of 370,000 words, only 333 break the 50% barrier, and most of those are:
- Four-letter words where 3-of-4 is easy
- Words with lots of S (because S does everything)
- Words with repeated vowels (BOOBOO, PEEWEE, MUUMUU)
- Words I've never heard of (KAKKAK?[^5])

[^5]: It's a type of bird. Of course it is.

The true champions are the long words that maintain dominance: POSSESSES, ASSESSORS, BEEKEEPER. These are the real MVPs — words that resist the statistical inevitability of variety and insist on repeating themselves.

Just like this article, which has now used the word "dominance" 27 times.

28.

---

*All data and code available at [repository]. I make no warranties about dictionary completeness or my ability to count letters correctly.*

---

## Appendix: The Full Distribution

```
[FIGURE 5: Histogram of letter dominance percentages for all 370,105 words]
[Alt-text: A very normal-looking distribution centered around 20-30%.
There's a tiny blip above 50% that you'd miss if you blinked. A stick
figure is squinting at it through a magnifying glass.]

Percentage of word that is most-common letter:
0-10%   ▏0.3%
10-20%  ████████████████ 31%
20-30%  ████████████████████████████████ 42%
30-40%  █████████████ 19%
40-50%  ████ 6%
50-60%  ▏0.08%
60-70%  ▏0.01%
70-80%  ▏0.006%
80-90%  ▏0%
90-100% ▏0.0005%
```

The vast majority of words hover around 25% dominance, which is what you'd expect if letters were roughly evenly distributed (100% / 4-5 unique letters = 20-25%).

Breaking 50% is hard. Breaking 60% is rare. Breaking 70% requires a 4-letter word. And 100% requires abandoning all pretense that you're writing actual words.

---

*Posted from my MMMM key. I mean my keyboard.*
