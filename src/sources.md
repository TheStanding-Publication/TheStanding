---
layout: layouts/base.njk
title: Monitoring sources
permalink: /sources/
eleventyExcludeFromCollections: true
---

# Monitoring sources

This is the public, curated list of news and government sources used by The Standing's automated monitoring system. The list ensures transparency about where stories come from and is maintained as part of the publication's commitment to editorial accountability.

## National news outlets

{% for outlet in monitoringSources.national_news %}
### {{ outlet.name }}

- **Type:** {{ outlet.type }}
- **Coverage:** {{ outlet.coverage }}
- **Reliability:** {{ outlet.reliability }}
{% if outlet.rss_feed %}- **RSS feed:** [{{ outlet.rss_feed }}]({{ outlet.rss_feed }}){% endif %}
- **Notes:** {{ outlet.notes }}

{% endfor %}

## Government & official sources

{% for source in monitoringSources.government_sources %}
### {{ source.name }}

- **Type:** {{ source.type }}
- **Coverage:** {{ source.coverage }}
- **Authority:** {{ source.reliability }}
{% if source.rss_feed %}- **RSS feed:** [{{ source.rss_feed }}]({{ source.rss_feed }}){% endif %}
{% if source.url %}- **URL:** [{{ source.url }}]({{ source.url }}){% endif %}
- **Notes:** {{ source.notes }}

{% endfor %}

## Civil rights & democracy watchdog organizations

{% for watchdog in monitoringSources.watchdog_sources %}
### {{ watchdog.name }}

- **Type:** {{ watchdog.type }}
- **Coverage:** {{ watchdog.coverage }}
- **Reliability:** {{ watchdog.reliability }}
- **URL:** [{{ watchdog.url }}]({{ watchdog.url }})
- **Notes:** {{ watchdog.notes }}

{% endfor %}

## Press freedom & accountability

{% for org in monitoringSources.press_freedom_sources %}
### {{ org.name }}

- **Type:** {{ org.type }}
- **Coverage:** {{ org.coverage }}
- **Reliability:** {{ org.reliability }}
- **URL:** [{{ org.url }}]({{ org.url }})
- **Notes:** {{ org.notes }}

{% endfor %}

## Investigative & specialized outlets

{% for outlet in monitoringSources.specialized_sources %}
### {{ outlet.name }}

- **Type:** {{ outlet.type }}
- **Coverage:** {{ outlet.coverage }}
- **Reliability:** {{ outlet.reliability }}
{% if outlet.rss_feed %}- **RSS feed:** [{{ outlet.rss_feed }}]({{ outlet.rss_feed }}){% endif %}
{% if outlet.url %}- **URL:** [{{ outlet.url }}]({{ outlet.url }}){% endif %}
- **Notes:** {{ outlet.notes }}

{% endfor %}

## About this list

Sources are selected for:
1. **National reach and reliability** — major outlets with editorial standards
2. **Coverage of democracy/rights/accountability issues** — focusing on The Standing's core subject matter
3. **Transparency and editorial standards** — outlets with public policies and corrections procedures
4. **Mix of perspectives** — mainstream news, government sources, and civil society watchdogs

All sources are verified for current RSS feed URLs and accessibility.

### Future expansions

- **Local news aggregation** (by state)
- **Social media monitoring** (Twitter/X, TikTok, Reddit)
- **International news** (for foreign government actions affecting US governance)
- **Academic sources** (law reviews, research institutions)

### Contributing source suggestions

Have a source you think The Standing should monitor? [Email the editor](mailto:editor@thestanding.us) with:

1. Source name and URL
2. What type of coverage it provides
3. Why it would be valuable for tracking democratic accountability

Sources are added after editorial review and verification.

---

*This list is public because The Standing's credibility depends on transparency about where stories come from. Readers should be able to verify that the sources meet The Standing's editorial standards. For updates, see the [GitHub repository](https://github.com/thestanding/thestanding).*
