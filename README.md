# Music Mining

In the universe of charted songs, why did some songs become nominated? Why were some songs awarded? Why did some songs stay on to top of the charts for so long, and others not? — Characteristics of the music, or the recording label behind it? — Can we establish causality? — Characteristics of music before and after artist signed to a major label.

Hypothesis: GRAMMY awards are all politics. It has more to do with the label more than how the band sounds. Music industry politics can't be described or measured systemically, and are represented instead in the unexplained variance. — Establish that all nominated and awarded music sounds the same.


What features of a song are similar across top 10 and bottom 10?

Later: what features of an album? snapshot of artist? 

Later: add artist nomination/award features later - hypothesis: if artist has won before, are they likely to win again?

Is it politics?
- Artists who have won have either 1. won previously; or 2. been nominated many times w/out winning.
- Only American artists


Use only tracks

Chart2000: only one artist
- Peak chart position
- Avg chart position
- Median chart position
- Number months its charted
- Total revenue

Next step:
- One dataset
- Spotify feature information
- Whether track nominated/won, category
- Number of months on chart
- Avg position on chart
- *** Aggregated chart dataset

track_won
track_nominated
artist_won
artist_nominated

Datasets:
- Spotify to Grammy
- Sample tracks features


NEED TO ADD:
- Label data
- Country data
- Artist first release?

NEXT:
- [ ] summarize charts
- [X] merge track features w/ grammy nominations
- [ ] merge track features w/ charts
- [ ] filter tracks for only relevant tracks
- [ ] track grammy and chart songs missing from tracks
- [ ] slices:
      - un-nominated & un-charted
      - charted, not nominated
      - not charted, nominated
      - winner
- [ ] slices (future): w/ labels
- [ ] GET RANDOM SONGS...
- 


FUTURE:
- [ ] create album-centric dataset, w/ albums that have been nominated,
- [ ] albums that track a particular artist through label history?
  - random sample artists that have won
  - select random albums before they won and after they won
  - download all tracks from album
  - create cluster or summary of album
  - compare


