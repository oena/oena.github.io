---
layout: post
title: A (very late) Tidy Tuesday
#subtitle: Practicing Vizualization in Python with a malaria dataset
#gh-repo: oena/oena.github.io
#gh-badge: [star, fork, follow]
tags: [python, visualization, malaria]
comments: false
readtime: true
---


Some plots from [this tidy Tuesday](https://github.com/rfordatascience/tidytuesday/tree/master/data/2018/2018-11-13) data set.


### 0. Setup and Get Data 


```python
%matplotlib inline 
import pandas as pd 
import seaborn as sns 
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "notebook"
```


```python
# Looking at the dataset corresponding to Malaria deaths by age across
# the world and time. 
malaria_deaths_url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2018/2018-11-13/malaria_deaths_age.csv"
malaria_deaths_df = pd.read_csv(malaria_deaths_url)
malaria_deaths_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Unnamed: 0</th>
      <th>entity</th>
      <th>code</th>
      <th>year</th>
      <th>age_group</th>
      <th>deaths</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Afghanistan</td>
      <td>AFG</td>
      <td>1990</td>
      <td>Under 5</td>
      <td>184.606435</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Afghanistan</td>
      <td>AFG</td>
      <td>1991</td>
      <td>Under 5</td>
      <td>191.658193</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Afghanistan</td>
      <td>AFG</td>
      <td>1992</td>
      <td>Under 5</td>
      <td>197.140197</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>Afghanistan</td>
      <td>AFG</td>
      <td>1993</td>
      <td>Under 5</td>
      <td>207.357753</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>Afghanistan</td>
      <td>AFG</td>
      <td>1994</td>
      <td>Under 5</td>
      <td>226.209363</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>30775</th>
      <td>30776</td>
      <td>Zimbabwe</td>
      <td>ZWE</td>
      <td>2012</td>
      <td>50-69</td>
      <td>103.185111</td>
    </tr>
    <tr>
      <th>30776</th>
      <td>30777</td>
      <td>Zimbabwe</td>
      <td>ZWE</td>
      <td>2013</td>
      <td>50-69</td>
      <td>100.113293</td>
    </tr>
    <tr>
      <th>30777</th>
      <td>30778</td>
      <td>Zimbabwe</td>
      <td>ZWE</td>
      <td>2014</td>
      <td>50-69</td>
      <td>99.013890</td>
    </tr>
    <tr>
      <th>30778</th>
      <td>30779</td>
      <td>Zimbabwe</td>
      <td>ZWE</td>
      <td>2015</td>
      <td>50-69</td>
      <td>98.091738</td>
    </tr>
    <tr>
      <th>30779</th>
      <td>30780</td>
      <td>Zimbabwe</td>
      <td>ZWE</td>
      <td>2016</td>
      <td>50-69</td>
      <td>97.402058</td>
    </tr>
  </tbody>
</table>
<p>30780 rows × 6 columns</p>
</div>



### 1. How much do malaria deaths change across age groups by year?


```python
# First, what are the age groups? 
malaria_deaths_df["age_group"].unique()
```




    array(['Under 5', '70 or older', '5-14', '15-49', '50-69'], dtype=object)




```python
# orders for age group, so they make sense
age_orders = ["Under 5", "5-14", "15-49", "50-69", "70 or older"]
(
    sns.
    lineplot(x="year", y="deaths",
             hue="age_group", 
             hue_order = age_orders,
             palette="bright",
             data=malaria_deaths_df).
    set_title("Malaria deaths across time, by age group")
)
```




    Text(0.5, 1.0, 'Malaria deaths across time, by age group')




![png](output_6_1.png)


Wow, deaths in the "Under 5" age group seem disproportionately high. We can see in the plot above that there is some variation by year, but on the whole deaths in the under 5 group range between 12,000-15,000 or so. So, let's take the average in the under 5 age group and see if there are any patterns by country. 

### 2. How does average death rate in the under 5 age group vary by country? 

First, what are the countries represented? Any non-countries included in the country column? 


```python
malaria_deaths_df["entity"].unique()
```




    array(['Afghanistan', 'Albania', 'Algeria', 'American Samoa',
           'Andean Latin America', 'Andorra', 'Angola', 'Antigua and Barbuda',
           'Argentina', 'Armenia', 'Australasia', 'Australia', 'Austria',
           'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados',
           'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan',
           'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil',
           'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia',
           'Cameroon', 'Canada', 'Cape Verde', 'Caribbean',
           'Central African Republic', 'Central Asia', 'Central Europe',
           'Central Latin America', 'Central Sub-Saharan Africa', 'Chad',
           'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica',
           "Cote d'Ivoire", 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic',
           'Democratic Republic of Congo', 'Denmark', 'Djibouti', 'Dominica',
           'Dominican Republic', 'East Asia', 'Eastern Europe',
           'Eastern Sub-Saharan Africa', 'Ecuador', 'Egypt', 'El Salvador',
           'England', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia',
           'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia',
           'Germany', 'Ghana', 'Greece', 'Greenland', 'Grenada', 'Guam',
           'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti',
           'High SDI', 'High-income Asia Pacific', 'High-middle SDI',
           'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran',
           'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan',
           'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan', 'Laos',
           'Latin America and Caribbean', 'Latvia', 'Lebanon', 'Lesotho',
           'Liberia', 'Libya', 'Lithuania', 'Low SDI', 'Low-middle SDI',
           'Luxembourg', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia',
           'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania',
           'Mauritius', 'Mexico', 'Micronesia (country)', 'Middle SDI',
           'Moldova', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique',
           'Myanmar', 'Namibia', 'Nepal', 'Netherlands', 'New Zealand',
           'Nicaragua', 'Niger', 'Nigeria', 'North Africa and Middle East',
           'North America', 'North Korea', 'Northern Ireland',
           'Northern Mariana Islands', 'Norway', 'Oceania', 'Oman',
           'Pakistan', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay',
           'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico',
           'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saint Lucia',
           'Saint Vincent and the Grenadines', 'Samoa',
           'Sao Tome and Principe', 'Saudi Arabia', 'Scotland', 'Senegal',
           'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia',
           'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa',
           'South Asia', 'South Korea', 'South Sudan', 'Southeast Asia',
           'Southern Latin America', 'Southern Sub-Saharan Africa', 'Spain',
           'Sri Lanka', 'Sub-Saharan Africa', 'Sudan', 'Suriname',
           'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Taiwan',
           'Tajikistan', 'Tanzania', 'Thailand', 'Timor', 'Togo', 'Tonga',
           'Trinidad and Tobago', 'Tropical Latin America', 'Tunisia',
           'Turkey', 'Turkmenistan', 'Uganda', 'Ukraine',
           'United Arab Emirates', 'United Kingdom', 'United States',
           'United States Virgin Islands', 'Uruguay', 'Uzbekistan', 'Vanuatu',
           'Venezuela', 'Vietnam', 'Wales', 'Western Europe',
           'Western Sub-Saharan Africa', 'World', 'Yemen', 'Zambia',
           'Zimbabwe'], dtype=object)



Mostly seems fine, but let's exclude regions (eg. "World", "Sub-Saharan Africa", etc) since we just want to look at this by country. We also need to reorganize the data a little, because we only want the under 5 data, and we want it averaged by year. 


```python
# Get under 5 data only 
malaria_under5_deaths = malaria_deaths_df.loc[malaria_deaths_df["age_group"] == "Under 5"]

# Remove regions from the "entity" (ie. country) column 
regions_to_exclude = ["Andean Latin America",
                      "Australasia",
                      "Central Asia", 
                      "Central Europe",
                      "Central Latin America", 
                      "Central Sub-Saharan Africa",
                      "East Asia", 
                      "Eastern Europe",
                      "Eastern Sub-Saharan Africa",
                      "High SDI", 
                      "High-income Asia Pacific", 
                      "High-middle SDI",
                      "Latin America and Caribbean",
                      "Low SDI", 
                      "Low-middle SDI",
                      "Middle SDI",
                      "North Africa and Middle East",
                      "North America",
                      "South Asia",
                      "Southeast Asia",
                      "Southern Latin America", 
                      "Southern Sub-Saharan Africa",
                      "Sub-Saharan Africa",
                      "Tropical Latin America",
                      "Western Europe",
                      "Western Sub-Saharan Africa",
                      "World"]
malaria_under5_deaths = malaria_under5_deaths.loc[~malaria_under5_deaths["entity"].isin(regions_to_exclude)]

# Get the average number of deaths by country
malaria_under5_avg_deaths = malaria_under5_deaths.groupby("entity").mean()
```

Let's reset the index (we need it as a column), round the number of deaths for readability, and add a `text` column (for what is shown upon hover) combining the Country and average death values: 


```python
malaria_under5_avg_deaths.reset_index(inplace=True)
malaria_under5_avg_deaths = malaria_under5_avg_deaths.round(2)
malaria_under5_avg_deaths["text"] = malaria_under5_avg_deaths["entity"] + ": " + malaria_under5_avg_deaths["deaths"].astype(str)
malaria_under5_avg_deaths.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>entity</th>
      <th>Unnamed: 0</th>
      <th>year</th>
      <th>deaths</th>
      <th>text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Afghanistan</td>
      <td>14</td>
      <td>2003</td>
      <td>315.89</td>
      <td>Afghanistan: 315.89</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Albania</td>
      <td>41</td>
      <td>2003</td>
      <td>0.00</td>
      <td>Albania: 0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Algeria</td>
      <td>68</td>
      <td>2003</td>
      <td>0.50</td>
      <td>Algeria: 0.5</td>
    </tr>
    <tr>
      <th>3</th>
      <td>American Samoa</td>
      <td>95</td>
      <td>2003</td>
      <td>0.00</td>
      <td>American Samoa: 0.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Andorra</td>
      <td>149</td>
      <td>2003</td>
      <td>0.00</td>
      <td>Andorra: 0.0</td>
    </tr>
  </tbody>
</table>
</div>




```python
malaria_under5_deaths.loc[malaria_under5_deaths["deaths"] == malaria_under5_deaths["deaths"].max()]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Unnamed: 0</th>
      <th>entity</th>
      <th>code</th>
      <th>year</th>
      <th>age_group</th>
      <th>deaths</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>3906</th>
      <td>3907</td>
      <td>Nigeria</td>
      <td>NGA</td>
      <td>2008</td>
      <td>Under 5</td>
      <td>261794.558211</td>
    </tr>
  </tbody>
</table>
</div>




```python
import os 
os.getcwd()
```




    '/Users/oana/Documents/github/oena.github.io/ipynbs'




```python
fig = go.Figure(data=go.Choropleth(
    locationmode = "country names",
    locations = malaria_under5_avg_deaths["entity"],
    z = malaria_under5_avg_deaths["deaths"],
    text = malaria_under5_avg_deaths["text"],
    autocolorscale=True,
    reversescale=False,
    colorbar_title = 'Average under 5 malaria deaths',
))

fig.update_layout(
    title_text='Average under 5 malaria deaths by country: 1990-2016',
    geo=dict(
        showcoastlines=True,
    ),
)
# Write to html so you can see it outside of this notebook 
fig.write_html("/Users/oana/Documents/github/oena.github.io/assets/html/world_malaria_map.html")
```

It's very clear from this plot that Nigeria has far and away more cases of malaria in children under 5 than any other country in the world; unsurprisingly (given that malaria is spread through mosquitos), geographically close countries like Niger, Cameroon, and Burkina Faso have high average death rates in young children too. 

It is worth noting that Nigeria is Africa's most populous country; so, in following up on this in more depth it would probably make sense to normalize these values by population size. However, [this health policy report](http://www.hcs.harvard.edu/epihc/currentissue/Fall2001/carrington.htm) notes that Nigeria has a number of specific issues that make malaria such a significant problem in its population: 

> Most of the rural areas do not have access to good health care systems. Usually there are no accessible roads to the health centers, which in turn are poorly equipped and have inadequate drugs for malaria treatment. Drug resistant malaria is common and anti malarial drugs are becoming less effective as the plasmodium parasite develops resistance to affordable drugs. This poses a serious threat to clinical management and treatment of malaria. People cannot afford anti-malarial drugs so they tend to self medicate with local herbs. Children wear little clothing during the day and at night due to heat and humidity, thus leaving their bodies exposed to mosquito bites. Rural dwellers cannot afford to purchase bed nets. Mud houses are poorly constructed and are surrounded by bushes. Water is collected from streams and wells and left standing in open clay pots since there are usually no running taps. Recommendations to Control Malaria in Rural Nigeria Within the control strategy for malaria, a multi-dimensional approach is needed.

This brings us to our last question (for this visualization exercise): 

### 3. How similar are malaria death rates (again for the under 5 age group) in Nigeria vs. the other countries close to it over time? 

For this, we'll consider Cameroon, Niger, Benin, Chad, Central African Republic, Mali, Ghana, Togo, and Benin. 

We begin by filtering the under 5 data set to these countries only, and then correlating values over time (using Spearman correlation since the death rates are on such different scales): 


```python
# Filter to relevant countries 
countries_close_to_nigeria = ["Nigeria",
                              "Cameroon", 
                              "Niger", 
                              "Benin", 
                              "Chad", 
                              "Central African Republic", 
                              "Mali", 
                              "Ghana", 
                              "Togo"]
nigeria_neighbors_under5_deaths = malaria_under5_deaths.loc[malaria_under5_deaths["entity"].isin(countries_close_to_nigeria)]

# Pivot data frame to wide
nigeria_neighbors_under5_deaths = nigeria_neighbors_under5_deaths.pivot(index='year', columns='entity', values='deaths')

# Correlate deaths by year across countries considered
nigeria_neighbors_under5_cors = nigeria_neighbors_under5_deaths.corr(method="spearman")
```


```python
p =sns.clustermap(nigeria_neighbors_under5_cors, annot=True)
p.fig.suptitle("Correlation of malaria deaths: 1990-2016, children under 5") 
```




    Text(0.5, 0.98, 'Correlation of malaria deaths: 1990-2016, children under 5')




![png](output_19_1.png)


Unsurprisingly, all of the correlation values are fairly high; however, it's surprising that Nigeria's malaria death rates (in the under 5 age group) are most correlated with Ghana and the Central African Republic, which do not immediately border it. 
