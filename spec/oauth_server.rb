require 'spec'
require 'mechanize'
require 'json'

def server_url(path)
  "http://localhost:#{ENV['PORT']}#{path}"
end

CLIENT_ID = 'b3a8d6fbe43a3a95ac5a7bd95e0a89fcd4eb6302'
CLIENT_SECRET = 'b6448e179471d13910829b9711ad06cd83f8f650'
CLIENT_REDIRECT = 'http://localhost:8080'
OWNER_USERNAME = 'ac123'
OWNER_PASSWORD = '123'

describe 'OAuth Access Token Endpoint' do
  it "lets client obtain access token with end-user credentials" do
    page = Mechanize.new.post(server_url("/oauth/token"), {
      "grant_type"  => "password",
      "client_id"   => CLIENT_ID,
      "client_secret" => CLIENT_SECRET,
      "username" => OWNER_USERNAME,
      "password" => OWNER_PASSWORD,
    })
    response = JSON.parse(page.body)
    response.keys.should include("access_token")
  end
  
  it "lets client obtain access token with a refresh token" do
    page = Mechanize.new.post(server_url("/oauth/token"), {
      "grant_type"  => "password",
      "client_id"   => CLIENT_ID,
      "client_secret" => CLIENT_SECRET,
      "username" => OWNER_USERNAME,
      "password" => OWNER_PASSWORD,
    })
    response = JSON.parse(page.body)
    refresh_token = response['refresh_token']
    page = Mechanize.new.post(server_url("/oauth/token"), {
      "grant_type"  => "refresh_token",
      "client_id"   => CLIENT_ID,
      "client_secret" => CLIENT_SECRET,
      "refresh_token" => refresh_token,
    })
    response = JSON.parse(page.body)
    response.keys.should include("access_token")
  end
  
  it "lets client obtain access token with only client credentials" do
    page = Mechanize.new.post(server_url("/oauth/token"), {
      "grant_type"  => "client_credentials",
      "client_id"   => CLIENT_ID,
      "client_secret" => CLIENT_SECRET,
    })
    response = JSON.parse(page.body)
    response.keys.should include("access_token")
  end
end

describe 'OAuth Authorization Endpoint' do
  it "lets a client get end-user authorization" do
    page = Mechanize.new.post(server_url("/oauth/authorize"), {
      "response_type" => "code",
      "client_id"     => CLIENT_ID,
      "redirect_uri" => CLIENT_REDIRECT,
    })
    # do local app engine sdk auth
    
    
    page.body.should include(CLIENT_ID)
  end
end
