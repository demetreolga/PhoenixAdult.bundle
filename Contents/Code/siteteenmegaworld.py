import PAsearchSites
import PAgenres

def search(results, encodedTitle, title, searchTitle, siteNum, lang, searchByDateActor, searchDate, searchAll, searchsiteID):
    searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle)
    for searchResult in searchResults.xpath('//div[contains(@class, "video-item")]'):  # Adjusted for TeenMegaWorld structure
        Log(searchResult.text_content())
        
        titleNoFormatting = searchResult.xpath('.//h4[contains(@class, "video-title")]')[0].text_content().strip()
        Log("Result Title: " + titleNoFormatting)
        
        curID = searchResult.xpath('.//a')[0].get('href')  # Fetch link to video details
        curID = curID.replace('/', '_')  # Adjust ID formatting
        Log("ID: " + curID)
        
        releasedDate = searchResult.xpath('.//span[contains(@class, "video-date")]')[0].text_content().strip()
        
        lowerResultTitle = titleNoFormatting.lower()
        if searchByDateActor != True:
            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
        else:
            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%B %d, %Y')
            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
        
        titleNoFormatting += f" [TeenMegaWorld, {releasedDate}]"
        results.Append(MetadataSearchResult(id=f"{curID}|{siteNum}", name=titleNoFormatting, score=score, lang=lang))
    return results

def update(metadata, siteID, movieGenres):
    temp = str(metadata.id).split("|")[0].replace('_', '/')
    url = PAsearchSites.getSearchBaseURL(siteID) + temp
    detailsPageElements = HTML.ElementFromURL(url)

    # Summary
    metadata.studio = "TeenMegaWorld"
    paragraph = detailsPageElements.xpath('//div[contains(@class, "description")]')[0].text_content().strip()
    metadata.summary = paragraph
    metadata.title = detailsPageElements.xpath('//h1')[0].text_content().strip()
    date = detailsPageElements.xpath('//span[contains(@class, "release-date")]')[0].text_content().strip()
    date_object = datetime.strptime(date, '%B %d, %Y')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genre in detailsPageElements.xpath('//div[contains(@class, "tags")]/a'):
        movieGenres.addGenre(genre.text_content().strip())

    # Actors
    metadata.roles.clear()
    actors = detailsPageElements.xpath('//div[contains(@class, "actors")]/a')
    if len(actors) > 0:
        for actorLink in actors:
            role = metadata.roles.new()
            actorName = actorLink.text_content().strip()
            role.name = actorName
            actorPhotoURL = actorLink.get("href")  # If the actor's profile includes a photo
            role.photo = actorPhotoURL

    # Posters/Background
    posters = detailsPageElements.xpath('//div[contains(@class, "poster-gallery")]/img')
    background = detailsPageElements.xpath('//img[contains(@class, "main-poster")]')[0].get("src")
    metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order=1)
    posterNum = 1
    for posterCur in posters:
        posterURL = posterCur.get("src")
        metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order=posterNum)
        posterNum += 1
    return metadata
