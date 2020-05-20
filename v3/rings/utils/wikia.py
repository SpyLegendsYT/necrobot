import asyncio
from datetime import datetime
from .utils import BotError

API_URL = 'http://{lang}{sub_wikia}.wikia.com/api/v1/{action}'
RATE_LIMIT = False
RATE_LIMIT_MIN_WAIT = None
RATE_LIMIT_LAST_CALL = None
USER_AGENT = 'necrobot (https://github.com/ClementJ18/necrobot)'
LANG = ""

async def _wiki_request(self, params):
    '''
    Make a request to the Wikia API using the given search parameters.
    Returns a parsed dict of the JSON response.
    '''
    global RATE_LIMIT_LAST_CALL
    global USER_AGENT

    api_url = API_URL.format(**params)
    params['format'] = 'json'
    headers = {
        'User-Agent': USER_AGENT
    }

    if RATE_LIMIT and RATE_LIMIT_LAST_CALL and \
        RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT > datetime.now():

        # it hasn't been long enough since the last API call
        # so wait until we're in the clear to make the request

        wait_time = (RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT) - datetime.now()
        await asyncio.sleep(int(wait_time.total_seconds()))

    async with self.bot.session.get(api_url, params=params, headers=headers) as resp:
        r = await resp.json()

    if RATE_LIMIT:
        RATE_LIMIT_LAST_CALL = datetime.now()

    # If we got a json response, then we know the format of the input was correct
    if "exception" in r:
        details, message, error_code= r['exception'].values()
        if error_code == 408:
            raise ValueError(str(r))
        raise BotError("{}. {} ({})".format(message, details, error_code))
    return r
    
async def search(self, sub_wikia, query, results=10):
    '''
    Do a Wikia search for `query`.

    Keyword arguments:

    * sub_wikia - the sub wikia to search in (i.e: "runescape", "elderscrolls")
    * results - the maxmimum number of results returned
    '''
    search_params = {
        'action': 'Search/List?/',
        'sub_wikia': sub_wikia,
        'lang': LANG,
        'limit': results,
        'query': query
    }

    raw_results = await _wiki_request(self, search_params)

    try:
        return raw_results["items"]
    except KeyError:
        raise BotError("Could not locate page \"{}\" in subwikia \"{}\"".format(query, sub_wikia))

async def page(self, sub_wikia, page_id):
    query_params = {
        'action': 'Articles/Details?/',
        'sub_wikia': sub_wikia,
        'ids': page_id,
        'abstract': 500,
        'lang': LANG
    }

    request = await _wiki_request(self, query_params)
    result = request['items'][str(page_id)]

    return result
  
async def related(self, sub_wikia, page_id):
    query_params = {
        'action': "RelatedPages/List?/",
        'ids': page_id,
        'limit': 3,
        'sub_wikia': sub_wikia,
        'lang': LANG,
    }
      
    request = await _wiki_request(self, query_params)

    return request["items"][str(page_id)]
