# Music Mining

## Dataset

Presented is a compilation of a dataset of Spotify tracks and their audio features, and assigned a category for their chart status, artist status and recording award status. The dataset is compiled from recordings nominated for a Grammy (n=~535), tracks that have entered the Chart2000 global aggregated monthly song chart (n=~3300), and a random sample (n=1000) from Spotify daily charts. The dataset is de-duplicated on track id, and limited to the years 2000-2021. The dataset is small (n=4237) but fairly balanced across the three categories.

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


### Data sources
- [Chart2000](https://chart2000.com/about.htm)
- [MusicBrainz](https://musicbrainz.org/doc/MusicBrainz_API)
- [GRAMMY Nominees - MusicBrainz](https://musicbrainz.org/series/216a2b1f-33e7-46a2-80d9-751ff7e20303)
- [Spotify Top 200 charts](https://rpubs.com/elgindykareem/top200charts)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-audio-features)

Alternative data sources:
* [MusicMoz - Record Labels](https://musicmoz.org/Record_Labels/)
* [Grammy Awards | Kaggle](https://www.kaggle.com/unanimad/grammy-awards)

Chart2000:
- Peak chart position
- Avg chart position
- Median chart position
- Number months its charted
- Total revenue

MusicBrainz:
- Grammy award nominations (category and year)
- Musical genre
- Number of releases
- Recording label and publishers

Spotify:
- Audio features

### Collection methodology
- Collection: nominated and awarded artists
    - Loop through Grammy awards and Billboard 100 lists
        - For each awarded and nominated artist:
            - For all of their release, distinct by release group:
                - Collect label and year
                - For all songs in a release:
                    - Collect EchoNest data from Spotify


### Limitations of dataset
Dataset is constructed from Grammy-nominated and top-charting songs.

### Missing features
* Music genre (from Spotify)
* Artist background: home town, home country, when they started.
* Recording labels and publishers (from MusicBrainz)
* Album type (e.g., single, EP, LP, compilation)

### Preprocessing
* Calculate variables for artists: year of first award nomination,
  first award win, latest nomination, latest win, number of awards, number of nominations.
* Aggregate artist on the year


## Analysis

Some questions we can ask:
* In the universe of charted songs, why did some songs become nominated? 
* Why were some songs awarded? What are factors for a recording to be nominated for an award?
* Why did some songs stay on to top of the charts for so long, and others not?
* What's important - musical characteristics, or the marketing and politics of the record label and publisher? 
* What are characteristics of independent artists vs major label artists?
* What characteristics of an artist's recordings change after an artist signs to a major label?
* Once an artist is signed, what happens - are they more likely to chart? Does their sound change? Do they continue to release recordings?
* What are characteristics of nominated and un-nominated artists?
* How does an artist's work change after they've been nominated?
* What features of a song are similar across the top of the charts, and the bottom of the charts?
* Can we predict whether an artist will be a one-hit-wonder or have a long career?
* How do recordings cluster - by genre, top charting, major labels?
* Are the factors involved for a song to be nominated and to be at the top of the chart the same?
* What songs are similar to nominated or charting songs? What factors separate them? (e.g., experience, label status)
* How much more likely is an artist to chart or be nominated if they've already won?

Hypotheses:
* GRAMMY awards are all politics, rather than artist or track qualities. 
* Charting is all marketing budget
* Top charting songs all sound the same
* Top charting songs lead to Grammy nominations
* An artist who has won previously or charted previously are likely to chart again.
* An artist who has been nominated previously without winning are likely to win.

## Prior work
* [Can the charts here tell us anything about long term trends](https://tsort.info/music/faq_peak_music.htm)
* [The show must go on](https://www.goldmansachs.com/insights/pages/infographics/music-in-the-air-2020/report.pdf)
* [GitHub - JLUT/Billboard_Grammy_Project1: Using Top 100 Data and Grammy Winners from the past 20 years,  analyzed datasets to determine if a Grammy winner can be determined based on the Billboard Top 100.](https://github.com/JLUT/Billboard_Grammy_Project1)
* [Spotify Top 200 charts](https://rpubs.com/elgindykareem/top200charts)

## Tasks

EDA:
* Missing values and imputing
* Multicollinearity


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
