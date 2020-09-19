import asyncio
from datetime import datetime
from .utils import BotError

API_URL = 'http://tolkiengateway.net/w/api.php'
RATE_LIMIT = False
RATE_LIMIT_MIN_WAIT = None
RATE_LIMIT_LAST_CALL = None
USER_AGENT = 'necrobot (https://github.com/ClementJ18/necrobot)'
LANG = ""

def _check_error_response(response, query):
    """ check for default error messages and throw correct exception """
    if "error" in response:
        http_error = ["HTTP request timed out.", "Pool queue is full"]
        geo_error = [
            "Page coordinates unknown.",
            "One of the parameters gscoord, gspage, gsbbox is required",
            "Invalid coordinate provided",
        ]
        err = response["error"]["info"]
        
        if err in http_error:
            raise ValueError(query)
        if err in geo_error:
            raise ValueError(err)
        raise ValueError(err)

async def _wiki_request(self, params):
    '''
    Make a request to the Wikia API using the given search parameters.
    Returns a parsed dict of the JSON response.
    '''
    global RATE_LIMIT_LAST_CALL
    global USER_AGENT

    api_url = API_URL
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
        
    return r

async def search(self, query):
    search_params = {
        "action": "query",
        "generator": "search",
        "prop": "info",
        "gsrsearch": query,
    }
        
    raw_results = await _wiki_request(self, search_params)

    _check_error_response(raw_results, query)

    return list(raw_results["query"]["pages"].values())
    
async def page(self, page_id):
    query_params = {
        "action": "query",
        "prop": "info|pageprops",
        "inprop": "url",
        "ppprop": "disambiguation",
        "redirects": "",
        "pageids": page_id
    }
    
    request = await _wiki_request(self, query_params)
    print(request)
    result = request['items'][str(page_id)]
    
    return result
    
async def related(self, page_id):
    pass
    
async def suggest(self, title):
    pass
