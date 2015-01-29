from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from lxml import etree

from Web.services import get_sample_tweets
from Web.services import classify


def index(request):
    '''Load index page; return an HTML string.
    Keyword arguments:
    @param: request The incoming request
    '''
    return render(request, 'main.html')


def intro(request):
    '''Load intro content; return an HTML string.
    Keyword arguments:
    @param: request The incoming request
    '''
    return render(request, '1st.html')


def tweets(request):
    '''Load tweets sample; return an HTML string.
    Keyword arguments:
    @param: request The incoming request
    '''
    tweets = get_sample_tweets()
    if tweets:
        return render(request, '2nd.html', {"tweets": tweets})
    return HttpResponse("Error", status=500)


def search_and_classify(request):
    '''Load classify content; return an HTML string.
    Keyword arguments:
    @param: request The incoming request
    '''
    return render(request, "3rd.html")


def classify_by_query(request):
    '''Classify by query function.
    It handles wrong requests, returning a specific HTTP status.
    Keyword arguments:
    @param: request The incoming request
    '''

    status = None
    ren = None
    if request.method == "POST":
        try:
            if "query" in request.POST and request.POST["query"]:
                res = classify(
                    twitter_query=request.POST.get("twitter_query",None),
                    text=request.POST["query"]
                )
                ren = render_to_string("result.xml", {"results":res, "status": 200})
                status = 200
            else:
                ren = render_to_string("result.xml", {"error":"Missing parameters in query string", "status": 400})
                status = 400
        except Exception as e:
            print e
            ren = render_to_string("result.xml", {"error":"Internal server error", "status": 500})
            status = 500
        finally:
            root = etree.fromstring(ren)
            return HttpResponse(etree.tostring(root, pretty_print=True), content_type="application/xml", status=status)
    else:
        status = 405
        ren = render_to_string("result.xml", {"error":"Method not allowed", "status": status})
        return HttpResponse(etree.tostring(root, pretty_print=True), content_type="application/xml", status=status)


@csrf_exempt
def classify_by_query_rest(request):
    '''Classify by query function (API endpoint)
    To ensure a very basic access control, if no token are passed to request,
    a 403 HTTP status is returned.
    Keyword arguments:
    @param: request The incoming request
    '''
    if request.method == "POST":
        if "token" in request.POST:
            return classify_by_query(request)
        else:
            return HttpResponse("Token is missing.", status=403)
    else:
        return HttpResponse("Only POST method is allowed.", status=405)

def pnf(request):
	'''
	Handles the 404 HTTP status code, instead delegating it to Apache web server
	
	Keyword arguments:
	@param: request the incoming request
	'''
	return render(request, "404.html")

def ise(request):
	'''Handles the 500 HTTP status code, instead delegating it to Apache web server
	
	Keyword arguments:
	@param: request the incoming request
	'''
	return rendere(request,"500.html")
