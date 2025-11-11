Skip to main content
            * 
            Resources
                    * Web Platform
                    * Dive into the web platform, at your pace.
                      * HTML
                      * CSS
                      * JavaScript
                    * User experience
                    * Learn how to build better user experiences.
                      * Performance
                      * Accessibility
                      * Identity
                    * Learn
                    * Get up to speed on web development.
                      * Learn HTML
                      * Learn CSS
                      * Learn JavaScript
                      * Learn Performance
                      * Learn Accessibility
                      * More courses
                    * Additional resources
                    * Explore content collections, patterns, and more.
                      * AI and the web
                      * Explore
                      * PageSpeed Insights
                      * Patterns
                      * Podcasts & shows
                      * Developer Newsletter
                      * About web.dev
            Baseline How to use Baseline Blog Case Studies
                /
          * English
          * Deutsch
          * Español – América Latina
          * Français
          * Indonesia
          * Italiano
          * Polski
          * Português – Brasil
          * Tiếng Việt
          * Türkçe
          * Русский
          * עברית
          * العربيّة
          * فارسی
          * हिंदी
          * বাংলা
          * ภาษาไทย
          * 中文 – 简体
          * 中文 – 繁體
          * 日本語
          * 한국어
        Sign in
      * 
      * Resources
          + More
      * Baseline
      * How to use Baseline
      * Blog
      * Case Studies
      * Web Platform
      * HTML
      * CSS
      * JavaScript
      * User experience
      * Performance
      * Accessibility
      * Identity
      * Learn
      * Learn HTML
      * Learn CSS
      * Learn JavaScript
      * Learn Performance
      * Learn Accessibility
      * More courses
      * Additional resources
      * AI and the web
      * Explore
      * PageSpeed Insights
      * Patterns
      * Podcasts & shows
      * Developer Newsletter
      * About web.dev
    * Home
    * Articles

