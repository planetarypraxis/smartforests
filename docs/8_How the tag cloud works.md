# How does the tag cloud work?

## What is the tag cloud?

The tag cloud is displayed on the [main page of the website](https://atlas.smartforests.net/en-gb/). It is also displayed on the footer of most other pages, for example on [Logbooks](https://atlas.smartforests.net/en/logbooks/cop26/) and [contributor pages](https://atlas.smartforests.net/en/contributors/danilo-urzedo/).

It is a way in which people navigate the site and is intended to display the inter-relation between topics and the topic of smart forests as a whole.

Authors of the Atlas select tags for content they add to the Atlas based on their understanding of the topic at hand. These tags are then mapped to one another to display this tag cloud.

## Design goals of the tag cloud

The tag cloud is intended to do three things.

1. Work out which topics are more central to the material on the site. This is what drives the main page tag cloud.
2. Work out how topics are related to one another. This is what drives the on page tag cloud.
3. Show this visually.

We want to show the absolute centrality of a topic and the relative centrality of a topic and the set of topics that are related to it. These topics are defined by user selected tags, where a researcher draws on their knowledge of a topic in order to tag it appropriately.

## How does it work?

The technique used here draws on [graph theory](https://en.wikipedia.org/wiki/Graph_theory) and in particularly [Eigenvector centrality](https://en.wikipedia.org/wiki/Eigenvector_centrality). Eigenvector centrality is most famously deployed in Google's [PageRank](https://en.wikipedia.org/wiki/PageRank) algorithm. The difference between this and something like PageRank is that PageRank is concerned with ranking pages on the basis of how many other pages link to them. Here we are ranking tags based on how other tags link to them.

Here we use page to mean any page on the Atlas, be it a Logbook, say, or a Logbook entry. 

When someone changes the tags a page is associated with and creates a new page that has tags, we perform a breadth first search of the page that it is linked to it the tag. We then look at the tags on the pages in that search, up to a fixed number of pages. This constructs a list of related topics, through tags. We limit this to 100 tags, as everything is at some point related to everything else.

When a page is displayed and we show a tag cloud, we search through all of the topics that are related to the page that you're on then construct a list of related topics and we rank them according to that degree of connectedness within the collection of topics that are related to that page.

For the question of absolute centrality, this is a bit harder, as we don't have any topic to start from. So we look through the clusters of topics we created for the purposes of determining the relatedness to a page. We then rank these according to the degree of total connectedness that exists between then. We the take the top scoring 30 or so and use as the space in which we are searching for further nodes. This helps us map the differences between them and display this visually.

Initial versions of the main page map were to visually dense to be useful and attractive. So we limit this to a random selection of 30 tags.

## Where can we find the code that relates to the tag cloud?

Describing this is quite complex in words, so it is easier to describe them in code.

- The [AtlasTag class](https://github.com/planetarypraxis/smartforests/blob/42510bfc1158dacd04669982aa52ecfc9be950a4/logbooks/models/snippets.py) defines how tags work. This generates the cloud when tags are saved or deleted.
- The [TagCloud class](https://github.com/planetarypraxis/smartforests/blob/main/logbooks/models/tag_cloud.py) describes how tag clouds are created. 
This contains [the core algorithm] regarding tag relatedness (https://github.com/planetarypraxis/smartforests/blob/main/logbooks/models/tag_cloud.py#L192-L242).
- [`tag_cloud.js`](https://github.com/planetarypraxis/smartforests/blob/main/smartforests/static/js/tag_cloud.js) Javascript code handles the display of tag clouds.

The Javascript code depends on [D3.js](https://d3js.org/) and [cola.js](https://ialab.it.monash.edu/webcola/) for displaying the graph.



