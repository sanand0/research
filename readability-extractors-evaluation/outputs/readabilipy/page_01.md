2024-10-02

9 min read

![](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/4oWX173TYNYhwBecZAf7lU/a9bc6be9b7687ba354e9db1f46f0e685/BLOG-2586_1.png)

Since early September, [Cloudflare's DDoS protection systems](https://developers.cloudflare.com/ddos-protection/about/components/#autonomous-edge) have been combating a month-long campaign of hyper-volumetric L3/4 DDoS attacks. Cloudflare’s defenses mitigated over one hundred hyper-volumetric L3/4 DDoS attacks throughout the month, with many exceeding 2 billion packets per second (Bpps) and 3 terabits per second (Tbps). The largest attack peaked 3.8 Tbps — the largest ever disclosed publicly by any organization. Detection and mitigation was fully autonomous. The graphs below represent two separate attack events that targeted the same Cloudflare customer and were mitigated autonomously.

![BLOG-2586 2](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/7hXUgmEd37kzZrMs0KPXLl/21a4779022bdff91f760dc66759eb955/BLOG-2586_2.png)

*A mitigated 3.8 Terabits per second DDoS attack that lasted 65 seconds*

![BLOG-2586 3](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/1uxvtlkdFoH6KU6waXxK3o/d17fe7cf0e33c20e64a47b3ca0e6ca63/BLOG-2586_3.png)

*A mitigated 2.14 billion packet per second DDoS attack that lasted 60 seconds*

## Cloudflare customers are protected

Cloudflare customers using Cloudflare’s HTTP reverse proxy services (e.g. [Cloudflare WAF](https://developers.cloudflare.com/waf/) and [Cloudflare CDN](https://developers.cloudflare.com/cache/)) are automatically protected.

Cloudflare customers using [Spectrum](https://developers.cloudflare.com/spectrum/) and [Magic Transit](https://developers.cloudflare.com/magic-transit/) are also automatically protected. Magic Transit customers can further optimize their protection by deploying [Magic Firewall](https://developers.cloudflare.com/magic-firewall/) rules to enforce a strict positive and negative security model at the packet layer.

## Other Internet properties may not be safe

The scale and frequency of these attacks are unprecedented. Due to their sheer size and bits/packets per second rates, these attacks have the ability to take down unprotected Internet properties, as well as Internet properties that are protected by on-premise equipment or by cloud providers that just don’t have sufficient network capacity or global coverage to be able to handle these volumes alongside legitimate traffic without impacting performance.

Cloudflare, however, does have the network capacity, global coverage, and intelligent systems needed to absorb and automatically mitigate these monstrous attacks.

In this blog post, we will review the attack campaign and why its attacks are so severe. We will describe the anatomy of a Layer 3/4 DDoS attack, its objectives, and how attacks are generated. We will then proceed to detail how Cloudflare’s systems were able to autonomously detect and mitigate these monstrous attacks without impacting performance for our customers. We will describe the key aspects of our defenses, starting with how our systems generate real-time (dynamic) signatures to match the attack traffic all the way to how we leverage kernel features to drop packets at wire-speed.

## Campaign analysis

We have observed this attack campaign targeting multiple customers in the financial services, Internet, and telecommunication industries, among others. This attack campaign targets bandwidth saturation as well as resource exhaustion of in-line applications and devices.

The attacks predominantly leverage [UDP](https://www.cloudflare.com/learning/ddos/glossary/user-datagram-protocol-udp/) on a fixed port, and originated from across the globe with larger shares coming from Vietnam, Russia, Brazil, Spain, and the US.

The high packet rate attacks appear to originate from multiple types of compromised devices, including MikroTik devices, DVRs, and Web servers, orchestrated to work in tandem and flood the target with exceptionally large volumes of traffic. The high bitrate attacks appear to originate from a large number of compromised ASUS home routers, likely exploited using [a CVE 9.8 (Critical) vulnerability that was recently discovered by Censys](https://censys.com/june-20-improper-authentication-vulnerability-in-asus-routers/).

|  |  |
| --- | --- |
| Russia | 12.1% |
| Vietnam | 11.6% |
| United States | 9.3% |
| Spain | 6.5% |
| Brazil | 4.7% |
| France | 4.7% |
| Romania | 4.4% |
| Taiwan | 3.4% |
| United Kingdom | 3.3% |
| Italy | 2.8% |

*Share of packets observed by source location*

## Anatomy of DDoS attacks

Before we discuss how Cloudflare automatically detected and mitigated the largest DDoS attacks ever seen, it‘s important to understand the basics of DDoS attacks.

![BLOG-2586 5](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/7HLtAHnyjS33iiJAR1B9h9/2e1fc2cab871440fc95fa803989ae156/BLOG-2586_5.png)

*Simplified diagram of a DDoS attack*

The goal of a [Distributed Denial of Service (DDoS) attack](https://www.cloudflare.com/learning/ddos/what-is-a-ddos-attack/) is to deny legitimate users access to a service. This is usually done by exhausting resources needed to provide the service. In the context of these recent Layer 3/4 DDoS attacks, that resource is CPU cycles and network bandwidth.

### Exhausting CPU cycles

Processing a packet consumes CPU cycles. In the case of regular (non-attack) traffic, a *legitimate* packet received by a service will cause that service to perform some action, and different actions require different amounts of CPU processing. However, before a packet is even delivered to a service there is per-packet work that needs to be done. Layer 3 packet headers need to be parsed and processed to deliver the packet to the correct machine and interface. Layer 4 packet headers need to be processed and routed to the correct socket (if any). There may be multiple additional processing steps that inspect every packet. Therefore, if an attacker sends at a high enough packet rate, then they can potentially saturate the available CPU resources, denying service to legitimate users.

![BLOG-2586 6](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/3aBbNG4Fc7TY6MTugLl3BE/064fb17761aebbce737a5a4518a14235/BLOG-2586_6.png)

To defend against high packet rate attacks, you need to be able to inspect and discard the bad packets using as few CPU cycles as possible, leaving enough CPU to process the good packets. You can additionally acquire more, or faster, CPUs to perform the processing — but that can be a very lengthy process that bears high costs.

### Exhausting network bandwidth

Network bandwidth is the total amount of data per time that can be delivered to a server. You can think of bandwidth like a pipe to transport water. The amount of water we can deliver through a drinking straw is less than what we could deliver through a garden hose. If an attacker is able to push more garbage data into the pipe than it can deliver, then both the bad data *and* the good data will be discarded upstream, at the entrance to the pipe, and the DDoS is therefore successful.

![BLOG-2586 7](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/OehVItOhGfP9ApllRvDDM/fce73e6f375173a1a53bc22026e0b9b1/BLOG-2586_7.png)

Defending against attacks that can saturate network bandwidth can be difficult because there is very little that can be done if you are on the downstream side of the saturated pipe. There are really only a few choices: you can get a bigger pipe, you can potentially find a way to move the good traffic to a new pipe that isn’t saturated, or you can hopefully ask the upstream side of the pipe to stop sending some or all of the data into the pipe.

## Generating DDoS attacks

If we think about what this means from the attackers point of view you realize there are similar constraints. Just as it takes CPU cycles to receive a packet, it also takes CPU cycles to create a packet. If, for example, the cost to send and receive a packet were equal, then the attacker would need an equal amount of CPU power to generate the attack as we would need to defend against it. In most cases this is not true — there is a cost asymmetry, as the attacker is able to generate packets using fewer CPU cycles than it takes to receive those packets. However, it is worth noting that generating attacks is not free and can require a large amount of CPU power.

Saturating network bandwidth can be even more difficult for an attacker. Here the attacker needs to be able to output more bandwidth than the target service has allocated. They actually need to be able to exceed the capacity of the receiving service. This is so difficult that the most common way to achieve a network bandwidth attack is to use a reflection/amplification attack method, for example a [DNS Amplification attack](https://www.cloudflare.com/learning/ddos/dns-amplification-ddos-attack/). These attacks allow the attacker to send a small packet to an intermediate service, and the intermediate service will send a large packet to the victim.

In both scenarios, the attacker needs to acquire or gain access to many devices to generate the attack. These devices can be acquired in a number of different ways. They may be server class machines from cloud providers or hosting services, or they can be compromised devices like DVRs, routers, and webcams that have been infected with the attacker’s malware. These machines together form the botnet.

## How Cloudflare defends against large attacks

Now that we understand the fundamentals of how DDoS attacks work, we can explain how Cloudflare can defend against these attacks.

### Spreading the attack surface using global anycast

The first not-so-secret ingredient is that Cloudflare’s network is built on [anycast](https://www.cloudflare.com/learning/cdn/glossary/anycast-network/). In brief, anycast allows a single IP address to be advertised by multiple machines around the world. A packet sent to that IP address will be served by the closest machine. This means when an attacker uses their distributed botnet to launch an attack, the attack will be received in a distributed manner across the Cloudflare network. An infected DVR in Dallas, Texas will send packets to a Cloudflare server in Dallas. An infected webcam in London will send packets to a Cloudflare server in London.

![BLOG-2586 8](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/48tW6A6ACUT4Fd9h3l70F4/c6bcea8f037fc853477d0987c939e007/BLOG-2586_8.png)

*Anycast vs. Unicast networks*

Our anycast network additionally allows Cloudflare to allocate compute and bandwidth resources closest to the regions that need them the most. Densely populated regions will generate larger amounts of legitimate traffic, and the data centers placed in those regions will have more bandwidth and CPU resources to meet those needs. Sparsely populated regions will naturally generate less legitimate traffic, so Cloudflare data centers in those regions can be sized appropriately. Since attack traffic is mainly coming from compromised devices, those devices will tend to be distributed in a manner that matches normal traffic flows sending the attack traffic proportionally to datacenters that can handle it. And similarly, within the datacenter, traffic is distributed across multiple machines.

Additionally, for high bandwidth attacks, Cloudflare’s network has another advantage. A large proportion of traffic on the Cloudflare network does not consume bandwidth in a symmetrical manner. For example, an HTTP request to get a webpage from a site behind Cloudflare will be a relatively small incoming packet, but produce a larger amount of outgoing traffic back to the client. This means that the Cloudflare network tends to egress far more legitimate traffic than we receive. However, the network links and bandwidth allocated are symmetrical, meaning there is an abundance of ingress bandwidth available to receive volumetric attack traffic.

### Generating real-time signatures

By the time you’ve reached an individual server inside a datacenter, the bandwidth of the attack has been distributed enough that none of the upstream links are saturated. That doesn’t mean the attack has been fully stopped yet, since we haven’t dropped the bad packets. To do that, we need to sample traffic, qualify an attack, and create rules to block the bad packets.

Sampling traffic and dropping bad packets is the job of our [l4drop](https://blog.cloudflare.com/l4drop-xdp-ebpf-based-ddos-mitigations/) component, which uses [XDP (eXpress Data Path)](https://netdevconf.info/2.1/papers/Gilberto_Bertin_XDP_in_practice.pdf) and leverages an extended version of the Berkeley Packet Filter known as [eBPF (extended BPF)](https://blog.cloudflare.com/tag/ebpf/). This enables us to execute custom code in kernel space and process (drop, forward, or modify) each packet directly at the network interface card (NIC) level. This component helps the system drop packets efficiently without consuming excessive CPU resources on the machine.

![BLOG-2586 9](https://cf-assets.www.cloudflare.com/zkvhlag99gkb/1NUxGTvKFs5l6G2UCSxvqw/3632f6728f9361123169d9694c807f0b/BLOG-2586_9.png)

*Cloudflare DDoS protection system overview*

We use XDP to sample packets to look for suspicious attributes that indicate an attack. The samples include fields such as the source IP, source port, destination IP, destination port, protocol, TCP flags, sequence number, options, packet rate and more. This analysis is conducted by the *denial of service daemon (dosd).* *Dosd* holds our secret sauce. It has many *filters* which instruct it, based on our curated heuristics, when to initiate mitigation. To our customers, these filters are logically grouped by attack vectors and exposed as the [DDoS Managed Rules](https://developers.cloudflare.com/ddos-protection/managed-rulesets/). Our customers can [customize their behavior](https://developers.cloudflare.com/ddos-protection/managed-rulesets/adjust-rules/) to some extent, as needed.

As it receives samples from XDP, dosd will generate multiple permutations of fingerprints for suspicious traffic patterns. Then, using a data streaming algorithm, dosd will identify the most optimal fingerprints to mitigate the attack. Once an attack is qualified, dosd will push a mitigation rule inline as an eBPF program to surgically drop the attack traffic.

The detection and mitigation of attacks by dosd is done at the server level, at the data center level and at the global level — and it’s all software defined. This makes our network extremely resilient and leads to almost instant mitigation. There are no out-of-path “scrubbing centers” or “scrubbing devices”. Instead, each server runs the full stack of the Cloudflare product suite including the DDoS detection and mitigation component. And it is all done autonomously. Each server also *gossips (multicasts)* mitigation instructions within a data center between servers, and globally between data centers. This ensures that whether an attack is localized or globally distributed, dosd will have already installed mitigation rules inline to ensure a robust mitigation.

## Strong defenses against strong attacks

Our software-defined, autonomous DDoS detection and mitigation systems run across our entire network. In this post we focused mainly on our dynamic fingerprinting capabilities, but our arsenal of defense systems is much larger. The [Advanced TCP Protection](https://developers.cloudflare.com/ddos-protection/tcp-protection/) system and [Advanced DNS Protection](https://developers.cloudflare.com/ddos-protection/dns-protection/) system work alongside our dynamic fingerprinting to identify sophisticated and highly randomized TCP-based DDoS attacks and also leverages statistical analysis to thwart complex DNS-based DDoS attacks. Our defenses also incorporate real-time threat intelligence, traffic profiling, and machine learning classification as part of our [Adaptive DDoS Protection](https://developers.cloudflare.com/ddos-protection/managed-rulesets/adaptive-protection/) to mitigate traffic anomalies.

Together, these systems, alongside the full breadth of the Cloudflare Security portfolio, are built atop of the Cloudflare network — one of the largest networks in the world — to ensure our customers are protected from the largest attacks in the world.

Cloudflare's connectivity cloud protects [entire corporate networks](https://www.cloudflare.com/network-services/), helps customers build [Internet-scale applications efficiently](https://workers.cloudflare.com/), accelerates any [website or Internet application](https://www.cloudflare.com/performance/accelerate-internet-applications/), [wards off DDoS attacks](https://www.cloudflare.com/ddos/), keeps [hackers at bay](https://www.cloudflare.com/application-security/), and can help you on [your journey to Zero Trust](https://www.cloudflare.com/products/zero-trust/).

Visit [1.1.1.1](https://one.one.one.one/) from any device to get started with our free app that makes your Internet faster and safer.

To learn more about our mission to help build a better Internet, [start here](https://www.cloudflare.com/learning/what-is-cloudflare/). If you're looking for a new career direction, check out [our open positions](https://www.cloudflare.com/careers).

  [DDoS](/tag/ddos/)[Attacks](/tag/attacks/)[Trends](/tag/trends/)[Security](/tag/security/)