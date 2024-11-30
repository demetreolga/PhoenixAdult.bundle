def search(results, encodedTitle, title, searchTitle, siteNum, lang, searchByDateActor, searchDate, searchAll, searchsiteID):
    searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle)
    for searchResult in searchResults.xpath('//article[@class="videolist-item"]'):
        titleNoFormatting = searchResult.xpath('.//h2[@class="videolist-caption-title"]')[0].text_content()
        curID = searchResult.xpath('.//a[@class="videolist-link ajaxable"]')[0].get('href').split('/')[-1]
        releasedDate = searchResult.xpath('.//span[@class="videolist-caption-date"]')[0].text_content()
        
        # Score calculation
        if searchByDateActor != True:
            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
        else:
            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%B %d, %y')
            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
        
        titleNoFormatting = f"{titleNoFormatting} [{PAsearchSites.searchSites[siteNum][1]}, {releasedDate}]"
        results.Append(MetadataSearchResult(id=f"{curID}|{str(siteNum)}", name=titleNoFormatting, score=score, lang=lang))
    return results

def update(metadata, siteID, movieGenres):
    temp = str(metadata.id).split("|")[0]
    url = PAsearchSites.getSearchBaseURL(siteID) + temp
    detailsPageElements = HTML.ElementFromURL(url)

    # Video Title
    metadata.title = detailsPageElements.xpath('//h1[@class="video-title"]')[0].text_content()

    # Release Date
    release_date = detailsPageElements.xpath('//span[@class="player-description-detail"]')[0].text_content()
    date_object = datetime.strptime(release_date, '%B %d, %Y')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Summary
    summary = detailsPageElements.xpath('//div[@class="summary-text"]')[0].text_content()
    metadata.summary = summary.strip()

    # Genres (manually set in template, adjust if available)
    movieGenres.clearGenres()
    movieGenres.addGenre("Hardcore")
    movieGenres.addGenre("Heterosexual")

    # Actors
    metadata.roles.clear()
    actors = detailsPageElements.xpath('//span[@class="actor-name"]')
    for actor in actors:
        role = metadata.roles.new()
        actorName = actor.text_content()
        role.name = actorName
        actorPageURL = actor.get("href")
        actorPage = HTML.ElementFromURL("https://oopsfamily.com" + actorPageURL)
        actorPhotoURL = actorPage.xpath('//img[@class="actor-photo"]')[0].get("src")
        role.photo = actorPhotoURL

    # Posters/Background Images
    posters = detailsPageElements.xpath('//img[@class="poster-img"]')
    for poster in posters:
        posterURL = poster.get("src")
        metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL).content, sort_order=1)

    background = detailsPageElements.xpath('//img[@class="background-img"]')[0].get("src")
    metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order=1)
    
    return metadata
