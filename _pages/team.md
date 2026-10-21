---
title: "Macquarie NLP group - Team"
layout: gridlay
excerpt: "Macquarie NLP group: Team members"
sitemap: false
permalink: /team/
---

# Group Members

 **We're always looking for keen new members to join the team.  There are regular rounds of PhD and master degree scholarships, and from time to time postdoctoral or research associate positions** [(see openings)]({{ site.url }}{{ site.baseurl }}/vacancies) **!**


Jump to [staff](#staff), [research students](#master-and-bachelor-students).

## Staff
{% assign number_printed = 0 %}
{% for member in site.data.team_members %}

{% assign even_odd = number_printed | modulo: 2 %}

{% if even_odd == 0 %}
<div class="row">
{% endif %}

<div class="col-sm-6 clearfix">
  <img src="{{ site.url }}{{ site.baseurl }}/images/teampic/{{ member.photo }}" class="img-responsive" width="25%" style="float: left" />
  <h4>{{ member.name }}</h4>
  <i>{{ member.info }} <br><{{ member.email }}><br><a href="{{ member.scholar }}" target="_blank">Google Scholar</a></i> <!--<br>email: <{{ member.email }}></i> -->
  <ul style="overflow: hidden">

  {% if member.number_educ == 1 %}
  <li> {{ member.interest1 }} </li>
  {% endif %}

  {% if member.number_educ == 2 %}
  <li> {{ member.interest1 | markdownify}} </li>
  <li> {{ member.interest2 | markdownify}} </li>
  {% endif %}

  {% if member.number_educ == 3 %}
  <li> {{ member.interest1 }} </li>
  <li> {{ member.interest2 }} </li>
  <li> {{ member.interest3 }} </li>
  {% endif %}

  {% if member.number_educ == 4 %}
  <li> {{ member.interest1 }} </li>
  <li> {{ member.interest2 }} </li>
  <li> {{ member.interest3 }} </li>
  <li> {{ member.interest4 }} </li>
  {% endif %}

  {% if member.number_educ == 5 %}
  <li> {{ member.interest1 }} </li>
  <li> {{ member.interest2 }} </li>
  <li> {{ member.interest3 }} </li>
  <li> {{ member.interest4 }} </li>
  <li> {{ member.interest5 }} </li>
  {% endif %}

  </ul>
</div>

{% assign number_printed = number_printed | plus: 1 %}

{% if even_odd == 1 %}
</div>
{% endif %}

{% endfor %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if even_odd == 1 %}
</div>
{% endif %}



## Research Students
{% assign number_printed = 0 %}
{% for member in site.data.students %}

{% assign even_odd = number_printed | modulo: 2 %}

{% if even_odd == 0 %}
<div class="row">
{% endif %}

<div class="col-sm-6 clearfix">
  <img src="{{ site.url }}{{ site.baseurl }}/images/teampic/{{ member.photo }}" class="img-responsive" width="25%" style="float: left" />
  <h4>{{ member.name }}</h4>
  <i><{{ member.email }}><br></i>
  <!--<i>{{ member.info }} <!-- <br>email: <{{ member.email }}></i> -->
  <!--<i>email: <{{ member.email }}></i> -->
  {% if member.has_scholar == 1 %}
  <a href="{{ member.scholar }}" target="_blank">Google Scholar</a>
  {% endif %}
  {% if member.has_webpage == 1 %}
  <a href="{{ member.webpage }}" target="_blank">Webpage</a>
  {% endif %}

  <ul style="overflow: hidden">

  

  {% if member.number_educ == 1 %}
  <li> {{ member.interest1 }} </li>
  {% endif %}

  {% if member.number_educ == 2 %}
  <li> {{ member.interest1 }} </li>
  <li> {{ member.interest2 }} </li>
  {% endif %}

  {% if member.number_educ == 3 %}
  <li> {{ member.interest1 }} </li>
  <li> {{ member.interest2 }} </li>
  <li> {{ member.interest3 }} </li>
  {% endif %}

  {% if member.number_educ == 4 %}
  <li> {{ member.interest1 }} </li>
  <li> {{ member.interest2 }} </li>
  <li> {{ member.interest3 }} </li>
  <li> {{ member.interest4 }} </li>
  {% endif %}

  {% if member.number_educ == 5 %}
  <li> {{ member.interest1 }} </li>
  <li> {{ member.interest2 }} </li>
  <li> {{ member.interest3 }} </li>
  <li> {{ member.interest4 }} </li>
  <li> {{ member.interest5 }} </li>
  {% endif %}

  </ul>
</div>

{% assign number_printed = number_printed | plus: 1 %}

{% if even_odd == 1 %}
</div>
{% endif %}

{% endfor %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if even_odd == 1 %}
</div>
{% endif %}



<!---
## Alumni

{% assign number_printed = 0 %}
{% for member in site.data.alumni_members %}

{% assign even_odd = number_printed | modulo: 2 %}

{% if even_odd == 0 %}
<div class="row">
{% endif %}

<div class="col-sm-6 clearfix">
  <img src="{{ site.url }}{{ site.baseurl }}/images/teampic/{{ member.photo }}" class="img-responsive" width="25%" style="float: left" />
  <h4>{{ member.name }}</h4>
  <i>{{ member.duration }} <br> Role: {{ member.info }}</i>
  <ul style="overflow: hidden">

  </ul>
</div>

{% assign number_printed = number_printed | plus: 1 %}

{% if even_odd == 1 %}
</div>
{% endif %}

{% endfor %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if even_odd == 1 %}
</div>
{% endif %}

## Former visitors, BSc/ MSc students
<div class="row">

<div class="col-sm-4 clearfix">
<h4>Visitors</h4>
{% for member in site.data.alumni_visitors %}
{{ member.name }}
{% endfor %}
</div>

<div class="col-sm-4 clearfix">
<h4>Master students</h4>
{% for member in site.data.alumni_msc %}
{{ member.name }}
{% endfor %}
</div>

<div class="col-sm-4 clearfix">
<h4>Bachelor Students</h4>
{% for member in site.data.alumni_bsc %}
{{ member.name }}
{% endfor %}
</div>

</div>


[//]: ## Administrative Support
[//]: <a href="mailto:Rijsewijk@Physics.LeidenUniv.nl">Ellie van Rijsewijk</a> is helping us [//]: (and other groups) with administration.
-->
