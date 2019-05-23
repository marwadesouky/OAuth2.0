def showLogin():
    if request.method == 'GET':
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

    login_session['state'] = state
    return render_template('login.html', STATE=state)

    if request.method == 'POST':
        try:
            if login_session['state'] != request.args.get('state'):
                
                response = make_response(json.dumps('Invalid state parameter.'), 401)
                response.headers['Content-Type'] = 'application/json'
                print("step 1")
                return response

			# Retrieve the token sent by the client
            token = request.data
            print("step 2")

			# Request an access tocken from the google api
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
            print("step 3")
            url = (
        	'https://oauth2.googleapis.com/tokeninfo?id_token=%s'
                % token)
            h = httplib2.Http()
            result = json.loads(h.request(url, 'GET')[1])
            print("step 4")
            print(result['aud'])
			# If there was an error in the access token info, abort.
            if result.get('error') is not None:
                response = make_response(json.dumps(result.get('error')), 500)
                response.headers['Content-Type'] = 'application/json'
                return response
            print("step 5")
			# Verify that the access token is used for the intended user.
            user_google_id = idinfo['sub']
            if result['sub'] != user_google_id:
                response = make_response(
                    json.dumps("Token's user ID doesn't match given user ID."),	401)
                response.headers['Content-Type'] = 'application/json'
                return response
            print(result['sub'])
			# Verify that the access token is valid for this app.
            if result['aud'] != CLIENT_ID:
                print("step 5.5")
                response = make_response(json.dumps("Token's client ID does not match app's."), 401)
                
                print ("Token's client ID does not match app's.")
                response.headers['Content-Type'] = 'application/json'
                return response
                        
            print("step 6")
			# Check if the user is already logged in
            stored_access_token = login_session.get('access_token')
            stored_user_google_id = login_session.get('user_google_id')
            if stored_access_token is not None and user_google_id == stored_user_google_id:
                response = make_response(json.dumps('Current user is already connected.'), 200)
                response.headers['Content-Type'] = 'application/json'
                return response
            print("step 7")
			# Store the access token in the session for later use.
            login_session['access_token'] = idinfo
            login_session['user_google_id'] = user_google_id
			# Get user info
            login_session['username'] = idinfo['name']
            login_session['picture'] = idinfo['picture']
            login_session['email'] = idinfo['email']
            
            user_id = getUserID(idinfo['email'])
            
            if not user_id:
                user_id = createUser(login_session)
            
            login_session['user_id'] = user_id
            
            return 'Successful'
			
        except ValueError:
			# Invalid token
            pass