## Prior work
[Can the charts here tell us anything about long term trends](https://tsort.info/music/faq_peak_music.htm)

https://tsort.info/



## Dataset


I’ve compiled a dataset of Spotify tracks and their audio features, and assigned a category for their chart status, artist status and recording award status. The dataset is compiled from recordings nominated for a Grammy (n=~535), tracks that have entered the Chart2000 global aggregated monthly song chart (n=~3300), and a random sample (n=1000) from Spotify daily charts. The dataset is de-duplicated on track id, and limited to the years 2000-2021. The dataset is small (n=4237) but fairly balanced across the three categories.

It’s not “big data,” but it’ll make for more easily analysis. If we’d like to add more data, we can explore incorporating more songs from Spotify’s daily and weekly charts and viral charts, or another global charts aggregator (https://tsort.info/). The limiting factor is the number of tracks nominated for a Grammy (535) and (~75). In the future, we could add data based on nominated albums, or other recordings by artists that have charted or been nominated later or previously in their career. I think this is good for now though!

The goal of this dataset is to focus on the track audio features by creating three categories that summarize the details about the source datasets. They’re simple and non-exhaustive, and created to help merge and balance the data sources. There are opportunities to further develop these categories. So far, they are interesting and may lend themselves to natural clusters.

chart_status	Whether the track has charted. 0 = never charted, 1 = charted, 2 = charted top 25
award_status	Whether the track was nominated for a Grammy. 0 = never nominated, 1 = nominated, 2 = won Grammy
artist_status	Whether artist was nominated or won a Grammy prior to release. 0 = never nominated, 1 = previously nominated, 2 = previously won Grammy

Interesting findings so far: while there are quite a lot of recordings that chart and are never nominated, there are also a lot of recordings that are nominated and even win without ever having charted.

Dataset and data dictionary published to Google Drive. High level aggregates below.

no. tracks: 4237
no. chart2000 songs: 3313 (charts2000)
no. spotify chart songs: 1000 (spotifycharts.com)
no. grammy songs: 535
no. tracks w/out features: 1
no. track features w/out nominations: 3915
no. tracks w/out chart position: 319
no. charted songs w/ nominations: 216
no. songs w/out nomination or chart: 0


### Collection methodology

- Collection: nominated and awarded artists
    - Loop through Grammy awards and Billboard 100 lists
        - For each awarded and nominated artist:
            - For all of their release, distinct by release group:
                - Collect label and year
                - For all songs in a release:
                    - Collect EchoNest data from Spotify


Next steps:
- Combine grammy nominees and chart tracks together 

Curated list of labels:
[MusicMoz - Record Labels](https://musicmoz.org/Record_Labels/)
[GRAMMY Nominees - MusicBrainz](https://musicbrainz.org/series/216a2b1f-33e7-46a2-80d9-751ff7e20303)

Similar: [GitHub - JLUT/Billboard_Grammy_Project1: Using Top 100 Data and Grammy Winners from the past 20 years,  analyzed datasets to determine if a Grammy winner can be determined based on the Billboard Top 100.](https://github.com/JLUT/Billboard_Grammy_Project1)
[Grammy Awards | Kaggle](https://www.kaggle.com/unanimad/grammy-awards)

Alternative datasets: [Spotify Top 200 charts](https://rpubs.com/elgindykareem/top200charts)

## Preprocessing

* Calculate variables for artists: year of first award nomination,
  first award win, latest nomination, latest win, number of awards, number of nominations.
* Aggregate artist on the year?

## Using the data

* Artist nomination
* Album nomination
* Recording nomination

## Analysis
- Analysis
    - Add labels to identify the song and release that was nominated or awarded, and indicating whether an artist had been nominated or awarded, and the year the artist was nominated or awarded.
    - Label a release label as independent or major - clustering and validation using known labels?
    - Summarize albums and artists: PCA or clustering
    - Compare songs or releases before and after nomination or award
    - Compare grammy nominees vs grammy winners?
    - Predict projected revenue - [Chart2000.com: Music Charts 2000 - 2021](https://chart2000.com/about.htm#google_vignette)
    - Compare songs by major labels vs independent labels. What are characteristics of billboard songs or grammy nominees/winners that are independent musicians?
    - Cluster songs based on characteristics - see if they land on cluster around major labels
    

- Analysis
    - What factors are involved for a song to be nominated for an award? (e.g., H_A: revenue, top of charts)
    - What factors are involved for a song to be at the top of the charts? (e.g., H_A: high dancability)
    - Are the factors involved for a song to be nominated and to be at the top of the chart the same?
    - Find songs that are similar to a nominated or charted songs;  what factor separates them?
    - Cluster songs w/out award/chart status as a factor, colored by award/chart status; cluster again \
    - Is song/artist that's uncharted, unnominated, but sounds the same - are they unnoticed? are they signed/unsigned? are they young, old, washed out?
      - are they the next big thing? compare against artists nomination/award status 5 years later. (or signed by a label )
      - if they get signed, what happens after they're signed? do they win? do they chart? does their sound change?do they continue releaseing music? 
    - How much more likely is an artist to chart or be nominated if they've already won?
---

## Notes about Grammy awards dataset

Collected from MusicBrainz Grammy Awards event series and subseries release groups.
MusicBrainz data is aggregated from Wikipedia. 
[Grammy Award series](https://musicbrainz.org/series/64249380-b076-4a9d-aa41-e617d81fa1c9).

Grammy Nominees found in the [GRAMMY Nominees series](https://musicbrainz.org/series/216a2b1f-33e7-46a2-80d9-751ff7e20303).

Missing data exist for minor award categories: in many cases, only the award winners are credited. 
Nominees are credited in major awards, or after 2010. Examples shown below.

* [Album of the Year nominees 1960-2009](https://musicbrainz.org/series/64249380-b076-4a9d-aa41-e617d81fa1c9)
  winner only; 2010-2021 nominees and winner; 2022 nominees only
* Best Alternative Music Album
  1991-2009 winner only; 2010-2021 nominees and winner
  https://musicbrainz.org/series/16a89a2d-1d9e-4a29-a59b-a5e88304a75d
* Best Contemporary Instrumental Album
  2001-2020 winner only; 2021 nominees and winner
  https://musicbrainz.org/series/6d57cea7-9e36-45e9-bc6f-e012702c3383
* Best Country
  2001-2019 winner only; 2020 nominees and winner
  https://musicbrainz.org/series/b3db9d98-e65f-493e-89a3-e751d88d5802
* Best Dance Recording
  1998-2020 winner only; 2021 nominees and winner
  https://musicbrainz.org/series/5dc3275e-ac47-4391-9550-a4d469a97cec
* Best Dance/Electronic Album
  2005-2020 winners only; 2021 nominees and winner; 2022 nominees
  https://musicbrainz.org/series/292ebdfe-efab-4e6d-8cbb-5ba1f3bb67ee
* Best Folk Album
  2012-2020 winners only; 2021 nominees and winner
  https://musicbrainz.org/series/1a6331c0-770b-4930-9568-6cfa238e7c39
* Best Gospel Album
  2012-2020 winners only
  https://musicbrainz.org/series/fabcae7e-07e1-4a27-8f42-4cbbf492a2fa
* Best Jazz Album
  1992-2020 winners only
  https://musicbrainz.org/series/1de1ec47-b3f5-41ea-bd62-6a0eddef6dad
* Best New Age Album
  1987-2021 winners only
  https://musicbrainz.org/series/51e73fae-c35c-4a3b-8728-71c0f25934f7
* Best Pop Vocal Album
  1995-2021 nominees and winners; 2022 nominees only
  https://musicbrainz.org/series/96eef69c-02a8-4e07-8b0d-cc56a184bd1f