Web Vitals Stay organized with collections Save and categorize content based on your preferences.

        Philip Walton

  Published: May 4, 2020

  Optimizing for quality of user experience is key to the long-term success of any site on the web. Whether you're a business owner, marketer, or developer, Web Vitals can help you quantify the experience of your site and identify opportunities to improve.

  Overview

  Web Vitals is an initiative by Google to provide unified guidance for quality signals that are essential to delivering a great user experience on the web.

  Google has provided a number of tools over the years to measure and report on performance. Some developers are experts at using these tools, while others have found the abundance of both tools and metrics challenging to keep up with.

  Site owners shouldn't have to be performance experts to understand the quality of experience they are delivering to their users. The Web Vitals initiative aims to simplify the landscape, and help sites focus on the metrics that matter most, the Core Web Vitals.

  Core Web Vitals

  Core Web Vitals are the subset of Web Vitals that apply to all web pages, should be measured by all site owners, and will be surfaced across all Google tools. Each of the Core Web Vitals represents a distinct facet of the user experience, is measurable in the field, and reflects the real-world experience of a critical user-centric outcome.

  The metrics that make up Core Web Vitals will evolve over time. The current set focuses on three aspects of the user experience—loading, interactivity, and visual stability—and includes the following metrics (and their respective thresholds):

    * Largest Contentful Paint (LCP): measures loading performance. To provide a good user experience, LCP should occur within 2.5 seconds of when the page first starts loading.
    * Interaction to Next Paint (INP): measures interactivity. To provide a good user experience, pages should have a INP of 200 milliseconds or less.
    * Cumulative Layout Shift (CLS): measures visual stability. To provide a good user experience, pages should maintain a CLS of 0.1. or less.

  To ensure you're hitting the recommended target for these metrics for most of your users, a good threshold to measure is the 75th percentile of page loads, segmented across mobile and desktop devices.

  Tools that assess Core Web Vitals compliance should consider a page passing if it meets the recommended targets at the 75th percentile for all three of the Core Web Vitals metrics.

  Note: To learn more about the research and methodology behind these recommendations, see: Defining the Core Web Vitals metrics thresholds.

  Lifecycle

  Metrics on the Core Web Vitals track go through a lifecycle consisting of three phases: experimental, pending, and stable.

  The stages of the Core Web Vitals lifecycle.

  Each phase is designed to signal to developers how they should think about each metric:

    * Experimental metrics are prospective Core Web Vitals that may still be undergoing significant changes depending on testing and community feedback.
    * Pending metrics are future Core Web Vitals that have passed the testing and feedback stage and have a well-defined timeline to becoming stable.
    * Stable metrics are the current set of Core Web Vitals that Chrome considers essential for great user experiences.

  The Core Web Vitals are at the following lifecycle stages:

    * LCP: Stable
    * CLS: Stable
    * INP: Stable

  Experimental

  When a metric is initially developed and enters the ecosystem, it is considered an experimental metric.

  The purpose of the experimental phase is to assess a metric's fitness, first by exploring the problem to be solved, and possibly iterate on what previous metrics may have failed to address. For example, Interaction to Next Paint (INP) was initially developed as an experimental metric to address the runtime performance issues present on the web more comprehensively than First Input Delay (FID).

  The experimental phase of Core Web Vitals lifecycle is also intended to give flexibility in a metric's development by identifying bugs and even exploring changes to its initial definition. It's also the phase in which community feedback is most important.

  Pending

  When the Chrome team determines that an experimental metric has received sufficient feedback and proven its efficacy, it becomes a pending metric. For example, INP was promoted in 2023 from experimental to pending status with the intent to eventually retire FID.

  Pending metrics are held in this phase for a minimum of six months to give the ecosystem time to adapt. Community feedback remains an important aspect of this phase, as more developers begin to use the metric.

  Stable

  When a Core Web Vital candidate metric is finalized, it becomes a stable metric. This is when the metric can become a Core Web Vital.

  Stable metrics are actively supported, and can be subject to bug fixes and definition changes. Stable Core Web Vitals metrics won't change more than once per year. Any change to a Core Web Vital will be clearly communicated in the metric's official documentation, as well as in the metric's changelog. Core Web Vitals are also included in any assessments.

  Key point: Stable metrics aren't necessarily permanent. A stable metric can be retired and replaced by another metric that addresses the problem area more effectively. This is exactly what happened to FID as INP became a stable Core Web Vital metric in 2024.

  Tools to measure and report Core Web Vitals

  Google believes that the Core Web Vitals are critical to all web experiences. As a result, it is committed to surfacing these metrics in all of its popular tools. The following sections details which tools support the Core Web Vitals.

  Field tools to measure Core Web Vitals

  The Chrome User Experience Report collects anonymized, real user measurement data for each Core Web Vital. This data enables site owners to quickly assess their performance without requiring them to manually instrument analytics on their pages, and powers tools like Chrome DevTools, PageSpeed Insights, and Search Console's Core Web Vitals report.

                                               LCP    INP    CLS  
      Chrome User Experience Report            check  check  check
      Chrome DevTools                          check  check  check
      PageSpeed Insights                       check  check  check
      Search Console (Core Web Vitals report)  check  check  check
      
    Note: For guidance on how to use these tools, and which tool is right for your use case, see: Getting started with measuring Web Vitals.

    The data provided by Chrome User Experience Report offers a quick way to assess the performance of sites, but it does not provide the detailed, per-pageview telemetry that is often necessary to accurately diagnose, monitor, and quickly react to regressions. As a result, we strongly recommend that sites set up their own real-user monitoring.

    Measure Core Web Vitals in JavaScript

    Each of the Core Web Vitals can be measured in JavaScript using standard web APIs.

    Note: Note that the Core Web Vitals measured in JavaScript using public APIs may differ from the Core Web Vitals reported by CrUX. Read about the differences between these data sources for more info.

    The easiest way to measure all the Core Web Vitals is to use the web-vitals JavaScript library, a small, production-ready wrapper around the underlying web APIs that measures each metric in a way that accurately matches how they're reported by all the Google tools listed earlier.

    With the web-vitals library, measuring each metric can be done by calling a single function. See the documentation for complete usage and API details.

    import {onCLS, onINP, onLCP} from 'web-vitals';
    
    function sendToAnalytics(metric) {
      const body = JSON.stringify(metric);
      // Use `navigator.sendBeacon()` if available, falling back to `fetch()`.
      (navigator.sendBeacon && navigator.sendBeacon('/analytics', body)) ||
        fetch('/analytics', {body, method: 'POST', keepalive: true});
    }
    
    onCLS(sendToAnalytics);
    onINP(sendToAnalytics);
    onLCP(sendToAnalytics);
    

    Once you've configured your site to use the web-vitals library to measure and send your Core Web Vitals data to an analytics endpoint, the next step is to aggregate and report on that data to see if your pages are meeting the recommended thresholds for at least 75% of page visits.

    While some analytics providers have built-in support for Core Web Vitals metrics, even those that don't should include basic custom metric features that allow you to measure Core Web Vitals in their tool.

    Developers who prefer to measure these metrics directly using the underlying web APIs can instead use these metric guides for implementation details:

      * Measure LCP in JavaScript
      * Measure INP in JavaScript
      * Measure CLS in JavaScript

    For additional guidance on measuring these metrics using popular analytics services or your own in-house analytics tools, see Best practices for measuring Web Vitals in the field.

    Lab tools to measure Core Web Vitals

    While all of the Core Web Vitals are, first and foremost, field metrics, many of them are also measurable in the lab.

    Lab measurement is the best way to test the performance of features during development—before they've been released to users. It's also the best way to catch performance regressions before they happen.

    The following tools can be used to measure the Core Web Vitals in a lab environment:

                         LCP    INP                      CLS  
        Chrome DevTools  check  check                    check
        Lighthouse       check  block (use TBT instead)  check
        
      Note: Tools like Lighthouse that load pages in a simulated environment without a user cannot measure INP, as there is no user input. However, the Total Blocking Time (TBT) metric is lab-measurable and is a proxy for INP. Performance optimizations that improve TBT in the lab may improve INP in the field (see performance recommendations below).

      While lab measurement is an essential part of delivering great experiences, it is not a substitute for field measurement.

      The performance of a site can substantially vary based on a user's device capabilities, their network conditions, what other processes may be running on the device, and how they're interacting with the page. In fact, each of the Core Web Vitals metrics can have its score affected by user interaction. Only field measurement can accurately capture the complete picture.

      Recommendations for improving your scores

      The following guides offer specific recommendations for how to optimize your pages for each of the Core Web Vitals:

        * Optimize LCP
        * Optimize INP
        * Optimize CLS

      There are many ways to improve Core Web Vitals, and each approach comes with varying levels of impact, relevance, and ease of use for every situation. Refer to The most effective ways to improve Core Web Vitals for a short list of the Chrome team's top recommendations.

      Other Web Vitals

      While the Core Web Vitals are the critical metrics for understanding and delivering a great user experience, there are other supporting metrics.

      These other metrics can serve as proxy—or as supplemental metrics for the three Core Web Vitals—to help capture a larger part of the experience or to aid in diagnosing a specific issue.

      For example, the metrics Time to First Byte (TTFB) and First Contentful Paint (FCP) are both vital aspects of the loading experience, and are both useful in diagnosing issues with LCP (slow server response times or render-blocking resources, respectively).

      Similarly, a metric like Total Blocking Time (TBT) is a lab metrics is vital in catching and diagnosing potential interactivity issues that can impact INP. However, it is not part of the Core Web Vitals set because they are not field-measurable, nor do they reflect a user-centric outcome.

      Changes to Web Vitals

      Web Vitals and Core Web Vitals represent the best available signals developers have today to measure quality of experience across the web, but these signals are not perfect and future improvements or additions should be expected.

      The Core Web Vitals are relevant to all web pages and featured across relevant Google tools. Changes to these metrics will have wide-reaching impact; as such, developers should expect the definitions and thresholds of the Core Web Vitals to be stable, and updates to have prior notice and a predictable, annual cadence.

      The other Web Vitals are often context or tool specific, and may be more experimental than the Core Web Vitals. As such, their definitions and thresholds may change with greater frequency.

      For all Web Vitals, changes will be clearly documented in this public CHANGELOG.

  Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.

  Last updated 2024-10-31 UTC.

    [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Missing the information I need","missingTheInformationINeed","thumb-down"],["Too complicated / too many steps","tooComplicatedTooManySteps","thumb-down"],["Out of date","outOfDate","thumb-down"],["Samples / code issue","samplesCodeIssue","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2024-10-31 UTC."],[],[]]

  * web.dev

      + web.dev

          We want to help you build beautiful, accessible, fast, and secure websites that work cross-browser, and for all of your users. This site is our home for content to help you on that journey, written by members of the Chrome team, and external experts.

  * Contribute

      + File a bug
      + See open issues

  * Related Content

      + Chrome for Developers
      + Chromium updates
      + Case studies
      + Podcasts & shows

  * Follow

      + @ChromiumDev on X
      + YouTube
      + Chrome for Developers on LinkedIn
      + RSS
    * Terms
    * Privacy
    * Manage cookies
    * English
    * Deutsch
    * Español – América Latina
    * Français
    * Indonesia
    * Italiano
    * Polski
    * Português – Brasil
    * Tiếng Việt
    * Türkçe
    * Русский
    * עברית
    * العربيّة
    * فارسی
    * हिंदी
    * বাংলা
    * ภาษาไทย
    * 中文 – 简体
    * 中文 – 繁體
    * 日本語
    * 한국어