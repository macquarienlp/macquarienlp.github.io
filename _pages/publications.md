---
title: "Macquarie NLP group - Publications"
layout: gridlay
excerpt: "Macquarie NLP group -- Publications."
sitemap: false
permalink: /publications/
---


# Publications

## Group highlights

**At the end of this page, you can find the [full list of publications](#full-list-of-publications).**

{% assign number_printed = 0 %}
{% for publi in site.data.publist %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if publi.highlight == 1 %}

{% if even_odd == 0 %}
<div class="row">
{% endif %}

<div class="col-sm-6 clearfix">
 <div class="well">
  <pubtit>{{ publi.title }}</pubtit>
  [comment]: <>  <img src="{{ site.url }}{{ site.baseurl }}/images/pubpic/{{ publi.image }}" class="img-responsive" width="33%" style="float: left" />
  [comment]: <>  <p>{{ publi.description }}</p>
  <p><em>{{ publi.authors }}</em></p>
  <p><em>{{ publi.year }}</em></p>
  <p><strong><a href="{{ publi.link.url }}">{{ publi.link.display }}</a></strong></p>
  <p class="text-danger"><strong> {{ publi.news1 }}</strong></p>
  <p> {{ publi.news2 }}</p>
 </div>
</div>

{% assign number_printed = number_printed | plus: 1 %}

{% if even_odd == 1 %}
</div>
{% endif %}

{% endif %}
{% endfor %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if even_odd == 1 %}
</div>
{% endif %}

<p> &nbsp; </p>


## Full List of publications

<style>
  details.pub-year { border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px; }
  details.pub-year > summary { cursor: pointer; padding: 10px 15px; background: #f5f5f5; font-size: 1.2em; font-weight: bold; }
  details.pub-year[open] > summary { border-bottom: 1px solid #ddd; }
  details.pub-year .pub-entry { padding: 8px 15px; }
</style>

{% assign pubs_by_year = site.data.publist | group_by: "year" | sort: "name" | reverse %}
{% for year_group in pubs_by_year %}
<details class="pub-year" markdown="0">
  <summary>{{ year_group.name }}</summary>
  {% for publi in year_group.items %}
  <div class="pub-entry">
    {{ publi.title }}<br />
    <em>{{ publi.authors }}</em><br />
    <a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
  </div>
  {% endfor %}
</details>
{% endfor %}
