# OAuth2 on App Engine

This is an implementation of an OAuth2 (draft 10ish) authorization server with example resource server. It was written to be as concise and readable as possible, so you can better see how the spec is implemented to either implement your own or use this as a starting point for your own.

## Running it

You can run this server locally by downloading the App Engine SDK and running it with their desktop application or command line tool. Alternatively, you can deploy this on App Engine for free with a Google account. 

## Using it

Okay, you've got a working implementation of an OAuth2 server. Now what? Presumably, you're here because you're interested in providing OAuth2 for your web service. Here are your options:

 * If your app is Python, use this code to get you started with your own implementation
 * If your app is something else, use this code as a reference for your own implementation
 * If you're altruistic, use this code as reference to build an OAuth2 library for your language
 * Alternatively, you can tweak this code to BE your authorization server running on App Engine
 
## Contributing to it

We're hoping this project not only helps you learn OAuth2 for your own implementations, but eventually we'd like to make it a library for Python. This requires a number of complications and abstractions that will make reading it for reference a bit more difficult. So the plan is to approach this slowly and intelligently with the least number of abstractions that do the job. Hopefully, this library will then also be a reference for libraries in other languages. This implementation itself is loosely based on an older Ruby OAuth2 server implementation/library (http://github.com/ThoughtWorksStudios/oauth2_provider).

HOWEVER, for the time being, the primary goal of this project is to provide a full implementation of the latest OAuth2 spec, which is currently at draft 10, with about 3 more planned before it becomes finalized in early 2011. 

That said, we welcome contributors to keep it up to date and add examples of all the base OAuth2 functionality. Feel free to submit issues or fork and send pull requests. Just be sure to add integration tests (which are currently still a work in progress).

## Contributors

 * Jeff Lindsay <progrium@gmail.com>

## License

MIT