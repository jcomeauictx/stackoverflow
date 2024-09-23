# Question 77252251

<https://stackoverflow.com/questions/77252251/send-requests-and-receive-answers-between-mitmproxy-and-upstream>

We can copy the flow and replay it to keep querying the server until we
get an acceptable answer. Alternatively, we could just return a FOUND (302)
status with a `Location:` header. A third way could be using
`urllib.request.urlopen`, which returns an http.client.HTTPResponse whose
contents can be `.read()`.

We can't just `kill` the unwanted flows, it will shut down the client's
(wget's) connection. Perhaps we can `intercept` them, but then we will have
to clean all those up later, and may run into other problems.

## Resources

* <https://docs.mitmproxy.org/stable/addons-examples/#duplicate-modify-replay>
