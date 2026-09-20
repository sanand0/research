# Did Claude Fable 5.1 really solve the Cyphral Distich?

<!-- https://chatgpt.com/c/6aafeccc-2754-83ec-b374-6ae964aba992 -->

On 31 August 2026, [Vals AI said Claude Fable 5.1 had solved the Cyphral Distich](https://www.vals.ai/blogs/fable-solves-cyphral-distich), a cipher attributed to the 17th-century Scottish writer Sir Thomas Urquhart.

The solution is wonderfully simple. It also has a fairly important catch.

**I can reproduce Fable's plaintext perfectly from the 1834 edition: all 64 letters match. But I cannot reproduce it from the surviving 1653 edition that Vals says the cipher came from.**

That makes this less a cryptography mystery now and more a bibliography mystery: where did the 1834 text come from?

## What is the Cyphral Distich?

Urquhart published *Logopandecteision* in 1653. Near the end are 32 numbered "Proquiritations", basically 32 requests or petitions.

A much later collection, [*The Works of Sir Thomas Urquhart of Cromarty, Knight* (1834)](https://archive.org/details/worksofsirthomas00mait), prints those 32 Proquiritations and then, on page 417, this:

[![Page 417 of the 1834 Works, showing the Cyphral Distich](cyphral-distich-p417.avif)](https://archive.org/details/worksofsirthomas00mait/page/417/mode/1up)

*The [local compressed scan](cyphral-distich-p417.avif) is from page 417 of the [1834 Internet Archive copy](https://archive.org/details/worksofsirthomas00mait).*

There are two lines of 32 numbers. This is not a recent puzzle: on 18 February 1899, [a reader in *Notes and Queries* printed the Cyphral Distich and asked if anyone could solve it](https://en.wikisource.org/wiki/Page:Notes_and_Queries_-_Series_9_-_Volume_3.djvu/134).

Fable's idea was different from the obvious number-to-letter approaches: **the numbers are word positions inside the 32 Proquiritations printed just before the cipher.**

The rule is:

> For the first cipher number, go to Proquiritation 1. Count to that numbered word. Take its first letter.
> For the second number, do the same with Proquiritation 2. Continue through Proquiritation 32.

Then restart at Proquiritation 1 for the second line.

That sounds almost suspiciously easy. So I tried it.

## The first four letters are literally "O GOD"

The first four cipher numbers are `5, 3, 27, 38`.

Applying Fable's rule to the 1834 text gives:

| Cipher position | Proquiritation | Word number | Word | Letter |
| ---: | ---: | ---: | --- | --- |
| 1 | 1 | 5 | **of** | O |
| 2 | 2 | 3 | **grant** | G |
| 3 | 3 | 27 | **of** | O |
| 4 | 4 | 38 | **desire** | D |

And it keeps going.

I wrote a small [reproduction script](verify.py) that parses the 32 Proquiritations, applies the rule to both lines, and records all 64 lookups in [coordinates.csv](coordinates.csv).

It gets:

```text
O GOD UPHOLD KING CHARLS THE SECOND AND
MAKE HIM THE SUPREME RULER OF THIS LAND
```

**Against the 1834 text, the result is 64/64.**

You can inspect every lookup in [coordinates.csv](coordinates.csv), rather than taking the final English sentence on faith.

There are two fiddly counting conventions. The Latin expression `hinc inde` has to count as one unit, which [Vals itself notes](https://www.vals.ai/blogs/fable-solves-cyphral-distich). Also, the printed `parol-breaking` has to count as two words. With those conventions, every coordinate works.

## There is a small error in the Vals article

While checking the numbers against the actual page, I noticed that [Vals' displayed ciphertext](https://www.vals.ai/blogs/fable-solves-cyphral-distich) has this segment in the second line:

```text
... 8.35.5.33.5.5.18 ...
```

But the [1834 scan](cyphral-distich-p417.avif) clearly prints:

```text
... 8.35.5.38.5.5.18 ...
```

The [1899 *Notes and Queries* printing](https://en.wikisource.org/wiki/Page:Notes_and_Queries_-_Series_9_-_Volume_3.djvu/134) also has `38`, so this is not just a judgment call on a fuzzy scan.

That `33` versus `38` matters.

Using `38`, the word is **for**, giving the `F` in:

```text
... RULER OF THIS LAND
```

Using the `33` printed in the Vals blog, the word is **thing**, giving:

```text
... RULER OT THIS LAND
```

So the rule works 64/64 against the source page, but **not against the ciphertext as transcribed in the Vals article**. This looks like a simple transcription error in the blog post, not a problem with the 1834 decode.

The [script](verify.py) checks both versions.

## Then I checked the 1653 book

This is where things got strange.

Vals describes the cipher as being "at the end of Urquhart's *Logopandecteision*" and immediately after its 32 Proquiritations.

So I checked the [digitized British Library copy of the actual 1653 *Logopandecteision*](https://archive.org/details/bim_early-english-books-1641-1700_logopandecteision-or-an_urquhart-sir-thomas_1653).

**The Cyphral Distich is not there.**

That copy ends its Proquiritations, prints the `Parva peto...` verse and its English translation, says `FINIS`, and moves on to errata. There is no page of 64 dotted numbers.

More importantly, **the 32 Proquiritations themselves are not the same key text**.

The 1834 Proquiritation 1 begins with Urquhart tracing his ancestry "from the creation of the world". In the 1653 copy, that petition appears later. Its Proquiritation 1 is a different petition, about his good name being "eternized".

That is fatal to this particular indexing rule. If cipher number 1 means "take word 5 of Proquiritation 1", then changing which paragraph is Proquiritation 1 changes the key.

So there are really two different claims here:

| Claim | What I found |
| --- | --- |
| The numbers printed in the **1834** Cyphral Distich decode with Fable's rule | **Yes. 64/64.** |
| This same cipher/key arrangement is established in the surviving **1653** book | **No. Not from the copy I checked.** |

The first result is very strong. The second is still an open provenance question.

## This also explains why independent checks seemed to disagree

On 1 September, [Reticuli Labs tried the rule against the 1653 text](https://github.com/reticuli-labs/panel-artifacts/blob/main/distich-refutation-2026-09-01/FINDINGS.md) and concluded that the claimed solution did not survive contact with the original book. They found that the cipher was absent and that several required letters could not even occur under the proposed rule.

On 16 September, [Daniel Bourdeau independently investigated Urquhart's ciphers](https://dbourdeau.github.io/cyphersolver/urquhart.html). He found strong evidence for Fable's related solution of Urquhart's much longer Cyphral Octastich, but reported that **the Distich rule does not reproduce against the 1653 Proquiritations**.

At first glance this sounds incompatible with Vals' 64-letter plaintext.

It isn't.

**The 1834 version really does decode to Fable's plaintext. The surviving 1653 version really does not.**

That is the useful distinction.

## So did Fable solve it?

I think the narrow claim is clear:

**Fable found a convincing and completely reproducible book-cipher reading of the Cyphral Distich as printed in 1834.**

What I would not yet say is that we have demonstrated how Urquhart's 1653 readers were meant to solve it.

The title page of the [1834 collection says it was "Reprinted from the original editions"](https://archive.org/details/worksofsirthomas00mait). Perhaps its editors had access to a different state or copy of the 1653 book. Perhaps the cipher and reordered Proquiritations survive through another source. Or perhaps something happened in transmission before 1834.

I haven't found evidence here that settles that.

A 1653 copy containing both the Distich and the same reordered Proquiritations would settle most of the question immediately.

## How I checked it

I did four checks, trying not to let the nice-looking plaintext do the persuading by itself.

First, I compared the numbers with the [actual 1834 page](cyphral-distich-p417.avif), rather than only using the Vals transcription. That is how the `33 -> 38` error showed up.

Second, I independently implemented the proposed rule in [verify.py](verify.py). It produces the claimed 64 letters and writes the full audit trail to [coordinates.csv](coordinates.csv).

Third, I checked the [1653 scan](https://archive.org/details/bim_early-english-books-1641-1700_logopandecteision-or-an_urquhart-sir-thomas_1653), including its final pages, rather than assuming the 1834 reprint was textually identical.

Finally, I compared the result with the two independent follow-ups: [Reticuli Labs](https://github.com/reticuli-labs/panel-artifacts/blob/main/distich-refutation-2026-09-01/FINDINGS.md) and [Bourdeau](https://dbourdeau.github.io/cyphersolver/urquhart.html).

The interesting bit, for me, is that the cryptographic part is now almost boring. A tiny script settles it.

**The hard part is provenance: why does the 1834 book contain exactly the text needed for this cipher when the surviving 1653 copy does not?**

## Reproduce it

The repository deliberately keeps the reproduction small. The script uses the Internet Archive OCR directly if a local copy is not present.

```bash
python3 verify.py
```

It should print:

```text
OGODUPHOLDKINGCHARLSTHESECONDAND
MAKEHIMTHESUPREMERULEROFTHISLAND
matches: 64 /64
Vals transcription:
MAKEHIMTHESUPREMERULEROTTHISLAND
matches: 31 /32
```

The detailed evidence is in [coordinates.csv](coordinates.csv).

Public sources: [Vals AI's original claim](https://www.vals.ai/blogs/fable-solves-cyphral-distich), the [1834 Works](https://archive.org/details/worksofsirthomas00mait), the [1653 *Logopandecteision*](https://archive.org/details/bim_early-english-books-1641-1700_logopandecteision-or-an_urquhart-sir-thomas_1653), [Reticuli Labs' replication](https://github.com/reticuli-labs/panel-artifacts/blob/main/distich-refutation-2026-09-01/FINDINGS.md), and [Bourdeau's independent Urquhart analysis](https://dbourdeau.github.io/cyphersolver/urquhart.html).
