from utils import *

server = Server(pool, "/static", debug=True)
# Serve the weather data
@server.route("/",[GET,POST])
def landing(request:Request):
    current_time = fetch_current_time()
    cached_data={}
    with open(cache_filename, 'r') as cache_file:
            cached_data = json.load(cache_file)
    #if current_time - cached_data['timestamp'] <= cache_duration:
    #    return Redirect(request, f"http://{str(wifi.radio.ipv4_address)}/weather")
   # else:      
    with open("/static/form.tpl.html", "r") as file:
        html_content = file.read()
    return Response(
        request,
        html_content,
        content_type="text/html",
    )

@server.route("/weather",[GET,POST])
def weather(request: Request):   
    # Get weather data
    location=""
    if request.method == POST:
        location = request.form_data.get("location")
    weather_data={}
    current_time = fetch_current_time()
    try:
        with open(cache_filename, 'r') as cache_file:
            cached_data = json.load(cache_file)
            if current_time - cached_data['timestamp'] <= cache_duration and cached_data!=None:
                weather_data=cached_data
            else:
                weather_data=fetch_weather(location)
    except (OSError, ValueError):
        pass
    
    if weather_data is None:
        return Response(
            request,
            "Failed to retrieve weather data.",
            content_type="text/html",
        )
    src = weather_data['weather_icon_url']
    temp = weather_data['temperature']
    weather = weather_data['weather_descriptions']
    location = weather_data['location']
    # Read the HTML template and replace placeholders
    with open("/static/index.tpl.html", "r") as file:
        html_content = file.read()
    
    html_content = html_content.replace('[[SRC]]', src)
    html_content = html_content.replace('[[TEMP]]', str(temp))
    html_content = html_content.replace('[[WEATHER]]', weather)
    html_content = html_content.replace('[[LOCATION]]', location)
    
    return Response(
        request,
        html_content,
        content_type="text/html",
    )

# Start the server
server.serve_forever(str(wifi.radio.ipv4_address), 80)
